# Software Requirements Specification
## Tournament Management System (TMS)

**Status:** Baselined. Changes tracked in `docs/change-log.md`.
**Last updated:** 2026-08-23 (incorporates CR-001)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements for the
Tournament Management System (TMS), a web-based application for creating, configuring,
managing, and viewing tournaments across both team-based and individual sports.

### 1.2 Scope
TMS supports two participation types (`TEAM`, `INDIVIDUAL`) and two tournament formats
(`ROUND_ROBIN`, `KNOCKOUT`) as independent dimensions, without sport-specific branching
in fixture generation or scoring logic. The same domain model supports football,
cricket, chess, badminton, or any comparable competition.

### 1.3 Out of Scope
- Swiss-system tournaments
- Double round-robin
- Double elimination
- Third-place matches
- Advanced sport-specific scoring (e.g. football penalty shootouts, chess-specific
  tiebreak systems)
- Live scoring, notifications, chat, payments, AI features, mobile application

These may be documented as future enhancements but are not implemented in this version.

---

## 2. Actors

### 2.1 Guest *(added by CR-001)*
An unauthenticated visitor. Can, without logging in or registering:
- view the list of tournaments and tournament details
- view registered participants
- view fixtures/matches
- view match results
- view standings

Cannot perform any write action — cannot create a tournament, register as a
participant, submit results, or perform any organizer function.

### 2.2 Player
Everything a Guest can do, plus, once registered and logged in:
- register as a tournament participant (individually or as part of a team)
- view their own profile (`GET /auth/me`)

### 2.3 Organizer
Everything a Guest can do, plus, once registered and logged in:
- create tournaments
- configure tournaments (subject to lifecycle rules, §6)
- open/close registration
- manage participants
- generate fixtures
- submit match results
- manage knockout progression

Organizer-only operations are enforced via role-based authorization on top of JWT
authentication, not authentication alone.

---

## 3. Participation Model

```
ParticipationType
    TEAM
    INDIVIDUAL
```

**TEAM** — a team participates as a unit (e.g. football: Team A vs Team B). Players may
optionally belong to a team.

**INDIVIDUAL** — an individual player participates directly (e.g. chess: Player A vs
Player B). No team is involved.

`participation_type` and `format` (§4) are independent, orthogonal fields on a
Tournament — never inferred from `sport`.

---

## 4. Tournament Format

```
TournamentFormat
    ROUND_ROBIN
    KNOCKOUT
```

The fixture service selects generation logic based on `format`, never on `sport`
(§10.6, Sport Independence).

---

## 5. Core Domain Model

```
User
  ├── Player (0..1)
  └── Organizer role

Team
  └── Player (0..N)

Tournament
  ├── organizer_id → User
  ├── TournamentParticipant (0..N)
  │     └── Participant (exactly one Player OR one Team)
  ├── Match (0..N)
  │     ├── venue_id → Venue
  │     ├── MatchParticipant (exactly 2)
  │     │     └── Participant
  │     │           └── MatchScore
  │     └── MatchResult
  │           └── winner_participant_id → Participant (nullable)
  └── Standing (0..N)
        └── Participant
```

The **Participant** entity is the central generic abstraction: it represents whoever
actually competes, and is exactly one Player or exactly one Team, never both, never
neither. This allows Match, MatchResult, MatchScore, and Standing to all reference
`Participant` generically, so the same schema supports both team sports and individual
sports without duplication.

---

## 6. Tournament Lifecycle

```
DRAFT → REGISTRATION_OPEN → ONGOING → COMPLETED
```

| Current State | Allowed Next State |
|---|---|
| DRAFT | REGISTRATION_OPEN |
| REGISTRATION_OPEN | ONGOING |
| ONGOING | COMPLETED |
| COMPLETED | *(none — terminal)* |

No skipping (e.g. `DRAFT → ONGOING` is invalid) and no reverse transitions (e.g.
`ONGOING → DRAFT` is invalid). The service layer rejects any transition not in this
table.

**DRAFT** — organizer configures the tournament; participants cannot register yet.
**REGISTRATION_OPEN** — eligible teams or players can register.
**ONGOING** — registration is closed; fixtures are generated; matches can be played and
results submitted. Entered via an explicit organizer action
(`POST /tournaments/{id}/start`).
**COMPLETED** — all required matches are finished. The tournament becomes read-only.
Entered either via explicit organizer action (future) or automatically once the final
knockout match or last round-robin match concludes (§11).

### 6.1 Configuration Locking
Before `REGISTRATION_OPEN`: organizer may freely edit `name`, `description`, `sport`,
`participant_type`, `format`, `start_date`, `end_date`, venue associations (via Match).

Once `REGISTRATION_OPEN` or later: `participant_type` and `format` are locked and
cannot be changed. Attempting to do so returns `409 Conflict`.

Once `ONGOING`: participants cannot be added through normal operations; fixtures cannot
be arbitrarily changed; completed matches cannot be modified through normal operations.

Once `COMPLETED`: the tournament is fully read-only.

---

## 7. Data Model

### 7.1 User
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| name | String | NOT NULL |
| email | String | UNIQUE, NOT NULL |
| password_hash | String | NOT NULL |
| role | Enum(ORGANIZER, PLAYER) | NOT NULL |
| created_at | DateTime | NOT NULL |

Passwords are never stored as plaintext.

### 7.2 Player
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| name | String | NOT NULL |
| email | String | UNIQUE, nullable |
| user_id | Integer | FK → User.id, nullable, UNIQUE |
| team_id | Integer | FK → Team.id, nullable |

`team_id` is nullable — a chess player needs no team. `user_id` is nullable — a
participant does not strictly need a separate login account to be registered, though a
Player who logs in must be linked to a User.

### 7.3 Team
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| name | String | UNIQUE, NOT NULL |
| created_at | DateTime | NOT NULL |

### 7.4 Tournament
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| name | String | NOT NULL |
| description | Text | nullable |
| sport | String | NOT NULL |
| format | Enum(ROUND_ROBIN, KNOCKOUT) | NOT NULL |
| participant_type | Enum(TEAM, INDIVIDUAL) | NOT NULL |
| status | Enum(DRAFT, REGISTRATION_OPEN, ONGOING, COMPLETED) | NOT NULL |
| start_date | Date | nullable |
| end_date | Date | nullable |
| organizer_id | Integer | FK → User.id |
| created_at | DateTime | NOT NULL |

No `venue_id` on Tournament — venue is associated per-Match, not per-Tournament, since
a tournament may use multiple venues across its matches.

### 7.5 Participant
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| type | Enum(TEAM, INDIVIDUAL) | NOT NULL |
| player_id | Integer | FK → Player.id, nullable |
| team_id | Integer | FK → Team.id, nullable |

**Invariant:** `type = INDIVIDUAL` requires `player_id IS NOT NULL AND team_id IS NULL`.
`type = TEAM` requires `team_id IS NOT NULL AND player_id IS NULL`. Enforced at the
service layer, and via database CHECK constraint where practical.

### 7.6 TournamentParticipant
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| tournament_id | Integer | FK → Tournament.id |
| participant_id | Integer | FK → Participant.id |
| registered_at | DateTime | NOT NULL |

`UNIQUE(tournament_id, participant_id)` — prevents duplicate registration.

Registration is only permitted while `Tournament.status = REGISTRATION_OPEN`, and only
for the Participant `type` matching `Tournament.participant_type`.

### 7.7 Venue
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| name | String | UNIQUE, NOT NULL |
| location | String | NOT NULL |
| capacity | Integer | nullable, CHECK ≥ 0 |

There is no concept of home/away venue.

### 7.8 Match
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| tournament_id | Integer | FK → Tournament.id |
| round | String/Integer | NOT NULL |
| venue_id | Integer | FK → Venue.id, nullable |
| scheduled_at | DateTime | nullable |
| status | Enum(SCHEDULED, COMPLETED) | NOT NULL |

No `home_team_id`/`away_team_id` and no `participant_a_id`/`participant_b_id` columns.
Participants attach via MatchParticipant (§7.9).

### 7.9 MatchParticipant
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| match_id | Integer | FK → Match.id |
| participant_id | Integer | FK → Participant.id |

`UNIQUE(match_id, participant_id)`. Every match has exactly two MatchParticipant rows.
Both participants must belong to the same tournament as the match, must match the
tournament's `participant_type`, and must be different from each other.

### 7.10 MatchResult
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| match_id | Integer | FK → Match.id, UNIQUE |
| winner_participant_id | Integer | FK → Participant.id, nullable |
| result_type | Enum(WIN, DRAW) | NOT NULL |
| submitted_at | DateTime | NOT NULL |

`result_type = WIN` requires `winner_participant_id IS NOT NULL`.
`result_type = DRAW` requires `winner_participant_id IS NULL`.
`winner_participant_id`, when set, must be one of the match's two participants.
One result per match (`UNIQUE(match_id)`); a completed match cannot receive another
result through normal operations.

### 7.11 MatchScore
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| match_participant_id | Integer | FK → MatchParticipant.id, UNIQUE |
| score | Decimal/Integer | NOT NULL |

References MatchParticipant rather than Match+Participant directly, which makes it
structurally impossible to record a score for a participant who isn't actually in that
match.

### 7.12 Standing
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| tournament_id | Integer | FK → Tournament.id |
| participant_id | Integer | FK → Participant.id |
| played | Integer | NOT NULL, ≥ 0 |
| won | Integer | NOT NULL, ≥ 0 |
| drawn | Integer | NOT NULL, ≥ 0 |
| lost | Integer | NOT NULL, ≥ 0 |
| points | Integer | NOT NULL, ≥ 0 |
| score_difference | Decimal/Integer | nullable |

`UNIQUE(tournament_id, participant_id)`. `played = won + drawn + lost`. References
Participant, not Team — so the same table supports both team standings (football) and
individual standings (chess).

---

## 8. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Users can register and log in; passwords are securely hashed; sessions use JWT. |
| FR-02 | Organizers can create and configure tournaments; tournament lifecycle transitions follow the state machine in §6. |
| CR-001 | Guests (unauthenticated) can view tournaments, participants, fixtures, results, and standings without logging in. |
| FR-03 | Organizers can register participants (teams or individuals, matching the tournament's participant type) while registration is open. |
| FR-04 | The system generates round-robin or knockout fixtures based on the tournament's format, including bye handling for non-power-of-two knockout brackets and odd-count round-robins. |
| FR-05 | Organizers submit match results transactionally; a valid result updates the match status, records scores, and updates standings/progression atomically. |
| FR-06 | The system computes and displays standings for round-robin tournaments, ordered deterministically. |
| FR-07 | The system manages knockout progression: match winners advance automatically to the next round; the final's winner is the champion. |

---

## 9. Match Results — Draws and Winners

For round-robin tournaments, equal scores produce a draw (`result_type = DRAW`,
`winner_participant_id = NULL`). For knockout tournaments, a completed match must
produce a winner — the initial implementation requires a sport-neutral tie-break
mechanism to be supplied when scores are equal, without implementing sport-specific
rules (e.g. football penalties, chess tiebreak systems) unless explicitly scoped in
later.

**Result submission is organizer-only.** Players do not submit their own match results
under any configuration (confirmed as part of CR-001 discussion — no player-submission
path exists or is planned).

---

## 10. Fixture Generation Rules

### 10.1 Round-Robin
For N participants, every participant plays every other participant once:
`N(N-1)/2` matches for even N. For odd N, one participant receives a bye each required
round. No self-pairing, no duplicate pairing.

### 10.2 Round-Robin Standings Rules
Points: Win = 3, Draw = 1, Loss = 0.
`score_difference = total score for − total score against`.

### 10.3 Standings Ordering
1. Points, descending
2. Score difference, descending
3. Total score, descending
4. Participant name, ascending

### 10.4 Knockout — Bracket Sizing
Bracket size is the smallest power of two ≥ participant count (e.g. 7 participants →
8-slot bracket with 1 bye; 5 participants → 8-slot bracket with 3 byes). Byes are
assigned via deterministic bracket ordering; advanced seeding is out of scope.

### 10.5 Knockout — Progression
A match winner advances automatically to the corresponding slot in the next round.
Knockout tournaments do not use league standings as their primary progression
mechanism. The final's winner is the champion; no third-place match is generated.

### 10.6 Sport Independence
The fixture service branches on `participant_type` and `format` only — never on
`sport`. `sport` is descriptive metadata.

---

## 11. Match Result Transaction

Result submission is transactional:

```
Validate Match → Validate Scores → Create MatchResult → Create MatchScore rows →
Update Match.status = COMPLETED → Update Standings / Progression → COMMIT
```

Any failure triggers a full ROLLBACK, preventing a saved result with stale standings.

When a knockout final concludes, or the last scheduled round-robin match completes, the
tournament automatically transitions to `COMPLETED` via the same lifecycle rules
defined in §6 (this is a system-triggered transition, distinct from the
organizer-triggered `REGISTRATION_OPEN`/`ONGOING` transitions).

---

## 12. API Summary

Base path: `/api/v1`. Full endpoint list and auth requirements are in `README.md`
(kept there rather than duplicated, since it must stay in sync with the actual routes).
The governing rule, per CR-001: **all `GET` endpoints are public; all `POST`/`PUT`
endpoints require authentication and, in almost all cases, the ORGANIZER role.**

### Standard error responses
| Code | Meaning |
|---|---|
| 400 | Bad Request — invalid input, invalid lifecycle transition |
| 401 | Unauthorized — missing/invalid JWT |
| 403 | Forbidden — authenticated but wrong role, or not the owning organizer |
| 404 | Not Found |
| 409 | Conflict — duplicate registration, duplicate result, invalid state transition |
| 500 | Internal Server Error |

Response body on error:
```json
{ "error": "Team is already registered in this tournament" }
```

---

## 13. Non-Functional Requirements

- **Security:** passwords hashed, never plaintext; JWT secret from environment
  variables; `.env` never committed; database credentials never hardcoded; all
  organizer-only routes protected by role-based authorization, not authentication alone.
- **Data Integrity:** all multi-step writes (e.g. result submission) are transactional
  with rollback on failure. Uniqueness constraints enforced at the database level
  (`UNIQUE(tournament_id, participant_id)`, `UNIQUE(match_id)`, etc.) in addition to
  service-level validation.
- **Extensibility:** sport-agnostic domain model — adding a new sport requires no
  changes to fixture, scoring, or progression logic, only new `sport` metadata values.

---

## 14. Architecture

```
React Frontend → REST API → Routes/Controllers → Services → SQLAlchemy Models → PostgreSQL
```

Business logic resides in the service layer, not directly in route functions. Routes
handle HTTP concerns, authentication, authorization, and request validation, then
delegate to services for tournament rules, lifecycle, participant registration, fixture
generation, result processing, standings, and knockout progression.

---

## 15. Change History

See `docs/change-log.md` for the full record. Summary:

| CR | Summary | Status |
|---|---|---|
| CR-001 | Added Guest actor with public read access to all tournament data | Approved, implemented |
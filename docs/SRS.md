# Software Requirements Specification
## Tournament Management System (TMS)

**Status:** Baselined. Changes tracked in `docs/change-log.md`.
**Last updated:** 2026-08-26 (incorporates CR-001, CR-002, CR-003)

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements for the
Tournament Management System (TMS), a web-based application for creating, configuring,
managing, and viewing tournaments across both team-based and individual sports.

### 1.2 Scope
TMS supports two participation types (`TEAM`, `INDIVIDUAL`) and two tournament formats
(`ROUND_ROBIN`, `KNOCKOUT`) as independent dimensions, without sport-specific branching
in fixture generation or scoring logic. `sport` is a free-text descriptive field on
Tournament with no fixed list — the backend places no restriction on its value.

### 1.3 Out of Scope
- Swiss-system tournaments, double round-robin, double elimination, third-place matches
- Advanced sport-specific scoring (e.g. football penalty shootouts)
- Live scoring, notifications, chat, payments, AI features, mobile application
- Account lockout after failed logins (rate limiting provides baseline brute-force
  protection instead — see §13)
- Real SMTP email delivery (development-mode token exposure used instead — see §9.3, §9.4)
- Pagination on tournament-scoped lists (participants, matches, standings) — naturally
  bounded by tournament size

These may be documented as future enhancements but are not implemented in this version.

---

## 2. Actors

### 2.1 Guest *(CR-001)*
An unauthenticated visitor. Can, without logging in or registering:
- view the list of tournaments and tournament details
- view registered participants, teams, and players
- view fixtures/matches
- view match results
- view standings

Cannot perform any write action.

### 2.2 Player *(registration flow updated by CR-002)*
Everything a Guest can do, plus, once registered and logged in:
- register their own `Player` profile as part of account registration (see §7.1)
- update their own team affiliation (`PUT /players/{id}/team`)
- view their own profile (`GET /auth/me`)
- log out (revokes their current session token — see §9.2)
- request a password reset if forgotten

### 2.3 Organizer
Everything a Guest can do, plus, once registered and logged in:
- create tournaments; configure tournaments (subject to lifecycle rules, §6)
- open/close registration
- register participants; remove a participant before the tournament starts
- generate fixtures
- submit match results
- manage knockout progression
- update any player's team affiliation

**Organizers cannot create `Player` or `Team` records** — that only happens through
Player self-registration (§7.1). This is enforced at the schema-validation level;
including player/team fields on an Organizer registration returns `400`.

Organizer-only operations are enforced via role-based authorization (`require_role`)
on top of JWT authentication, and — for tournament-scoped write actions — an
additional ownership check confirming the authenticated organizer is the one who
created that specific tournament (see §6.2).

---

## 3. Participation Model

```
ParticipationType
    TEAM
    INDIVIDUAL
```

**TEAM** — a team participates as a unit. Players may optionally belong to a team.
**INDIVIDUAL** — an individual player participates directly. No team is involved.

`participation_type` and `format` (§4) are independent, orthogonal fields on a
Tournament — never inferred from `sport`.

---

## 4. Tournament Format

```
TournamentFormat
    ROUND_ROBIN
    KNOCKOUT
```

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

User
  ├── PasswordResetToken (0..N)
  └── EmailVerificationToken (0..N)
```

The **Participant** entity is the central generic abstraction: it represents whoever
actually competes, and is exactly one Player or exactly one Team, never both, never
neither. This allows Match, MatchResult, MatchScore, and Standing to all reference
`Participant` generically.

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

No skipping and no reverse transitions. The service layer rejects any transition not in
this table.

**DRAFT** → **REGISTRATION_OPEN** → **ONGOING**: entered via explicit organizer action.
**COMPLETED**: entered automatically once the final knockout match or the last
scheduled round-robin match's result is submitted (§11).

### 6.1 Configuration Locking
Before `REGISTRATION_OPEN`: organizer may freely edit `name`, `description`, `sport`,
`participant_type`, `format`, `start_date`, `end_date`.

Once `REGISTRATION_OPEN` or later: `participant_type` and `format` are locked
(`409 Conflict` if changed).

Once `ONGOING`: participants cannot be added through normal operations (only removable
before `ONGOING` — see §7.3); fixtures cannot be arbitrarily changed; completed matches
cannot be modified through normal operations.

Once `COMPLETED`: the tournament is fully read-only.

### 6.2 Ownership Enforcement

Every write operation scoped to a specific tournament — participant registration,
participant removal, fixture generation, result submission, and all lifecycle/CRUD
operations on the Tournament itself — verifies that the authenticated organizer is the
**same organizer who created that tournament** (`tournament.organizer_id == authenticated_user_id`).
An organizer authenticated with a valid ORGANIZER-role token cannot manage a tournament
they do not own; such attempts return `403 Forbidden`.

---

## 7. Registration & Account Model *(CR-002)*

### 7.1 Player Self-Registration

`POST /auth/register` with `role=PLAYER` requires additional fields:

```
participation_type: INDIVIDUAL | TEAM   (required)

If participation_type = TEAM:
  team_option: NEW | EXISTING            (required)
  If team_option = NEW:
    team_name: string                    (required)
  If team_option = EXISTING:
    team_id: integer                     (required)
```

On success, a `Player` row is created automatically, linked to the new `User` via
`user_id`. If `participation_type = TEAM`, the `Player` is also linked to the
specified team — either a newly created `Team` (rejecting duplicate names with `409`)
or an existing one (rejecting an invalid ID with `404`).

A `Player` can later change or remove their team affiliation via
`PUT /players/{id}/team` (self-service, or by an Organizer on any player's behalf —
see §7.4).

### 7.2 Organizer Registration

`POST /auth/register` with `role=ORGANIZER` accepts only `name`, `email`, `password`,
`role`. Including any of `participation_type`, `team_option`, `team_name`, `team_id`
is rejected with `400` — organizers never create Player or Team records.

### 7.3 Participant Removal

`DELETE /tournaments/{id}/participants/{participant_id}` — organizer-only (owning
organizer), permitted only while the tournament is `DRAFT` or `REGISTRATION_OPEN`.
Returns `409` if attempted once the tournament is `ONGOING` or `COMPLETED`.

### 7.4 Player-Team Update

`PUT /players/{id}/team` — either the Player themself (verified via their own
`user_id`) or any Organizer may reassign a player's `team_id`, including setting it
to `null` to remove them from a team entirely. A Player attempting to update another
player's team affiliation receives `403`.

---

## 8. Data Model

*(Unchanged from the frozen database design — see the Frozen DB Design document for
full column-level detail on Player, Team, Tournament, Participant,
TournamentParticipant, Venue, Match, MatchParticipant, MatchResult, MatchScore, and
Standing. One column was added under CR-003, shown below.)*

### 8.1 User
| Column | Type | Constraint |
|---|---|---|
| id | Integer | PK |
| name | String | NOT NULL |
| email | String | UNIQUE, NOT NULL |
| password_hash | String | NOT NULL |
| role | Enum(ORGANIZER, PLAYER) | NOT NULL |
| is_verified | Boolean | NOT NULL, default False *(CR-003)* |
| created_at | DateTime | NOT NULL |

---

## 9. Authentication & Account Management *(CR-003)*

### 9.1 Passwords
Hashed via `werkzeug.security`, never stored or compared as plaintext.

### 9.2 Logout / Token Revocation

`POST /auth/logout` (requires valid JWT) — records the token's `jti` (JWT ID) and its
original `exp` (expiry) in a `TokenBlocklist` table. Subsequent requests presenting a
blocklisted token are rejected as unauthenticated, even though the token has not
naturally expired yet. Blocklist entries store `expires_at` so that entries for
tokens which have since expired naturally can be safely purged (not currently
scheduled automatically — see §13 non-functional notes).

### 9.3 Password Reset

```
POST /auth/forgot-password  { email }
  -> generates a PasswordResetToken (30-minute TTL)
  -> invalidates any previously issued, still-unused tokens for that user
  -> in development mode only, returns the raw token in the response body
     (dev_token field) since no SMTP provider is configured; production
     would email it instead and never expose it via the API

POST /auth/reset-password  { token, new_password }
  -> validates token is unused and unexpired
  -> updates password_hash
  -> marks token used
```

### 9.4 Email Verification

`User.is_verified` (boolean, default `false`) is set via:

```
GET /auth/verify-email?token=...
```

An `EmailVerificationToken` (48-hour TTL) is generated automatically at registration
time. In development mode, the token is returned in the registration response
(`dev_verification_token`) for the same reason as §9.3. **Verification is tracked but
not enforced** — an unverified user can still log in and use the system normally. This
is a deliberate scope decision for the current version; enforcing verified-only login
is a documented possible future enhancement.

### 9.5 Rate Limiting

| Endpoint | Limit |
|---|---|
| `POST /auth/login` | 5 per minute per IP |
| `POST /auth/register` | 20 per minute per IP |

Disabled automatically in the test configuration to avoid interference with the
automated test suite. Uses in-memory storage (see §13 non-functional notes).

---

## 10. Match Results — Draws and Winners

For round-robin tournaments, equal scores produce a draw (`result_type = DRAW`,
`winner_participant_id = NULL`). For knockout tournaments, a completed match must
produce a winner.

**Result submission is organizer-only**, with the owning-organizer check from §6.2
applied. Players do not submit their own match results under any configuration.

---

## 11. Fixture Generation & Match Result Transaction

### 11.1 Round-Robin
For N participants: `N(N-1)/2` matches for even N; odd N gets a bye per round via the
circle method. No self-pairing, no duplicate pairing.

### 11.2 Round-Robin Standings
Win = 3 points, Draw = 1, Loss = 0. `score_difference = total for - total against`.
Ordering: points desc, then score difference desc, then total score desc, then name
asc. Every registered participant appears in standings with zero values from the
moment fixtures exist, not only once they've played their first match.

### 11.3 Knockout — Bracket Sizing & Byes
Bracket size = smallest power of two >= participant count. Byes assigned to the first
N registered participants deterministically; a bye is represented as an immediately
`COMPLETED` single-participant match with a `MatchResult` already recorded, so
downstream progression logic treats byes and real wins identically.

### 11.4 Knockout — Progression
A match winner advances automatically to the next round's corresponding slot. Final's
winner = champion; no third-place match.

### 11.5 Transaction & Automatic Completion

```
Validate Match -> Validate Scores -> Create MatchResult -> Create MatchScore rows ->
Update Match.status = COMPLETED -> Update Standings / Progression -> COMMIT
```

Any failure triggers full ROLLBACK. When a knockout final concludes, or the last
scheduled round-robin match completes, the tournament automatically transitions to
`COMPLETED` — a system-triggered transition, not requiring explicit organizer action.

### 11.6 Sport Independence
Fixture generation branches on `participant_type` and `format` only, never on `sport`.

---

## 12. API Summary

Base path: `/api/v1`. Governing rule (CR-001): **all `GET` endpoints are public; all
`POST`/`PUT`/`DELETE` endpoints require authentication**, almost always requiring the
ORGANIZER role plus tournament ownership where applicable (§6.2). Full endpoint list
maintained in `README.md`.

**Pagination** (CR-003): `GET /tournaments`, `GET /players`, `GET /teams` return
`{"items": [...], "page", "per_page", "total", "total_pages"}` rather than a bare
array. All other list endpoints are unpaginated.

### Standard error responses
| Code | Meaning |
|---|---|
| 400 | Bad Request - invalid input, invalid lifecycle transition |
| 401 | Unauthorized - missing/invalid/revoked JWT |
| 403 | Forbidden - wrong role, or not the owning organizer |
| 404 | Not Found |
| 409 | Conflict - duplicate registration, duplicate result, invalid state transition |
| 429 | Too Many Requests - rate limit exceeded (§9.5) |
| 500 | Internal Server Error |

Response body: `{ "error": "<message>" }`

---

## 13. Non-Functional Requirements

- **Security:** passwords hashed; JWT secret from environment variables with no
  fallback default; `.env` never committed; CORS restricted to an explicit origin
  allowlist (`CORS_ORIGINS` env var) rather than wide open; all organizer-only routes
  protected by role-based authorization plus, where applicable, ownership verification.
- **Data Integrity:** multi-step writes are transactional with rollback on failure.
  Uniqueness enforced at the database level in addition to service-level validation.
  Explicit indexes declared on all foreign-key columns.
- **Extensibility:** sport-agnostic domain model.
- **Known limitations (documented, not defects):**
  - Rate limiting uses in-memory storage — resets on server restart and would not
    function correctly across multiple server processes. Acceptable for this
    project's single-process deployment scope; a production deployment would use a
    shared store (e.g. Redis).
  - Token blocklist entries are not automatically purged on a schedule; a
    `TokenBlocklist.purge_expired()` utility exists but must be invoked manually or
    via a future maintenance job.
  - Email verification and password reset tokens are exposed directly in API
    responses in development mode only, since no SMTP provider is configured. This
    must never be enabled in a production deployment.

---

## 14. Architecture

```
React Frontend -> REST API -> Routes/Controllers -> Services -> SQLAlchemy Models -> PostgreSQL
```

Business logic resides in the service layer, not in route functions.

---

## 15. Testing Summary

- **94 automated tests** (pytest), covering models, services, and routes across every
  functional requirement, change request, and hardening fix.
- **2 manual end-to-end integration scenarios** run against the live API (documented in
  `backend/scripts/scenario_a.ps1`, `scenario_b.ps1`): a full round-robin lifecycle and
  a full knockout lifecycle including byes, verifying behavior no unit test can, since
  it exercises the complete chain of real HTTP requests, real database state, and
  real timing (e.g., automatic tournament completion) together.
- Integration testing surfaced three defects invisible to unit testing (a missing FK
  cascade, an overly strict rate limit, and a broken migration downgrade) — see
  `docs/change-log.md` CR-003 addendum and `docs/traceability.md` for details.

---

## 16. Change History

See `docs/change-log.md` for full detail.

| CR | Summary | Status |
|---|---|---|
| CR-001 | Guest actor with public read access | Approved, implemented |
| CR-002 | Player self-registration with team creation/joining | Approved, implemented |
| CR-003 | Auth hardening (logout, password reset, email verification), pagination, rate limiting | Approved, implemented |
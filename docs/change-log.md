# Change Log

This log records requirement changes made after the initial baseline (per SRS §5's
change-management process: Requirement Change → Change Record → SRS Update → Affected
Design Artifacts → Implementation → Tests). Every entry here should have a corresponding
update in `docs/SRS.md`.

---

## CR-001 — Public read access for guests (unauthenticated visitors)

**Date raised:** 2026-08-23
**Raised during:** Backend Phase 3 (Tournament CRUD implementation)
**Requested by:** Team decision (both members)

### Original requirement
The initial SRS (§6) defined only two actors: **Organizer** and **Player**. All
functionality, including viewing tournaments, fixtures, results, and standings, was
implicitly assumed to require an authenticated session under one of these two roles.

### New requirement
A third actor, **Guest**, is introduced. A Guest is any unauthenticated visitor. Guests
can view all read-only tournament data without creating an account or logging in:
- tournaments (list and detail)
- participants
- fixtures / matches
- match results
- standings

Guests cannot perform any write action: they cannot create tournaments, register as a
participant, submit results, or perform any organizer function. To do any of these, a
visitor must register and log in as either a Player or an Organizer.

### Reason
Improves accessibility and matches how most real-world tournament platforms behave —
browsing should not require an account; only participation or organization should.

### Affected SRS sections
- §6 (Actors) — new "Guest" actor added
- §37 (API) — clarifies that all `GET` endpoints are public; only `POST`/`PUT` endpoints
  require authentication and role authorization

### Affected design/implementation
- All `GET` routes across every blueprint (`tournament_routes.py`, `venue_routes.py`, and
  Teammate B's `participant_routes.py`, `match_routes.py`, `standings_routes.py`) carry
  **no** `@jwt_required()` or `@require_role()` decorator.
- All `POST`/`PUT` routes remain protected with `@require_role("ORGANIZER")` (or, where
  applicable in future, `@require_role("ORGANIZER", "PLAYER")`).
- Confirmed as part of this change: match result submission is **organizer-only** with no
  player-submission path, consistent with the original SRS §6 listing of "submit match
  results" solely under Organizer.

### Status
**Approved and implemented.** Landed starting with Backend Phase 3 (Tournament and Venue
routes). Applies retroactively as a design rule to all subsequent routes built by either
teammate.

### Verification
Covered by guest-access test cases in `test_tournaments.py` (e.g.
`test_guest_can_view_tournaments_without_login`,
`test_guest_can_view_single_tournament`) and equivalent tests required in Teammate B's
`test_participants.py`, `test_fixtures.py`, `test_results.py`, and `test_standings.py`.

---

*Add new entries above this line, in reverse chronological order (newest at top), as
future changes arise.*
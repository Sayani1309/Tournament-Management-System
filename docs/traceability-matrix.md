# Traceability Matrix

This matrix links each functional requirement to its design artifact, implementation
file, and test file, per SRS §43. It is updated as each feature is completed — not
filled in retroactively at the end of the project.

**Status legend:** ✅ Done · 🟡 In progress · ⬜ Not started

---

| ID | Requirement | Design Artifact | Implementation | Test | Status |
|---|---|---|---|---|---|
| FR-01 | User registration & login | Auth sequence diagram (pending, §44) | `app/services/auth_service.py`, `app/routes/auth_routes.py`, `app/schemas/auth_schema.py` | `tests/test_auth.py` | ✅ |
| FR-02 | Create & configure tournament | Use-case diagram (pending, §44) | `app/services/tournament_service.py`, `app/routes/tournament_routes.py`, `app/schemas/tournament_schema.py` | `tests/test_tournaments.py` | ✅ |
| FR-02a | Tournament lifecycle transitions (DRAFT→REGISTRATION_OPEN→ONGOING→COMPLETED) | Activity diagram: tournament lifecycle (pending, §44) | `advance_lifecycle()` in `tournament_service.py` | `tests/test_tournaments.py` (lifecycle tests) | ✅ |
| FR-02b | Config locking after DRAFT (participant_type, format immutable) | — | `update_tournament()` in `tournament_service.py` | `tests/test_tournaments.py::test_cannot_change_format_after_leaving_draft` | ✅ |
| — | Venue management | — | `app/models/venue.py`, `app/routes/venue_routes.py` | `tests/test_venues.py` | ✅ |
| CR-001 | Guest (unauthenticated) read access to all tournament data | — (see `docs/change-log.md`) | Route-level: no auth decorator on any `GET` route across all blueprints (tournaments, venues, participants, matches, results, standings) | Guest-access tests in `test_tournaments.py`, `test_venues.py`, `test_participants.py`, `test_fixtures.py`, `test_results.py`, `test_standings.py` | ✅ |
| FR-03 | Register participant (team or individual) | ER diagram (pending, §44) | `app/services/participant_service.py`, `app/routes/participant_routes.py` | `tests/test_participants.py` | ✅ |
| FR-04 | Generate fixtures (round-robin & knockout, incl. byes) | Sequence diagram: fixture generation (pending, §44) | `app/services/fixture_service.py`, `app/routes/match_routes.py` (fixtures half) | `tests/test_fixtures.py` | ✅ |
| FR-05 | Submit match result (organizer-only, transactional) | Sequence diagram: result → standings (pending, §44) | `app/services/result_service.py`, `app/routes/match_routes.py` (results half) | `tests/test_results.py` | ✅ |
| FR-06 | Compute & display standings | Class diagram (pending, §44) | `app/services/standings_service.py`, `app/routes/standings_routes.py` | `tests/test_standings.py` | ✅ |
| FR-07 | Knockout progression & automatic tournament completion | Activity diagram: knockout progression (pending, §44) | `app/services/knockout_service.py`, hooked into `result_service.py` and `fixture_service.py` (bye advancement) | `tests/test_knockout.py` | ✅ |

---

## Summary

All functional requirements (FR-01 through FR-07) and CR-001 are implemented and tested.
**66 automated tests passing** across the backend as of the end of Phase 6.

## Remaining before final submission

- **Diagrams (§44):** ER diagram, class diagram, sequence diagrams (auth, fixture
  generation, result → standings), and activity diagrams (tournament lifecycle, knockout
  progression) are the one deferred SRS deliverable — the full schema and service
  interactions are now finalized, so these can be drawn in one pass without needing
  revision. Replace each "(pending, §44)" cell above with the actual diagram filename
  once created (e.g. `docs/diagrams/er-diagram.png`).
- **§38/§39 polish pass:** confirm standard error-response format (`{"error": "..."}`)
  is consistent across every route, and re-verify the security checklist (secrets,
  `.env` handling) now that all routes exist.
- **Frontend integration:** React screens for auth, tournament CRUD, participant
  registration, fixtures, results entry, and standings display.
- **Integration testing:** end-to-end manual/automated pass across both teammates'
  tracks together, beyond the unit/route-level tests already in place.

## Polish / Integration / Frontend Progress

- **P1 (Polish — §38, §39):** ✅ Complete. Full route-by-route error-handling audit
  (all 6 route files) found no inconsistencies. Security checklist verified: `.env`
  never committed, no `__pycache__` tracked, no hardcoded credentials, `SECRET_KEY`
  fallback removed for consistency with `JWT_SECRET_KEY`. All 66 tests still passing.
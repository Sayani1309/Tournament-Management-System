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
| CR-001 | Guest (unauthenticated) read access to all tournament data | — (see `docs/change-log.md`) | Route-level: no auth decorator on any `GET` route across all blueprints | `tests/test_tournaments.py` (guest tests); required in `test_participants.py`, `test_fixtures.py`, `test_results.py`, `test_standings.py` | 🟡 (done for Tournament/Venue; pending for B's routes) |
| FR-03 | Register participant (team or individual) | ER diagram (pending, §44) | `app/services/participant_service.py`, `app/routes/participant_routes.py` | `tests/test_participants.py` | ⬜ |
| FR-04 | Generate fixtures (round-robin & knockout, incl. byes) | Sequence diagram: fixture generation (pending, §44) | `app/services/fixture_service.py`, `app/routes/match_routes.py` (fixtures half) | `tests/test_fixtures.py` | ⬜ |
| FR-05 | Submit match result (organizer-only, transactional) | Sequence diagram: result → standings (pending, §44) | `app/services/result_service.py`, `app/routes/match_routes.py` (results half) | `tests/test_results.py` | ⬜ |
| FR-06 | Compute & display standings | Class diagram (pending, §44) | `app/services/standings_service.py`, `app/routes/standings_routes.py` | `tests/test_standings.py` | ⬜ |
| FR-07 | Knockout progression & automatic tournament completion | Activity diagram: knockout progression (pending, §44) | `app/services/knockout_service.py` | `tests/test_knockout.py` | ⬜ |

---

## Notes

- Diagrams under `docs/diagrams/` (SRS §44) are deferred until Teammate B's Phase 1
  models (Participant, Match, etc.) land, so the ER diagram and class diagram can
  reflect the complete schema in one pass rather than being redrawn twice.
- Update the Status column and add the actual diagram filename once each diagram is
  created — replace "(pending, §44)" with a real path, e.g.
  `docs/diagrams/sequence-result-to-standings.png`.
- When a row moves from ⬜/🟡 to ✅, also confirm the corresponding SRS section (if any)
  has been updated to match the implemented behavior exactly.
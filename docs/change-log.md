# Change Log

This log records requirement changes made after the initial baseline (per SRS §5's
change-management process). Every entry here has a corresponding update in `docs/SRS.md`.

---

## CR-003 — Auth hardening and pagination

**Date:** 2026-08-26
**Reason:** Gaps identified during a full codebase review: no logout/token revocation,
no password reset, no email verification, unbounded list endpoints, no rate limiting
on auth endpoints.

**Added:**
- JWT logout via server-side token blocklist (`TokenBlocklist`, keyed by `jti`, storing
  `expires_at` for future cleanup of naturally-expired entries)
- Password reset flow (`POST /auth/forgot-password`, `POST /auth/reset-password`) —
  previously issued unused tokens are invalidated when a new one is requested.
  Development mode exposes the raw token in the API response since no SMTP provider is
  configured; production would email it instead.
- Email verification (`is_verified` field on `User`, `GET /auth/verify-email`) — tracked
  but **not enforced**; login does not require a verified account. Same dev-only token
  exposure pattern as password reset.
- Rate limiting on `/auth/login` (5/minute) and `/auth/register` (initially 5/minute,
  see addendum below)
- Pagination on `GET /tournaments`, `GET /players`, `GET /teams` — the only system-wide
  unbounded lists. Tournament-scoped lists (participants, matches, standings) remain
  unpaginated by design, since they're naturally capped by tournament size.

**Explicitly out of scope:** account lockout after failed logins, real SMTP integration,
pagination on tournament-scoped endpoints.

**Response shape change:** `GET /tournaments`, `GET /players`, `GET /teams` now return
`{"items": [...], "page": N, "per_page": N, "total": N, "total_pages": N}` instead of a
bare array.

**Status:** Approved and implemented.

### Addendum (discovered during P2 integration testing, 2026-08-26)

Manual end-to-end testing of a realistic bulk-registration workflow (an organizer
registering several players in quick succession) hit the 5/minute rate limit on
`/auth/register`, which is unrealistically tight for that use case. **Register limit
raised to 20/minute.** `/auth/login` remains at 5/minute, since brute-force protection
on a single account's password is the actual threat model there, not bulk registration.

---

## CR-002 — Player self-registration with team creation/joining

**Date:** 2026-08-24
**Reason:** The original registration flow (`POST /auth/register`) only created a
`User` row. There was no way to create a `Player` or `Team` record through the API at
all — every test and manual workflow had to insert them directly via SQLAlchemy,
bypassing the API entirely. This meant a real user could never actually register as a
tournament participant through the system as built.

**Clarified registration model** (three-tier, as specified by the team):
1. **Guests** — browse everything, no account required (see CR-001).
2. **Players** — register via `POST /auth/register` with `role=PLAYER`. Must also
   specify `participation_type` (`INDIVIDUAL` or `TEAM`). If `TEAM`, must specify
   `team_option` (`NEW`, with a `team_name`, or `EXISTING`, with a `team_id`). A
   `Player` row is created automatically and linked to the new `User`, and to a `Team`
   if applicable.
3. **Organizers** — register via `POST /auth/register` with `role=ORGANIZER`. Cannot
   include any player/team fields — rejected with `400` if they do. Organizers never
   create `Player` or `Team` records themselves.

One email = one identity, enforced by the existing `User.email` unique constraint — no
additional work needed, since an email can't register as both an Organizer and a Player.

**Added:**
- Role-specific validation in `RegisterSchema` (`app/schemas/auth_schema.py`)
- Automatic `Player`/`Team` creation inside `register_user()` (`app/services/auth_service.py`)
- `GET /teams` (public, list) — lets a registering player browse existing teams to join

**Affected SRS sections:** §7 (Participation Model), §10 (Player)

**Status:** Approved and implemented.

---

## CR-001 — Public read access for guests

**Date:** 2026-08-23
**Reason:** Unauthenticated visitors should be able to browse tournaments, participants,
fixtures, results, and standings without an account. Login is required only for actions
(creating tournaments, registering as a participant, submitting results, managing
lifecycle).

**Affected SRS sections:** §6 (Actors), §37 (API)
**Affected design:** All GET endpoints are public; POST/PUT/DELETE remain
role-protected.
**Confirmed during discussion:** match result submission is organizer-only with no
player-submission path, consistent with the original SRS §6 listing of "submit match
results" solely under Organizer.

**Status:** Approved and implemented starting with Backend Phase 3 (Tournament/Venue
routes), applied retroactively as a design rule to all subsequent routes.

---
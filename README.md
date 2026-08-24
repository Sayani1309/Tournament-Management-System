# Tournament Management System

A web-based system for creating, configuring, managing, and viewing sports and
competition tournaments — supporting both team-based (football, cricket) and
individual (chess, badminton) formats, with round-robin or knockout progression.

## Problem Statement

Organizing a tournament — registering participants, generating fair fixtures, tracking
results, and computing standings — is typically done manually or with sport-specific
tools that don't generalize across team and individual competition formats. This system
provides a single, sport-agnostic backend and frontend for running any tournament,
regardless of whether participants are teams or individuals, and regardless of whether
the format is round-robin or single-elimination knockout.

## Technology Stack

**Backend**
- Python 3.12+ / Flask 3.x
- SQLAlchemy 2.x (via Flask-SQLAlchemy)
- PostgreSQL (via `psycopg` v3)
- Flask-Migrate / Alembic for schema migrations
- Flask-JWT-Extended for authentication
- Marshmallow for request/response schema validation and serialization
- Flask-CORS
- PyTest for testing

**Frontend**
- React

## Project Objective

Support two participation types — `TEAM` and `INDIVIDUAL` — and two tournament formats —
`ROUND_ROBIN` and `KNOCKOUT` — as independent, orthogonal dimensions, without
sport-specific branching in the fixture or scoring logic. See `docs/SRS.md` for the full
requirements specification.

## Backend Status

**Complete.** All functional requirements (FR-01 through FR-07) and the guest-access
change (CR-001) are implemented and covered by 66 automated tests. See
`docs/traceability-matrix.md` for the full requirement-to-implementation mapping.

---

## Repository Structure

```
tournament-management-system/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── routes/       # HTTP endpoints (auth, tournament, venue, participant, match, standings)
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic (lifecycle rules, fixture generation, results, standings, knockout)
│   │   ├── schemas/      # Marshmallow request/response schemas
│   │   ├── constants/    # Shared enums
│   │   └── utils/
│   ├── tests/
│   ├── migrations/
│   ├── requirements.txt
│   └── run.py
└── docs/
    ├── SRS.md
    ├── change-log.md
    ├── traceability-matrix.md
    └── diagrams/          # pending — see traceability-matrix.md
```

---

## Backend Setup

### 1. Prerequisites
- Python 3.12+
- PostgreSQL running locally

### 2. Clone and enter the backend directory
```bash
git clone <repo-url>
cd tournament-management-system/backend
```

### 3. Create and activate a virtual environment
```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Create the databases
Two separate Postgres databases are required — one for development, one exclusively for
the automated test suite (tests refuse to run against a non-test database as a safety
guard):
```bash
psql -U postgres -c "CREATE DATABASE tms_dev;"
psql -U postgres -c "CREATE DATABASE tms_test;"
```

### 6. Configure environment variables
Copy the example file and fill in your own values:
```bash
cp .env.example .env
```
Generate secrets:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Fill in `backend/.env`:
```
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/tms_dev
TEST_DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/tms_test
JWT_SECRET_KEY=<generated secret>
SECRET_KEY=<a different generated secret>
FLASK_ENV=development
```
`.env` is gitignored and must never be committed. `.env.example` is the committed
template with placeholder values only.

### 7. Run migrations
```bash
flask --app run.py db upgrade
```

### 8. Run the server
```bash
flask --app run.py run
```
Confirm it's up:
```bash
curl http://localhost:5000/api/v1/health
```
Should return `{"status": "ok"}`.

### 9. Run tests
Always run from inside `backend/`:
```bash
python -m pytest -v
```
Expect all 66 tests to pass.

---

## API Reference

Base path: `/api/v1`. Governing rule (CR-001): **all `GET` endpoints are public; all
`POST`/`PUT` endpoints require authentication, almost always with the ORGANIZER role.**

| Endpoint | Method | Auth | Notes |
|---|---|---|---|
| `/auth/register` | POST | Public | |
| `/auth/login` | POST | Public | Returns JWT |
| `/auth/me` | GET | JWT required | Returns the logged-in user's profile |
| `/tournaments` | GET | **Public** | List all tournaments |
| `/tournaments/{id}` | GET | **Public** | Tournament detail |
| `/tournaments` | POST | Organizer | Create tournament (starts in DRAFT) |
| `/tournaments/{id}` | PUT | Organizer (owner only) | Locked once past DRAFT for `format`/`participant_type` |
| `/tournaments/{id}/open-registration` | POST | Organizer (owner only) | DRAFT → REGISTRATION_OPEN |
| `/tournaments/{id}/start` | POST | Organizer (owner only) | REGISTRATION_OPEN → ONGOING |
| `/venues` | GET | **Public** | |
| `/venues` | POST | Organizer | |
| `/tournaments/{id}/participants` | GET | **Public** | |
| `/tournaments/{id}/participants` | POST | Organizer | Register a team or player; requires REGISTRATION_OPEN and matching participant type |
| `/tournaments/{id}/fixtures` | POST | Organizer | Generates round-robin or knockout matches; requires ONGOING; one-time only |
| `/tournaments/{id}/matches` | GET | **Public** | |
| `/matches/{id}/result` | POST | Organizer | Transactional; updates standings and, for knockout, advances the winner. Organizer-only — players never submit results. |
| `/matches/{id}/result` | GET | **Public** | |
| `/tournaments/{id}/standings` | GET | **Public** | Ordered: points desc → score difference desc → total score desc → name asc |

### Automatic tournament completion
The tournament transitions to `COMPLETED` automatically — no explicit organizer
action — once either: the knockout final's result is submitted, or the last scheduled
round-robin match's result is submitted. See `docs/SRS.md` §11.

### Standard error responses
| Code | Meaning |
|---|---|
| 400 | Bad Request — invalid input, invalid lifecycle transition |
| 401 | Unauthorized — missing/invalid JWT |
| 403 | Forbidden — authenticated but wrong role, or not the owning organizer |
| 404 | Not Found |
| 409 | Conflict — duplicate registration, duplicate result, invalid state transition |
| 500 | Internal Server Error |

```json
{ "error": "Team is already registered in this tournament" }
```

---

## Contributing (team workflow)

- Branching: feature branches merged into `main` via review where practical
- Never commit `.env` — verify with `git status` before every commit
- Shared files requiring coordination before editing: `app/constants/enums.py`,
  `app/models/__init__.py`, `app/__init__.py`
- Update `docs/traceability-matrix.md` when a feature's implementation and tests are
  both complete, not at the end of the project
- Log any requirement change in `docs/change-log.md` before implementing it

---

## Documentation

- [`docs/SRS.md`](docs/SRS.md) — full requirements specification
- [`docs/change-log.md`](docs/change-log.md) — record of requirement changes since baseline
- [`docs/traceability-matrix.md`](docs/traceability-matrix.md) — requirement → design → implementation → test mapping
- [`docs/diagrams/`](docs/diagrams/) — ER diagram, class diagram, sequence diagrams, activity diagrams (pending — next documentation task)
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

---

## Repository Structure

```
tournament-management-system/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── routes/       # HTTP endpoints (auth, tournament, venue, participant, match, standings)
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic (lifecycle rules, fixture generation, results, standings)
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
    └── diagrams/
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

---

## API Overview

Base path: `/api/v1`

| Area | Auth | Notes |
|---|---|---|
| `POST /auth/register`, `POST /auth/login` | Public | Anyone can register/log in |
| `GET /auth/me` | JWT required | Returns the logged-in user's profile |
| `GET /tournaments`, `GET /tournaments/{id}` | **Public** | Guests can browse without an account |
| `POST /tournaments`, `PUT /tournaments/{id}` | Organizer only | |
| `POST /tournaments/{id}/open-registration`, `POST /tournaments/{id}/start` | Organizer only | Lifecycle transitions |
| `GET /venues` | **Public** | |
| `POST /venues` | Organizer only | |
| `GET /tournaments/{id}/participants` | **Public** | |
| `POST /tournaments/{id}/participants` | Organizer only | |
| `GET /tournaments/{id}/matches`, `GET /matches/{id}/result` | **Public** | |
| `POST /tournaments/{id}/fixtures`, `POST /matches/{id}/result` | Organizer only | Result submission is organizer-only, not player-submitted |
| `GET /tournaments/{id}/standings` | **Public** | |

See `docs/SRS.md` §37 for the complete specification and `docs/change-log.md` (CR-001)
for the reasoning behind the public/organizer-only split.

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
- [`docs/diagrams/`](docs/diagrams/) — ER diagram, class diagram, sequence diagrams, activity diagrams (added once the full schema is finalized)
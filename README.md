# MyHouse24

[![CI](https://github.com/ValeriaTsentylo/MyHouse24/actions/workflows/ci.yml/badge.svg)](https://github.com/ValeriaTsentylo/MyHouse24/actions/workflows/ci.yml)

Web application for managing residential complexes: houses and apartments, owners,
utility services and tariffs, receipts and personal accounts, cash-flow statements
and admin statistics. Django 5 + PostgreSQL + Celery, fully dockerized.

---

## Stack

| Layer     | Technology |
|-----------|------------|
| Backend   | Python 3.12, Django 5.1 |
| Database  | PostgreSQL 16 (`psycopg` / `psycopg2-binary`) |
| Auth      | `django-allauth` — email login, mandatory email confirmation |
| Async     | Celery 5 + Redis 7 (transactional email) |
| Frontend  | Django templates, `django-ajax-datatable` for server-side tables |
| Infra     | Docker / docker compose, GitHub Actions |
| Quality   | pytest + pytest-django + coverage, ruff, djLint, pre-commit |
| Tooling   | Poetry, Task (`Taskfile.yml`), django-debug-toolbar |
| Config    | `python-decouple` + `python-dotenv` |

---

## Quick start (Docker)

Everything — web, PostgreSQL, Redis and a Celery worker — comes up with one command.

```bash
git clone https://github.com/ValeriaTsentylo/MyHouse24.git
cd MyHouse24
cp .env.example .env_local      # required: compose reads it via env_file

docker compose up --build       # or: task up
```

App: http://localhost:8000 · admin: http://localhost:8000/admin/

Migrations run automatically on start. Create an admin user and the standard roles:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell -c \
  "from src.roles.models import RolePermission; RolePermission.create_standard_roles()"
```

Stop with `docker compose down` (or `task down`); add `-v` to drop the `pgdata` volume.

---

## Local setup (Poetry)

Requires Python 3.12, PostgreSQL 14+, Redis 6+ and [Poetry](https://python-poetry.org/).

```bash
poetry install                                  # task install
cp .env.example .env_local                      # then fill in SECRET_KEY, DB_*, ...
createdb myhouse24

poetry run python manage.py migrate             # task migrate
poetry run python manage.py createsuperuser     # task createsuperuser
poetry run python manage.py runserver           # task runserver
```

Celery worker in a second terminal (Redis must be running):

```bash
poetry run celery -A config worker -l info      # task celery
```

---

## Configuration

Settings are read with `python-decouple`. `ENVIRONMENT` selects the env file:
`local` (default) loads `.env_local`, anything else loads `.env_prod`.
`.env.example` is the template — copy it, never commit the filled-in copy.

| Variable | Notes |
|----------|-------|
| `SECRET_KEY` | required, no default |
| `DEBUG` | defaults to `False` — set `True` locally |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | comma-separated |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | required; `DB_HOST`/`DB_PORT` default to `localhost:5432` |
| `REDIS_URL` | Celery broker and result backend, default `redis://localhost:6379/0` |
| `EMAIL_*` | optional under `DEBUG=True` — mail is printed to the console |
| `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY` | form verification |
| `SECURE_SSL_REDIRECT` | production only, defaults to `True` |

With `DEBUG=False` Django turns on HSTS (30 days), SSL redirect, secure session and
CSRF cookies, `X-Frame-Options: DENY` and content-type nosniff. Debug toolbar and
media serving are wired up only when `DEBUG=True`.

---

## Project structure

```
config/                 Django project: settings, urls, wsgi/asgi, celery
manage.py
src/
  core/                 shared entities — Gallery, GalleryImage
  users/                custom User (email as login), Celery email task
  roles/                RolePermission (proxy over Group) + standard role bootstrap
  houses/               House, Section, Floor, Staff
  apartments/           Apartment, ApartmentOwner
  service/              UnitOfChange, Service, Tariff, ServicePrice, Account
  payments_section/     Receipt, PersonalAccount, InStatement, ExStatement
  statistic/            admin dashboard / statistics
tests/                  pytest suite (conftest fixtures, users, access control)
templates/              global templates
static/ staticfiles/    source static files / collectstatic output
media/                  user uploads
docs/DB_schema.png      database diagram
.github/workflows/ci.yml
Dockerfile docker-compose.yml Taskfile.yml
```

### Domain model

- **House → Section → Floor → Apartment** — the physical hierarchy of a complex.
- **Apartment ↔ ApartmentOwner ↔ PersonalAccount** — who owns what and which account is billed.
- **Service → Tariff → ServicePrice** — services with units of measurement, priced per tariff.
- **Receipt / InStatement / ExStatement** — issued invoices, incoming and outgoing statements.
- **User + RolePermission** — Director, Manager, Accountant, Electrician, Plumber, User;
  each role is a Django `Group` with a preset permission list.

### URL map

| Prefix | App |
|--------|-----|
| `/admin/` | Django admin |
| `/core/` | `src.core` |
| `/users/` | `src.users` |
| `/houses/` | `src.houses` |
| `/apartments/` | `src.apartments` |
| `/statistic/` | `src.statistic` |
| `/system/settings/` | `src.service` |
| `/__debug__/` | debug toolbar (`DEBUG=True` only) |

---

## Tests and linting

```bash
poetry run pytest --cov=src --cov-report=term-missing   # task test
poetry run ruff check --fix . && poetry run ruff format .  # task lint
poetry run python manage.py check --deploy              # task check
```

`tests/test_access_control.py` walks the real URLConf, so every newly registered
admin view is checked against anonymous access the moment it is added.

Enable the hooks once — ruff, ruff-format, djLint and the standard hygiene checks
(trailing whitespace, private-key detection, large files) run on every commit:

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

CI (GitHub Actions, on push to `main` and every PR) spins up PostgreSQL 16 and
Redis 7 and runs: ruff lint + format check → `manage.py check` →
`makemigrations --check` → pytest with coverage.

---

## Task shortcuts

```bash
task install          task migrate         task makemigrations
task runserver        task collectstatic   task createsuperuser
task shell            task celery          task check
task up               task down            task test           task lint
```

---

## Notes

- The user model is `users.User` — email is the login field, there is no username.
- Email confirmation is mandatory; links expire after 3 days and the user is logged
  in automatically once confirmed.
- Mail is sent from a Celery task (`src.users.tasks.send_email_task`), so a worker
  has to be running in production; with `DEBUG=True` the console backend is used
  and no worker or SMTP credentials are needed.
- Logging goes to the console: `INFO` at the root, `DEBUG` for `src.*` when `DEBUG=True`.

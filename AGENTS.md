# AGENTS.md

## Project overview

SongLib is a Django web application for managing song lyrics and setlists. It supports ChordPro-formatted lyrics with real-time chord transposition, multiple notation systems (English and Latin), and organization-based multi-tenancy so teams can collaborate on shared song libraries.

- **Framework:** Django 4.2 with Django REST Framework
- **Package manager:** `uv`
- **Database:** PostgreSQL (production) / SQLite (development fallback)
- **Static files:** WhiteNoise
- **Container:** Docker (single container, gunicorn on port 80)

## Environment setup

Configuration is loaded from a `.env` file at the project root via `django-environ`. Required variables:

```
DEBUG=on
SECRET_KEY=your-secret-key
DB_NAME=songlib
DB_USER=postgres
DB_PASS=secret
DB_HOST=localhost
DB_PORT=5432
```

For local development, SQLite is used when `DB_HOST` is empty.

## Dev environment commands

All commands use `uv run` to execute within the managed virtual environment.

```bash
# Install dependencies
uv sync

# Apply database migrations
uv run manage.py migrate

# Create a superuser
uv run manage.py createsuperuser

# Start development server
uv run manage.py runserver

# Compile requirements.txt from pyproject.toml
make requirements
```

## Project structure

```
app/           # Main Django application (models, views, forms, templates)
songlib/       # Django project settings, URLs, WSGI/ASGI
templates/     # HTML templates (base.html + app-specific templates)
locale/        # i18n translations (Spanish supported)
migrations/    # Database migrations inside app/migrations/
```

Key files:
- `app/models.py` — `Organization`, `Membership`, `UserProfile`, `Song`, `Category`, `Tag`, `SetList`, `SetListSong`
- `app/views.py` — All view functions and DRF viewsets
- `app/chords.py` — ChordPro parsing and chord transposition logic
- `app/forms.py` — Django forms
- `app/serializers.py` — DRF serializers (used for setlist song ordering API)
- `songlib/urls.py` — Root URL configuration
- `songlib/settings.py` — Project settings (reads from `.env`)

## Data model conventions

- Every `Song`, `Category`, `Tag`, and `SetList` belongs to an `Organization`.
- The active organization for a user is stored in `UserProfile.active_organization`.
- All views filter data by the current user's active organization via `app/middleware.py`.
- `Membership` enforces roles: `admin` or `member`. Only admins can manage organization settings and members.

## Testing

```bash
uv run manage.py test
```

Tests live in `app/tests.py`. The test suite uses Django's `TestCase`. When adding new features, add corresponding tests to that file.

## Code style guidelines

- Follow PEP 8. Keep lines under 100 characters where practical.
- Use Django's translation utilities (`gettext_lazy as _`) for all user-visible strings.
- Use `django-environ` for all settings — never hardcode secrets or credentials.
- Template names follow the pattern `app/<model_name>_<action>.html` (e.g., `song_form.html`, `song_list.html`).
- URL names follow the pattern `<model>_<action>` (e.g., `song_detail`, `setlist_create`).
- Keep views as function-based views (FBVs); DRF `ViewSet` is only used for the setlist song ordering API.

## Migrations

After changing `app/models.py`, always generate and apply migrations:

```bash
uv run manage.py makemigrations
uv run manage.py migrate
```

Data migrations live alongside schema migrations in `app/migrations/`. Use them for backfilling data when needed (see `0006_convert_html_lyrics_to_plain_text.py` as an example).

## Docker

```bash
# Build the image
docker build -t songlib .

# Run the container
docker run --name songlib \
  -e DEBUG=off \
  -e SECRET_KEY=yoursecret \
  -e DB_NAME=songlib \
  -e DB_USER=postgres \
  -e DB_PASS=secret \
  -e DB_HOST=dbhost \
  -e DB_PORT=5432 \
  songlib
```

The container entrypoint (`runserver.sh`) runs `migrate`, `createadminuser`, then starts gunicorn on port 80.

## i18n

Translations are in `locale/es/LC_MESSAGES/`. To update after adding new translatable strings:

```bash
uv run manage.py makemessages -l es
uv run manage.py compilemessages
```

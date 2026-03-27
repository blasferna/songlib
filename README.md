# SongLib: My Personal Song Library

SongLib is a Django web application for managing song lyrics and setlists. It supports ChordPro-formatted lyrics with real-time chord transposition, multiple notation systems, and organization-based multi-tenancy so teams can collaborate on shared song libraries.

## Features

- **ChordPro lyrics** — Write lyrics with inline chords (`[Am]Amazing [G]grace`) and render them with separated chord/lyric lines.
- **Chord transposition** — Transpose songs to any key on the fly; supports both English (C, D, E…) and Latin (Do, Re, Mi…) notation.
- **Setlist management** — Create setlists with drag-and-drop song ordering, per-song key override, adjustable font size, and page-break control.
- **Setlist reader** — A public, offline-friendly single-page view for sharing setlists with band members.
- **Setlist export** — Export setlists as plain-text `.txt` files, with or without chords.
- **Printable setlist views** — Print-ready layouts with configurable page sizes (A4, Letter, Legal).
- **Categories & tags** — Organize songs by category and apply multiple tags for flexible filtering.
- **Multi-organization support** — Create multiple organizations with admin/member roles; switch between them seamlessly.
- **User registration & authentication** — Self-service sign-up with automatic personal organization creation.
- **Docker deployment** — Ship as a single container image with PostgreSQL support.

## Screenshots

| | | |
|:---:|:---:|:---:|
| ![Screenshot 1](screenshots/screenshot_1.png) | ![Screenshot 2](screenshots/screenshot_2.png) | ![Screenshot 3](screenshots/screenshot_3.png) |
| ![Screenshot 4](screenshots/screenshot_4.png) | ![Screenshot 5](screenshots/screenshot_5.png) | ![Screenshot 6](screenshots/screenshot_6.png) |

## How to Run SongLib

### Local Installation

1. Clone the repository to your local machine.
2. Create a virtual environment and activate it.
3. Install the required packages using `uv sync`.
4. Run migrations using `uv run manage.py migrate`.
5. Create a superuser for the Django admin interface using `uv run manage.py createsuperuser`.
6. Start the development server using `uv run manage.py runserver`.
7. Access the application at `localhost:8000`.

### Docker

The SongLib application is also available as a Docker image. You can pull and run the Docker image using the following commands:

1. Pull the Docker image:

    ```
    docker pull ghcr.io/blasferna/songlib:latest
    ```

2. Run the Docker image:

    ```
    docker run --name songlib -e DEBUG=off -e DB_NAME=songlib -e DB_USER=postgres -e DB_PASS=secret -e DB_HOST=dbhost -e DB_PORT=5432 -e SECRET_KEY=secreto ghcr.io/blasferna/songlib
    ```

Please replace the `DB_HOST`, `DB_PASS`, and `SECRET_KEY` placeholders with your actual database host, password, and Django secret key.

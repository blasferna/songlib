# SongLib

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
<img width="1309" height="731" alt="06" src="https://github.com/user-attachments/assets/517e672f-df14-4649-bbb8-3cf21fabb976" />

| | | |
|:---:|:---:|:---:|
| <img width="300" height="748" alt="05" src="https://github.com/user-attachments/assets/d5beb774-6fae-4282-ac0e-43b09a4ff6a1" /> |<img width="300" alt="01" src="https://github.com/user-attachments/assets/376dca4d-13f2-4fb3-98c0-15a0db64375b" />  |  <img width="300" alt="02" src="https://github.com/user-attachments/assets/2e288afa-0b32-4934-8ce8-cf0c393007c2" /> |
| <img width="300" alt="03" src="https://github.com/user-attachments/assets/c1d22c4a-2d6a-43f1-acac-ffc15da0b42c" />  | <img width="300" alt="04" src="https://github.com/user-attachments/assets/eca00c7b-4ca1-4aa0-a8ba-7702a56db51d" /> | <img width="300" alt="07" src="https://github.com/user-attachments/assets/a3bfc9e7-0d11-4386-9489-37fe1957aac6" />|

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

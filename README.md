# SongLib: My Personal Song Library

## Description

SongLib is a personal Django web application designed to help me manage my song lyrics and setlists. The application allows me to store lyrics, categorize songs, and create and manage setlists for performances. It provides a straightforward Django admin interface for managing song lyrics and setlists. Features include tag-based song categorization, song ordering within setlists, and printable setlist views. 

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

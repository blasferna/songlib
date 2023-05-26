python manage.py collectstatic --no-input
python manage.py migrate
gunicorn --bind :80 --workers 2 songlib.wsgi

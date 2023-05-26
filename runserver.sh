python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createadminuser
gunicorn --bind :80 --workers 2 songlib.wsgi

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

def create_adminuser():
    from django.contrib.auth.models import User
    try:
        owner = User.objects.get(username="admin")
    except ObjectDoesNotExist:
        User.objects.create_superuser(username="admin", 
        email='admin@test.com', password="admin")



class Command(BaseCommand):
    help = 'Create superuser without params'

    def handle(self, *args, **kwargs):
        create_adminuser()
        self.stdout.write("Admin user created")

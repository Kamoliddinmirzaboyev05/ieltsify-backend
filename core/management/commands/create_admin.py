from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser automatically if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'superadmin'
        email = 'superadmin@example.com'
        password = 'kamoliddin05'

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Creating superuser for {username}...')
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists.'))

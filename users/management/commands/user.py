from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from tqdm import tqdm

from users.models import Preference, User


class Command(BaseCommand):
    help = "Check integrity all users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
        )
        parser.add_argument(
            "--integrity",
            action="store_true",
            help="check and fix integrity for missing data for user models",
        )

    def handle(self, *args, **options):
        self.verbose = options["verbose"]
        self.fix = options["fix"]
        if options["integrity"]:
            self.integrity()

    def integrity(self):
        count = 0
        for user in tqdm(User.objects.filter(is_active=True)):
            i = user.identity.takahe_identity
            if i.public_key is None:
                count += 1
                if self.fix:
                    i.generate_keypair()
            if i.inbox_uri is None:
                count += 1
                if self.fix:
                    i.ensure_uris()
            if not Preference.objects.filter(user=user).first():
                if self.fix:
                    Preference.objects.create(user=user)
                count += 1
        print(f"{count} issues")

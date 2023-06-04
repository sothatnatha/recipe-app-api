""""
Django command to wait for the database to available.
"""
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Django command to wait for the database."""
    def handle(self, *args, **options):
        """Entrypoint command for waiting for the database"""
        self.stdout.write("Waiting for database...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database uavailable, Wait for 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is available'))

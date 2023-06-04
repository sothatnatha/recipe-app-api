""""
Django command to wait for the database to available.
"""

from typing import Any, Optional
from django.core.management import BaseCommand

class Command(BaseCommand):
    """Django command to wait for the database."""

    def handle(self, *args, **options):
        pass
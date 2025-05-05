"""Custom Reset DB Command for Django Admin."""

from typing import override

from django.core import management
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """Custom command to reset all tables in the database."""

    help = 'Reset all tables in Postgres database'

    @override
    def handle(self, *args: tuple, **options: dict) -> None:
        self.stdout.write(self.style.WARNING('Resetting all database tables'))

        with connection.cursor() as cursor:
            cursor.execute('DROP SCHEMA public CASCADE;')
            cursor.execute('CREATE SCHEMA public;')

        management.call_command('migrate')

        self.stdout.write(self.style.SUCCESS('Successfully reset database'))

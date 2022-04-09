"""
Custom Reset DB Command for Django Admin
"""

from django.core import management
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Reset all tables in Postgres database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Resetting all database tables'))

        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")

        management.call_command('migrate')

        self.stdout.write(self.style.SUCCESS('Successfully reset database'))

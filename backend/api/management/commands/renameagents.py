"""
Custom Reset DB Command for Django Admin
"""

from django.core.management.base import BaseCommand
from api.simulation.models import AgentConfig


class Command(BaseCommand):
    help = 'Reset all agents in Postgres database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Renaming agents'))

        for i, agent in enumerate(AgentConfig.objects.all()):
            agent.name = f'default-agent-{i}'
            agent.save()

        self.stdout.write(self.style.SUCCESS('Successfully renamed agents'))

"""Custom Reset DB Command for Django Admin."""

from typing import override

from django.core.management.base import BaseCommand

from api.simulation.models import AgentConfig


class Command(BaseCommand):
    """Custom command to reset all agents in the database."""

    help = 'Reset all agents in Postgres database'

    @override
    def handle(self, *args: tuple, **options: dict) -> None:
        self.stdout.write(self.style.WARNING('Renaming agents'))

        for i, agent in enumerate(AgentConfig.objects.all()):
            agent.name = f'default-agent-{i}'
            agent.save()

        self.stdout.write(self.style.SUCCESS('Successfully renamed agents'))

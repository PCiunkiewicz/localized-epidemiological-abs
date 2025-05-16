"""Localized Epidemiological ABS API Models."""

from __future__ import annotations

from pathlib import Path

from django.core.exceptions import FieldDoesNotExist
from django.core.validators import MinValueValidator, validate_slug
from django.db import models

# TODO: all models - write appropriate on-create and on-delete logic
# TODO: add Export model and logic for figures


class BaseModel(models.Model):
    """Base Model for all models in the simulation app."""

    class Meta:
        abstract = True

    @classmethod
    def contains_field(cls, field: str) -> bool:
        """Check if the model contains a specific field."""
        try:
            cls._meta.get_field(field)
            return True
        except FieldDoesNotExist:
            return False


class Terrain(BaseModel):
    """Terrain Model representing different types of surfaces in the simulation."""

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    value = models.CharField(max_length=7)
    color = models.CharField(max_length=7)
    material = models.CharField(max_length=250, null=True)
    walkable = models.BooleanField(default=True)
    interactive = models.BooleanField(default=False)
    restricted = models.BooleanField(default=False)
    access_level = models.IntegerField(default=0)


class Simulation(BaseModel):
    """Simulation Model representing the simulation parameters."""

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    mapfile = models.CharField(max_length=250)
    xy_scale = models.FloatField(default=10.0, validators=[MinValueValidator(1)])
    t_step = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_iter = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    save_resolution = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    save_verbose = models.BooleanField(default=False)
    terrain = models.ManyToManyField(Terrain, blank=True)


class Virus(BaseModel):
    """Virus Model representing the virus parameters."""

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    attack_rate = models.FloatField(default=0.07, validators=[MinValueValidator(0)])
    infection_rate = models.FloatField(default=0.021, validators=[MinValueValidator(0)])
    fatality_rate = models.FloatField(default=0.01, validators=[MinValueValidator(0)])


class Scenario(BaseModel):
    """Scenario Model representing combined parameters for simulation scenarios."""

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    virus = models.ForeignKey(Virus, on_delete=models.CASCADE)
    prevention = models.JSONField()  # TODO: figure out best structure for this, maybe split vax and mask as models?


class AgentConfig(BaseModel):
    """Agent Configuration Model representing the agent parameters."""

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    default = models.JSONField(default=dict)  # TODO: come back and finish this json validation
    random_agents = models.PositiveIntegerField()
    random_infected = models.PositiveIntegerField()
    custom = models.JSONField(default=list)


class Run(BaseModel):
    """Run Model representing an individual simulation run or parallel batch."""

    class Status(models.TextChoices):
        """Run `status` field possible choices."""

        CREATED = 'CREATED'
        RUNNING = 'RUNNING'
        SUCCESS = 'SUCCESS'
        FAILURE = 'FAILURE'

    name = models.CharField(max_length=250, validators=[validate_slug])
    status = models.CharField(max_length=7, choices=Status.choices, default=Status.CREATED)
    save_dir: str | Path = models.CharField(max_length=250, null=True)
    config: str | Path = models.CharField(max_length=250, null=True)
    logfile: str | Path = models.CharField(max_length=250, null=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.RESTRICT)
    agents = models.ForeignKey(AgentConfig, on_delete=models.RESTRICT)
    runs = models.IntegerField(default=1, validators=[MinValueValidator(1)])

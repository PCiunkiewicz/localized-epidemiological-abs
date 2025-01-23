"""
Localized Epidemiological ABS API Models
"""

from django.core.validators import MinValueValidator, validate_slug
from django.db import models

# TODO: all models - write appropriate on-create and on-delete logic
# TODO: add Export model and logic for figures


class Terrain(models.Model):
    """
    Terrain Model
    """

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    value = models.CharField(max_length=7)
    color = models.CharField(max_length=7)
    material = models.CharField(max_length=250, null=True)
    walkable = models.BooleanField(default=True)
    interactive = models.BooleanField(default=False)
    restricted = models.BooleanField(default=False)
    access_level = models.IntegerField(default=0)


class Simulation(models.Model):
    """
    Simulation Details Model
    """

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    mapfile = models.CharField(max_length=250)
    xy_scale = models.FloatField(default=10.0, validators=[MinValueValidator(1)])
    t_step = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    max_iter = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    save_resolution = models.IntegerField(default=60, validators=[MinValueValidator(1)])
    save_verbose = models.BooleanField(default=False)
    terrain = models.ManyToManyField(Terrain, blank=True)


class Virus(models.Model):
    """
    Virus Model
    """

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    attack_rate = models.FloatField(default=0.07, validators=[MinValueValidator(0)])
    infection_rate = models.FloatField(default=0.021, validators=[MinValueValidator(0)])
    fatality_rate = models.FloatField(default=0.01, validators=[MinValueValidator(0)])


class Scenario(models.Model):
    """
    Scenario Model
    """

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    sim = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    virus = models.ForeignKey(Virus, on_delete=models.CASCADE)
    prevention = models.JSONField()  # TODO: figure out best structure for this, maybe split vax and mask as models?


class AgentConfig(models.Model):
    """
    Agent Configuration Model
    """

    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    default = models.JSONField(default=dict)  # TODO: come back and finish this json validation
    random_agents = models.PositiveIntegerField()
    random_infected = models.PositiveIntegerField()
    custom = models.JSONField(default=list)


class Run(models.Model):
    """
    Run Model
    """

    class Status(models.TextChoices):
        """
        Run `status` field valid options
        """

        CREATED = 'CREATED'
        RUNNING = 'RUNNING'
        SUCCESS = 'SUCCESS'
        FAILURE = 'FAILURE'

    name = models.CharField(max_length=250, validators=[validate_slug])
    status = models.CharField(max_length=7, choices=Status.choices, default=Status.CREATED)
    save_dir = models.CharField(max_length=250, null=True)
    config = models.CharField(max_length=250, null=True)
    logfile = models.CharField(max_length=250, null=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.RESTRICT)
    agents = models.ForeignKey(AgentConfig, on_delete=models.RESTRICT)
    runs = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    parallel = models.BooleanField(default=False)  # TODO: consider replacing with n_jobs or adding
    # TODO: add status and special logic for polling completeness

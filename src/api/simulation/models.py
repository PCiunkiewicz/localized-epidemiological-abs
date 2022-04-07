"""
Localized Epidemiological ABS API Models
"""

from django.db import models
from django.core.validators import validate_slug, MinLengthValidator, MinValueValidator


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


class Terrain(models.Model):
    """
    Terrain Model
    """
    name = models.CharField(max_length=250, unique=True, validators=[validate_slug])
    value = models.CharField(max_length=7, validators=MinLengthValidator(7))
    color = models.CharField(max_length=7, validators=MinLengthValidator(7))
    material = models.CharField(max_length=250, null=True)
    walkable = models.BooleanField(default=True)
    restricted = models.BooleanField(default=True)
    access_level = models.IntegerField(default=0)
    simulations = models.ManyToManyField(Simulation)


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
    prevention = models.JSONField() # TODO: figure out best structure for this, maybe split vax and mask as models?


class AgentConfig(models.Model):
    """
    Agent Configuration Model
    """
    default = models.JSONField(default=dict)
    random_agents = models.PositiveIntegerField()
    random_infected = models.PositiveIntegerField()
    custom = models.JSONField(default=list)


class Run(models.Model):
    """
    Run Model
    """
    name = models.CharField(max_length=250, validators=[validate_slug])
    save_dir = models.CharField(max_length=250, null=True) # TODO: create on save as `$id-$name`
    scenario = models.ForeignKey(Scenario)
    runs = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    parallel = models.BooleanField(default=False)

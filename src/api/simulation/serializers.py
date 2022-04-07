"""
MLFramework API Model Serializers
"""
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Simulation, Terrain, Virus, Scenario, AgentConfig, Run


class Nested(serializers.PrimaryKeyRelatedField):
    """
    Nested serializer for full foreign-key representation
    """
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        if self.serializer is not None and not issubclass(self.serializer, serializers.Serializer):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return not bool(self.serializer)

    def to_representation(self, value):
        if self.serializer:
            return self.serializer(value, context=self.context).data
        return super().to_representation(value)


# TODO: figure out many-to-many serialization for Terrain
class SimulationSerializer(serializers.ModelSerializer):
    """
    Simulation Model Serializer
    """
    class Meta:
        model = Simulation
        fields = '__all__'

    def validate_mapfile(self, data):
        """
        Validate `mapfile` field on Simulation
        """
        filetypes = ('.png', '.gif')
        if not data.endswith(filetypes):
            raise ValidationError({'mapfile': f'must have filetype in {filetypes}'})

        return data


class TerrainSerializer(serializers.ModelSerializer):
    """
    Terrain Model Serializer
    """
    class Meta:
        model = Terrain
        fields = '__all__'

    def validate(self, attrs):
        """
        Validate fields on Terrain
        """
        for field in {'value', 'color'}:
            if not re.search(r'^#(?:[0-9a-fA-F]{6})$', attrs[field]):
                raise ValidationError({field: f'invalid hex color: {attrs[field]}'})
        return super().validate(attrs)


class VirusSerializer(serializers.ModelSerializer):
    """
    Virus Serializer
    """
    class Meta:
        model = Virus
        fields = '__all__'


class ScenarioSerializer(serializers.ModelSerializer):
    """
    Scenario Serializer
    """
    sim = Nested(queryset=Simulation.objects.all(), serializer=SimulationSerializer)
    virus = Nested(queryset=Virus.objects.all(), serializer=VirusSerializer)

    class Meta:
        model = Scenario
        fields = '__all__'


class AgentConfigSerializer(serializers.ModelSerializer):
    """
    AgentConfig Serializer
    """
    class Meta:
        model = AgentConfig
        fields = '__all__'

    def validate(self, attrs): # TODO: come back and finish this json validation, maybe use dataclasses from sim
        return super().validate(attrs)


class RunSerializer(serializers.ModelSerializer):
    """
    Run Serializer
    """
    class Meta:
        model = Run
        fields = '__all__'

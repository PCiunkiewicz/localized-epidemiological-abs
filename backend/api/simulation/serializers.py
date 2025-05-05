"""Localized Epidemiological Simulation API Model Serializers."""

import os
import re
from typing import Any, override

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.simulation.models import AgentConfig, Run, Scenario, Simulation, Terrain, Virus


class Nested(serializers.PrimaryKeyRelatedField):
    """Nested serializer for full foreign-key representation."""

    @override
    def __init__(self, **kwargs: dict) -> None:
        self.serializer = kwargs.pop('serializer', None)
        if self.serializer is not None and not issubclass(self.serializer, serializers.Serializer):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    @override
    def use_pk_only_optimization(self) -> bool:
        return not bool(self.serializer)

    @override
    def to_representation(self, value) -> Any:
        if self.serializer:
            return self.serializer(value, context=self.context).data
        return super().to_representation(value)


class TerrainSerializer(serializers.ModelSerializer):
    """Terrain Model Serializer."""

    class Meta:
        model = Terrain
        fields = '__all__'

    @override
    def validate(self, attrs: Any) -> Any:
        """Validate `Terrain` hex colors."""
        for field in {'value', 'color'}:
            if not re.search(r'^#(?:[0-9a-fA-F]{6})$', attrs[field]):
                raise ValidationError({field: f'invalid hex color: {attrs[field]}'})
        return super().validate(attrs)


class SimulationSerializer(serializers.ModelSerializer):
    """Simulation Model Serializer."""

    terrain = TerrainSerializer(read_only=True, many=True)

    class Meta:
        model = Simulation
        fields = '__all__'

    def validate_mapfile(self, data: Any) -> Any:
        """Validate `mapfile` path on Simulation."""
        filetypes = ('.png', '.gif')
        if os.path.isdir(data):
            for file in os.listdir(data):
                if not file.endswith(filetypes):
                    raise ValidationError({'mapfile': f'must have filetype in {filetypes}'})
            return data

        if not data.endswith(filetypes):
            raise ValidationError({'mapfile': f'must have filetype in {filetypes}'})
        if not os.path.isfile(data):
            raise ValidationError({'mapfile': f'file `{data}` does not exist'})

        return data


class VirusSerializer(serializers.ModelSerializer):
    """Virus Model Serializer."""

    class Meta:
        model = Virus
        fields = '__all__'


class ScenarioSerializer(serializers.ModelSerializer):
    """Scenario Model Serializer."""

    sim = Nested(queryset=Simulation.objects.all(), serializer=SimulationSerializer)
    virus = Nested(queryset=Virus.objects.all(), serializer=VirusSerializer)

    class Meta:
        model = Scenario
        fields = '__all__'


class AgentConfigSerializer(serializers.ModelSerializer):
    """AgentConfig Model Serializer."""

    class Meta:
        model = AgentConfig
        fields = '__all__'

    @override
    def validate(
        self, attrs: Any
    ) -> Any:  # TODO: come back and finish this json validation, maybe use dataclasses from sim
        return super().validate(attrs)


class RunSerializer(serializers.ModelSerializer):
    """Run Model Serializer."""

    scenario = Nested(queryset=Scenario.objects.all(), serializer=ScenarioSerializer)
    agents = Nested(queryset=AgentConfig.objects.all(), serializer=AgentConfigSerializer)

    class Meta:
        model = Run
        fields = '__all__'

    @override
    def validate(self, attrs: Any) -> Any:
        if not attrs.get('parallel', False) and attrs.get('runs', 1) > 1:
            raise ValidationError({'runs': 'cannot have `runs` > 1 if `parallel` is false'})
        return super().validate(attrs)

"""Localized Epidemiological Simulation API Model Serializers."""

import re
from typing import Any, override

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.simulation import models
from utilities.paths import MAPFILES
from utilities.types.config import ScenarioConfig, SimplifiedAgentSpec
from utilities.types.scenario import PreventionIndex


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
        model = models.Terrain
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
        model = models.Simulation
        fields = '__all__'

    def validate_mapfile(self, data: Any) -> Any:
        """Validate `mapfile` path on Simulation."""
        filetypes = ('.png', '.gif')
        if not (path := MAPFILES.rel / data).exists():
            raise ValidationError({'mapfile': f'path `{data}` does not exist'})
        elif path.is_dir():
            if not any(file.suffix in filetypes for file in path.iterdir()):
                raise ValidationError({'mapfile': f'no valid files of type {filetypes} found in `{path}`'})
        elif path.is_file():
            if path.suffix not in filetypes:
                raise ValidationError({'mapfile': f'must have filetype in {filetypes}'})

        return path


class VirusSerializer(serializers.ModelSerializer):
    """Virus Model Serializer."""

    class Meta:
        model = models.Virus
        fields = '__all__'


class PreventionSerializer(serializers.ModelSerializer):
    """Prevention Model Serializer."""

    class Meta:
        model = models.Prevention
        fields = '__all__'

    @override
    def validate(self, attrs: Any) -> Any:
        """Validate prevention mask and vax attributes."""
        try:
            PreventionIndex(**attrs)
        except Exception as e:
            raise ValidationError({'prevention': f'Invalid prevention index: {e}'})

        return super().validate(attrs)


class ScenarioSerializer(serializers.ModelSerializer):
    """Scenario Model Serializer."""

    class Meta:
        model = models.Scenario
        fields = '__all__'


class NestedScenarioSerializer(ScenarioSerializer):
    """Nested FK field Scenario Model Serializer."""

    sim = Nested(queryset=models.Simulation.objects.all(), serializer=SimulationSerializer)
    virus = Nested(queryset=models.Virus.objects.all(), serializer=VirusSerializer)
    prevention = Nested(queryset=models.Prevention.objects.all(), serializer=PreventionSerializer)


class AgentConfigSerializer(serializers.ModelSerializer):
    """AgentConfig Model Serializer."""

    class Meta:
        model = models.AgentConfig
        fields = '__all__'

    @override  # TODO: come back and finish this json validation, maybe use dataclasses from sim
    def validate(self, attrs: Any) -> Any:
        """Validate `AgentConfig` fields."""
        if attrs['random_infected'] > attrs['random_agents']:
            raise ValidationError({'random_infected': f'must be <= random_agents ({attrs["random_agents"]})'})

        try:
            SimplifiedAgentSpec.from_dict(attrs['default'])
        except Exception as e:
            raise ValidationError({'default': f'invalid default agent spec: {e}'})

        custom = ScenarioConfig._process_agents({'agents': attrs})
        for i, spec in enumerate(custom):
            try:
                SimplifiedAgentSpec.from_dict({**attrs['default'], **spec})
            except Exception as e:
                raise ValidationError({'custom': f'invalid custom agent spec at index {i}: {e}'})

        if attrs['random_agents'] + len(attrs['custom']) == 0:
            raise ValidationError(
                {
                    'random_agents': 'must have non-zero total agents (random + custom)',
                    'custom_agents': 'must have non-zero total agents (random + custom)',
                }
            )

        return super().validate(attrs)


class RunSerializer(serializers.ModelSerializer):
    """Run Model Serializer."""

    class Meta:
        model = models.Run
        fields = '__all__'


class NestedRunSerializer(RunSerializer):
    """Nested FK field Run Model Serializer."""

    scenario = Nested(queryset=models.Scenario.objects.all(), serializer=NestedScenarioSerializer)
    agents = Nested(queryset=models.AgentConfig.objects.all(), serializer=AgentConfigSerializer)

"""Simluations page."""

from typing import override

import streamlit as st

from components.orm import GenericORM
from utilities.api import GenericAPI


class Simulations(GenericORM):
    """Simulation ORM."""

    model = 'simulations'
    api = GenericAPI(model)
    mapfiles = None
    defaults = {
        'name': '',
        'mapfile': 'bow_view_manor',
        'xy_scale': 2.77,
        't_step': 5,
        'save_resolution': 12,
        'max_iter': 250,
        'save_verbose': False,
        'terrain': None,
    }

    @override
    @classmethod
    def form(cls, obj_id: int | None = None) -> dict:
        data = {}
        obj = cls._get_defaults(obj_id)

        text = st.columns(2)
        data['name'] = text[0].text_input('Name', value=obj['name'])
        data['mapfile'] = text[1].text_input(
            'Map File / Folder',
            value=obj['mapfile'].replace('data/mapfiles/', ''),
            help='Path to the map file or folder containing the map files. Relative to `backend/data/mapfiles`.',
        )

        numbers = st.columns(4)
        data['xy_scale'] = numbers[0].number_input(
            'XY Scale',
            value=obj['xy_scale'],
            help='Physical map scale in terms of pixels per meter.',
        )
        data['t_step'] = numbers[1].number_input(
            'Time Step',
            value=obj['t_step'],
            min_value=1,
            help='Simulation time step in seconds.',
        )
        data['save_resolution'] = numbers[2].number_input(
            'Save Resolution',
            value=obj['save_resolution'],
            min_value=1,
            help='Number of time steps in each "iteration". Represents how often the simulation data is saved.',
        )
        data['max_iter'] = numbers[3].number_input(
            'Maximum Iterations',
            value=obj['max_iter'],
            min_value=1,
            help='Maximum number of "iterations" to run the simulation.',
        )
        data['save_verbose'] = st.checkbox(
            'Save Verbose',
            value=obj['save_verbose'],
            help='Whether to save the full virus matrix (in addition to agent info) at each time step.',
        )
        terrains = st.multiselect(
            'Terrains',
            GenericAPI('terrains').get().json(),
            default=obj['terrain'],
            format_func=cls._format,
            help='Represents the different surfaces and rooms (e.g. Walls, Doors, Open Spaces, etc.) in the simulation.',
        )
        data['terrain'] = [terrain['id'] for terrain in terrains]

        return data


Simulations.run()

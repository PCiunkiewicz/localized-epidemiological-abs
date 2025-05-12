"""Simluations page."""

import os
from typing import override

import streamlit as st

from components.orm import GenericORM
from utilities.api import GenericAPI


class Simulations(GenericORM):
    """Simulation ORM."""

    model = 'simulations'
    api = GenericAPI(model)

    @override
    @classmethod
    def form(cls) -> dict:
        data = {}
        data['name'] = st.text_input('Name')
        mapfile = st.file_uploader('Map File', type=['png'])
        data['mapfile'] = None
        if mapfile:
            st.image(mapfile)
            path = f'/data/mapfiles/{mapfile.name}'
            if os.path.exists(path):
                st.warning('File already exists, rename and try again')
            else:
                data['mapfile'] = path.lstrip('/')
                with open(path, 'wb') as file:
                    file.write(mapfile.getvalue())
        data['xy_scale'] = st.number_input('XY Scale', value=10.0, min_value=1.0)
        data['t_step'] = st.number_input('Time Step', value=1, min_value=1)
        data['max_iter'] = st.number_input('Max Iterations', value=100, min_value=1)
        data['save_resolution'] = st.number_input('Save Resolution', value=60, min_value=1)
        data['save_verbose'] = st.checkbox('Save Verbose', value=False)
        terrains = st.multiselect('Terrain', GenericAPI('terrains').get().json(), format_func=cls._format)
        data['terrain'] = [terrain['id'] for terrain in terrains]

        return data


Simulations.run()

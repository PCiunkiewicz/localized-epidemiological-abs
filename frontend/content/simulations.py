"""Simluations page."""

import os

import streamlit as st
from components.orm import generic_orm

from utilities.format import id_, options


def _form() -> dict:
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
    terrains = st.multiselect('Terrain', options('terrains'))
    data['terrain'] = [id_(terrain) for terrain in terrains]

    return data


generic_orm(
    'simulations',
    create_form=_form,
    update_form=_form,
)

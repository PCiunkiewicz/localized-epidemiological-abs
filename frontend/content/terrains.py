"""Terrains page."""

from typing import override

import streamlit as st

from components.orm import GenericORM
from utilities.api import GenericAPI


class Terrains(GenericORM):
    """Terrain ORM."""

    model = 'terrains'
    api = GenericAPI(model)

    @override
    @classmethod
    def form(cls) -> dict:
        data = {}
        data['name'] = st.text_input('Name').upper()
        color = st.color_picker('Pick A Color', '#00f900')
        data['value'] = color
        data['color'] = color
        data['material'] = None
        data['walkable'] = st.checkbox('Walkable', value=True)
        data['interactive'] = st.checkbox('Interactive', value=False)
        data['restricted'] = st.checkbox('Restricted', value=False)
        data['access_level'] = st.slider('Access Level', 0, 10, 0)

        return data


Terrains.run()

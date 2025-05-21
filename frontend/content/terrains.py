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
    def form(cls, obj_id: int | None = None) -> dict:
        data = {}

        data['name'] = st.text_input('Name').upper()
        data['material'] = None

        checks = st.columns(5, vertical_alignment='bottom')
        data['walkable'] = checks[0].checkbox('Walkable', value=True)
        data['interactive'] = checks[1].checkbox('Interactive', value=False)
        data['restricted'] = checks[2].checkbox('Restricted', value=False)
        data['value'] = data['color'] = checks[3].color_picker('Color', '#00f900')
        data['access_level'] = checks[4].number_input('Access Level', 0, 10, 0)

        return data


Terrains.run()

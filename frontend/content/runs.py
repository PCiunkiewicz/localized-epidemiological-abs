"""Runs page."""

from typing import override

import streamlit as st

from components.orm import GenericORM, obj_select
from utilities.api import GenericAPI


class Runs(GenericORM):
    """Run ORM."""

    model = 'runs'
    api = GenericAPI(model)
    defaults = {
        'name': '',
        'scenario': None,
        'agents': None,
        'runs': 1,
    }

    @override
    @classmethod
    def form(cls, obj_id: int | None = None) -> dict:
        data = {}
        obj = cls._get_defaults(obj_id)

        data['name'] = st.text_input('Name', value=obj['name'])

        cols = st.columns([0.4, 0.4, 0.2])
        with cols[0]:
            data['scenario'] = obj_select('scenarios', obj['scenario'], label='Scenario')
        with cols[1]:
            data['agents'] = obj_select('agent_configs', obj['agents'], label='Agent Configuration')
        data['runs'] = cols[2].number_input('Runs', min_value=1, max_value=10000, value=obj['runs'])

        return data


Runs.run()

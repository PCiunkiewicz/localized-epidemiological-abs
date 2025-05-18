"""Runs page."""

from typing import override

import streamlit as st

from components.orm import GenericORM
from utilities.api import GenericAPI


class Runs(GenericORM):
    """Scenario ORM."""

    model = 'runs'
    api = GenericAPI(model)

    @override
    @classmethod
    def form(cls) -> dict:
        data = {}
        data['name'] = st.text_input('Name')
        obj = st.selectbox('Scenario', GenericAPI('scenarios').get().json(), format_func=cls._format)
        data['scenario'] = obj.get('id') if isinstance(obj, dict) else obj
        obj = st.selectbox('Agent Config', GenericAPI('agent_configs').get().json(), format_func=cls._format)
        data['agents'] = obj.get('id') if isinstance(obj, dict) else obj
        data['runs'] = st.number_input('Runs', min_value=1, max_value=10000, value=1)

        return data


Runs.run()

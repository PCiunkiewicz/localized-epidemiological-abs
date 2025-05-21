"""Agent Configuration Page."""

from typing import override

import streamlit as st

from components.orm import GenericORM, json_input
from utilities.api import GenericAPI

AGENT_DEFAULT = {
    'info': {
        'mask_type': '',
        'vax_type': '',
        'vax_doses': 0,
        'schedule': {},
        'work_zone': None,
        'start_zone': None,
    },
    'state': {
        'x': 0,
        'y': 0,
        'status': 'UNKNOWN',
    },
}


class AgentConfigs(GenericORM):
    """Agent Configuration ORM."""

    model = 'agent_configs'
    api = GenericAPI(model)
    defaults = {
        'name': '',
        'default': AGENT_DEFAULT,
        'random_agents': 0,
        'random_infected': 0,
        'custom': [],
    }

    @override
    @classmethod
    def form(cls, obj_id: int | None = None) -> dict:
        data = {}
        obj = cls._get_defaults(obj_id)

        cols = st.columns([0.5, 0.25, 0.25])
        data['name'] = cols[0].text_input('Name', value=obj['name'])

        input_kws = {'min_value': 0, 'max_value': 1000}
        data['random_agents'] = cols[1].number_input('Random Agents', value=obj['random_agents'], **input_kws)
        data['random_infected'] = cols[2].number_input('Random Infected', value=obj['random_infected'], **input_kws)

        inputs = st.columns(2, border=True)
        with inputs[0]:
            data['default'] = json_input('Default Agent Configuration', obj['default'], AGENT_DEFAULT)
        with inputs[1]:
            data['custom'] = json_input('Custom Agents', obj['custom'], [])

        return data


AgentConfigs.run()

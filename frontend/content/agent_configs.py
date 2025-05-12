"""Agent Configuration Page."""

import json
from typing import override

import streamlit as st
from streamlit_monaco import st_monaco

from components.orm import GenericORM
from utilities.api import GenericAPI

AGENT_DEFAULT = {
    'info': {},
    'state': {
        'x': 0,
        'y': 0,
        'status': 'UNKNOWN',
    },
}

CUSTOM_DEFAULT = [
    {
        'info': {
            'schedule': {},
            'work_zone': None,
            'start_zone': None,
        },
        'state': {
            'status': 'UNKNOWN',
        },
    },
]


class AgentConfigs(GenericORM):
    """Agent Configuration ORM."""

    model = 'agent_configs'
    api = GenericAPI(model)

    @override
    @classmethod
    def form(cls) -> dict:
        data = {}

        data['name'] = st.text_input('Name')
        st.write('Default Agent Configuration')
        default = st_monaco(value=f'{json.dumps(AGENT_DEFAULT, indent=4)}', language='json')
        try:
            data['default'] = json.loads(default)
        except TypeError:
            data['default'] = AGENT_DEFAULT
        except json.decoder.JSONDecodeError:
            data['default'] = None
            st.warning('Invalid Default Agent Configuration JSON, check your syntax')

        data['random_agents'] = st.number_input('Random Agents', min_value=0, max_value=1000, value=0)
        data['random_infected'] = st.number_input('Random Infected', min_value=0, max_value=1000, value=0)

        st.write('Custom Agent Configuration')
        custom = st_monaco(value=f'{json.dumps(CUSTOM_DEFAULT, indent=4)}', language='json')
        try:
            data['custom'] = json.loads(custom)
            if data['custom'] == CUSTOM_DEFAULT:
                data['custom'] = []
        except TypeError:
            data['custom'] = None
        except json.decoder.JSONDecodeError:
            data['custom'] = None
            st.warning('Invalid Custom Agent Configuration JSON, check your syntax')

        return data


AgentConfigs.run()

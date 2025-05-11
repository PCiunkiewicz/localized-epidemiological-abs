"""Agent Configuration Page."""

import json

import streamlit as st
from components.orm import generic_orm
from streamlit_monaco import st_monaco

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


def _form() -> dict:
    data = {}

    data['name'] = st.text_input('Name')
    st.write('Default Agent Configuration')
    default = st_monaco(
        value=f'{json.dumps(AGENT_DEFAULT, indent=4)}',
        language='json',
        theme='vs-dark',
        height='400px',
    )
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
    custom = st_monaco(
        value=f'{json.dumps(CUSTOM_DEFAULT, indent=4)}',
        language='json',
        theme='vs-dark',
        height='400px',
    )
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


generic_orm(
    'agent_configs',
    create_form=_form,
    update_form=_form,
)

"""Scenarios page."""

import json

import streamlit as st
from components.orm import generic_orm
from streamlit_monaco import st_monaco

from utilities.format import id_, options

PREVENTION_DEFAULT = {'mask': {}, 'vax': {}}


def _form() -> dict:
    data = {}
    data['name'] = st.text_input('Name')
    data['sim'] = id_(st.selectbox('Simulation', options('simulations')))
    data['virus'] = id_(st.selectbox('Virus', options('viruses')))
    st.write('Prevention')
    prevention = st_monaco(
        value=f'{json.dumps(PREVENTION_DEFAULT, indent=4)}',
        language='json',
        theme='vs-dark',
        height='400px',
    )
    try:
        data['prevention'] = json.loads(prevention)
    except TypeError:
        data['prevention'] = PREVENTION_DEFAULT
    except json.decoder.JSONDecodeError:
        data['prevention'] = None
        st.warning('Invalid Prevention JSON, check your syntax')

    return data


generic_orm(
    'scenarios',
    create_form=_form,
    update_form=_form,
)

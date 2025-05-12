"""Scenarios page."""

import json
from typing import override

import streamlit as st
from streamlit_monaco import st_monaco

from components.orm import GenericORM
from utilities.api import GenericAPI

PREVENTION_DEFAULT = {'mask': {}, 'vax': {}}


class Scenarios(GenericORM):
    """Scenario ORM."""

    model = 'scenarios'
    api = GenericAPI(model)

    @override
    @classmethod
    def form(cls) -> dict:
        data = {}
        data['name'] = st.text_input('Name')
        obj = st.selectbox('Simulation', GenericAPI('simulations').get().json(), format_func=cls._format)
        data['sim'] = obj.get('id') if isinstance(obj, dict) else obj
        obj = st.selectbox('Virus', GenericAPI('viruses').get().json(), format_func=cls._format)
        data['virus'] = obj.get('id') if isinstance(obj, dict) else obj
        st.write('Prevention')
        prevention = st_monaco(value=f'{json.dumps(PREVENTION_DEFAULT, indent=4)}', language='json')
        try:
            data['prevention'] = json.loads(prevention)
        except TypeError:
            data['prevention'] = PREVENTION_DEFAULT
        except json.decoder.JSONDecodeError:
            data['prevention'] = None
            st.warning('Invalid Prevention JSON, check your syntax')

        return data


Scenarios.run()

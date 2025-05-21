"""Scenarios page."""

from typing import override

import streamlit as st

from components.orm import GenericORM, obj_select
from utilities.api import GenericAPI

PREVENTION_DEFAULT = {'mask': {}, 'vax': {}}


class Scenarios(GenericORM):
    """Scenario ORM."""

    model = 'scenarios'
    api = GenericAPI(model)
    defaults = {
        'name': '',
        'sim': None,
        'virus': None,
        'prevention': PREVENTION_DEFAULT,
    }

    @override
    @classmethod
    def form(cls, obj_id: int | None = None) -> dict:
        data = {}
        obj = cls._get_defaults(obj_id)

        data['name'] = st.text_input('Name', value=obj['name'])

        selects = st.columns(3)
        with selects[0]:
            data['sim'] = obj_select('simulations', obj['sim'], label='Simulation')
        with selects[1]:
            data['virus'] = obj_select('viruses', obj['virus'], label='Virus')
        with selects[2]:
            data['prevention'] = obj_select('preventions', obj['prevention'], label='Prevention')

        return data


Scenarios.run()

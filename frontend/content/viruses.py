"""Viruses page."""

from typing import override

import streamlit as st

from components.orm import GenericORM
from utilities.api import GenericAPI


class Viruses(GenericORM):
    """Virus ORM."""

    model = 'viruses'
    api = GenericAPI(model)
    defaults = {
        'name': '',
        'attack_rate': 0.07,
        'infection_rate': 0.021,
        'fatality_rate': 0.01,
    }

    @override
    @classmethod
    def form(cls, obj_id: int | None = None) -> dict:
        data = {}
        obj = cls._get_defaults(obj_id)

        data['name'] = st.text_input('Name', value=obj['name'])
        slider_kws = {'min_value': 0.0, 'max_value': 1.0, 'step': 0.001}
        data['attack_rate'] = st.slider('Attack Rate', value=obj['attack_rate'], **slider_kws)
        data['infection_rate'] = st.slider('Infection Rate', value=obj['infection_rate'], **slider_kws)
        data['fatality_rate'] = st.slider('Fatality Rate', value=obj['fatality_rate'], **slider_kws)

        return data


Viruses.run()

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

        numbers = st.columns(3)
        number_kws = {'min_value': 0.0, 'max_value': 1.0, 'step': 0.001, 'format': '%0.3f'}
        data['attack_rate'] = numbers[0].number_input('Attack Rate', value=obj['attack_rate'], **number_kws)
        data['infection_rate'] = numbers[1].number_input('Infection Rate', value=obj['infection_rate'], **number_kws)
        data['fatality_rate'] = numbers[2].number_input('Fatality Rate', value=obj['fatality_rate'], **number_kws)

        return data


Viruses.run()

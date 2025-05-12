"""Viruses page."""

from typing import override

import streamlit as st

from components.orm import GenericORM
from utilities.api import GenericAPI


class Viruses(GenericORM):
    """virus ORM."""

    model = 'viruses'
    api = GenericAPI(model)

    @override
    @classmethod
    def form(cls) -> dict:
        data = {}
        data['name'] = st.text_input('Name')
        data['attack_rate'] = st.slider('Attack Rate', min_value=0.0, max_value=1.0, value=0.07, step=0.001)
        data['infection_rate'] = st.slider('Infection Rate', min_value=0.0, max_value=1.0, value=0.021, step=0.001)
        data['fatality_rate'] = st.slider('Fatality Rate', min_value=0.0, max_value=1.0, value=0.01, step=0.001)

        return data


Viruses.run()

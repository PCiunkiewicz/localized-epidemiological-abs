"""
ML Framework Interface for Datasets
"""
# pylint: disable=invalid-name
import streamlit as st

from components.orm import generic_orm
from components.sidebar import default_sidebar

st.set_page_config(page_title='Viruses', page_icon='static/neural.png')


def main():
    """
    TODO: Write docstring
    """
    def _form():
        data = {}
        data['name'] = st.text_input('Name')
        data['attack_rate'] = st.slider('Attack Rate', min_value=0.0, max_value=1.0, value=0.07, step=0.001)
        data['infection_rate'] = st.slider('Infection Rate', min_value=0.0, max_value=1.0, value=0.021, step=0.001)
        data['fatality_rate'] = st.slider('Fatality Rate', min_value=0.0, max_value=1.0, value=0.01, step=0.001)

        return data

    generic_orm(
        'viruses',
        create_form=_form,
        update_form=_form,
    )


default_sidebar()
main()

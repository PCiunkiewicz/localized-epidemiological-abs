"""
ML Framework Interface for Datasets
"""
# pylint: disable=invalid-name
import streamlit as st

from components.orm import generic_orm
from components.sidebar import default_sidebar

st.set_page_config(page_title='Terrains', page_icon='static/neural.png')


def main():
    """
    TODO: Write docstring
    """
    def _form():
        data = {}
        data['name'] = st.text_input('Name').upper()
        color = st.color_picker('Pick A Color', '#00f900')
        data['value'] = color
        data['color'] = color
        data['material'] = None
        data['walkable'] = st.checkbox('Walkable', value=True)
        data['interactive'] = st.checkbox('Interactive', value=False)
        data['restricted'] = st.checkbox('Restricted', value=False)
        data['access_level'] = st.slider('Access Level', 0, 10, 0)

        return data

    generic_orm(
        'terrains',
        create_form=_form,
        update_form=_form,
    )


default_sidebar()
main()

"""
ML Framework Interface for Runs
"""

# pylint: disable=invalid-name
import streamlit as st

from components.sidebar import default_sidebar

st.set_page_config(page_title='Runs', page_icon='static/neural.png')


def main():
    """
    TODO: Write docstring
    """
    st.header('Runs')

    st.info('To Do')


default_sidebar()
main()

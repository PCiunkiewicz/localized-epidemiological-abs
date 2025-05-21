"""Admin page."""

import streamlit as st

from utilities.api import GenericAPI

st.header('Admin Panel')


@st.dialog('Reset local database')
def _reset_db() -> None:
    st.write('This action cannot be undone. Are you sure you want to reset the database?')
    col1, col2 = st.columns([0.2, 0.8], vertical_alignment='bottom')
    if col1.button('Cancel'):
        st.rerun()
    if col2.button('Confirm', type='primary'):
        response = GenericAPI('admin/resetdb').get()
        st.write(f'`GET {response.url}`', response, response.json())


if st.button('Reset DB', type='primary'):
    _reset_db()

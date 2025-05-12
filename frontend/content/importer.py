"""Importer page."""

from pathlib import Path

import streamlit as st

from utilities.api import GenericAPI

with st.form('Import Config'):
    data = {}

    def _format(path: str) -> str:
        """Format the path for display."""
        return Path(path).name

    data['config_path'] = st.selectbox('Config File', GenericAPI('importer/configs').get().json(), format_func=_format)
    data['exist_ok'] = st.checkbox('Ignore Existing', value=True)

    if st.form_submit_button('POST'):
        response = GenericAPI('importer/import').post(data)
        st.write(f'`POST {response.url}`', response, response.json())

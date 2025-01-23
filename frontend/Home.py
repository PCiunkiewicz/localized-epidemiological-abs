"""
Home page for the Streamlit app
"""

# pylint: disable=invalid-name
import streamlit as st
from components.sidebar import default_sidebar

st.set_page_config(page_title='Home', page_icon='static/neural.png')


default_sidebar()

st.write('# LocABS Interface')

st.markdown(
    # pylint: disable=line-too-long
    """
        User interface for interacting with the Localized Agent-Based Simulation (LocABS) framework.
        The LocABS framework is a collection of tools for simulating and visualizing agent-based models
        of localized epidemiological interactions. The framework is designed to be modular and extensible, allowing
        for the integration of new models and data sources. The framework is built using a combination of
        Python, Streamlit, and Dask for parallel processing.
    """
)

st.image('static/models.drawio.png', use_column_width=True)

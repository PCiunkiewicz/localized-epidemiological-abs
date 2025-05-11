"""Home page for the Streamlit app."""

import streamlit as st

st.write('# LocABS Interface')

st.markdown(
    """
        User interface for interacting with the Localized Agent-Based Simulation (LocABS) framework.
        The LocABS framework is a collection of tools for simulating and visualizing agent-based models
        of localized epidemiological interactions. The framework is designed to be modular and extensible, allowing
        for the integration of new models and data sources. The framework is built using a combination of
        Python, Streamlit, and Dask for parallel processing.
    """
)

st.image('static/components.png', use_container_width=True)

st.image('static/architecture.png', use_container_width=True)

"""Main streamlit app."""

import streamlit as st

from components.sidebar import default_sidebar

home_page = st.Page('content/home.py', title='Home')
terrains_page = st.Page('content/terrains.py', title='Terrains')
simulations_page = st.Page('content/simulations.py', title='Simulations')
viruses_page = st.Page('content/viruses.py', title='Viruses')
scenarios_page = st.Page('content/scenarios.py', title='Scenarios')
agent_configs_page = st.Page('content/agent_configs.py', title='Agent Configs')
runs_page = st.Page('content/runs.py', title='Runs')
importer_page = st.Page('content/importer.py', title='Importer')
admin_page = st.Page('content/admin.py', title='Admin')

pg = st.navigation(
    pages=[
        home_page,
        terrains_page,
        simulations_page,
        viruses_page,
        scenarios_page,
        agent_configs_page,
        runs_page,
        importer_page,
        admin_page,
    ],
)

default_sidebar()
pg.run()

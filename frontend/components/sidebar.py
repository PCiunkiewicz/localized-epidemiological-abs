"""Sidebar components for all pages."""

import streamlit as st


def default_sidebar() -> None:
    """Default sidebar elements for all pages."""
    st.sidebar.image('static/btlab_logo.svg', use_container_width=True)
    st.sidebar.write('Welcome to LocABS')
    st.sidebar.divider()

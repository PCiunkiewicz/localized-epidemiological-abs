"""
ML Framework Interface for Datasets
"""

# pylint: disable=invalid-name
import json

import streamlit as st
from streamlit_monaco import st_monaco


from components.orm import generic_orm
from components.sidebar import default_sidebar
from lib.utils import options, id_

st.set_page_config(page_title='Scenarios', page_icon='static/neural.png')

PREVENTION_DEFAULT = {'mask': {}, 'vax': {}}


def main():
    """
    TODO: Write docstring
    """

    def _form():
        data = {}
        data['name'] = st.text_input('Name')
        data['sim'] = id_(st.selectbox('Simulation', options('simulations')))
        data['virus'] = id_(st.selectbox('Virus', options('viruses')))
        st.write('Prevention')
        prevention = st_monaco(
            value=f'{json.dumps(PREVENTION_DEFAULT, indent=4)}',
            language='json',
            theme='vs-dark',
            height='400px',
        )
        try:
            data['prevention'] = json.loads(prevention)
        except TypeError:
            data['prevention'] = PREVENTION_DEFAULT
        except json.decoder.JSONDecodeError:
            data['prevention'] = None
            st.warning('Invalid Prevention JSON, check your syntax')

        return data

    generic_orm(
        'scenarios',
        create_form=_form,
        update_form=_form,
    )


default_sidebar()
main()

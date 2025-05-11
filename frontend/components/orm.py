"""Generic ORM operation interface."""

import streamlit as st

from utilities import api
from utilities.format import id_, options


def generic_orm(model, create_form=None, update_form=None, header=None) -> None:
    """Generic ORM operation interface."""
    st.header(header or model.capitalize())
    if st.button('Refresh'):
        st.cache_data.clear()
    _create, _retrieve, _update, _delete = st.tabs(['Create', 'Retrieve', 'Update', 'Delete'])

    with _create:
        generic_create(model, create_form)

    with _retrieve:
        generic_retrieve(model)

    with _update:
        generic_update(model, update_form)

    with _delete:
        generic_delete(model)


def generic_create(model, form=None) -> None:
    """Generic ORM create operation."""
    with st.form(f'{model}_create'):
        data = {}
        if form:
            data = form()
        submit = st.form_submit_button('POST')

    if submit:
        response = api.post_obj(model, data)
        st.write(f'`POST {response.url}`', response, response.json())


def generic_retrieve(model, label='name') -> None:
    """Generic ORM retrieve operation."""
    with st.form(f'{model}_retrieve'):
        obj_id = id_(st.selectbox(f'{model.capitalize()} ID', options(model, label)))
        submit = st.form_submit_button('GET')

    if submit:
        response = api.get_obj(model, obj_id)
        st.write(f'`GET {response.url}`', response, response.json())


def generic_update(model, form=None) -> None:
    """Generic ORM update operation."""
    with st.form(f'{model}_update'):
        obj_id = id_(st.selectbox(f'{model.capitalize()} ID', options(model)))

        data = {}
        if form:
            data = form()
        submit = st.form_submit_button('PATCH')

    if submit:
        if obj_id:
            data = {k: v for k, v in data.items() if v}
            response = api.patch_obj(model, obj_id, data)
            st.write(f'`PATCH {response.url}`', response, response.json())
        else:
            st.warning('Please select an ID to update')


def generic_delete(model, label='name') -> None:
    """Generic ORM delete operation."""
    with st.form(f'{model}_delete'):
        obj_id = id_(st.selectbox(f'{model.capitalize()} ID', options(model, label)))
        submit = st.form_submit_button('DELETE')

    if submit:
        if obj_id:
            response = api.delete_obj(model, obj_id)
            st.write(f'`DELETE {response.url}`', response)
        else:
            st.warning('Please select an ID to delete')

"""Generic ORM operation interface."""

import json
from abc import ABC, abstractmethod

import requests
import streamlit as st
from streamlit_monaco import st_monaco

from utilities.api import GenericAPI


class GenericORM(ABC):
    """Generic ORM class for handling backend requests.

    Attributes:
        model: Model name for the ORM.
        form: Callable to generate the streamlit form elements.
        api: API object for making requests.
    """

    model: str
    api: GenericAPI
    defaults: dict

    @classmethod
    @abstractmethod
    def form(cls, obj_id: int | None = None) -> dict:
        """Generate the streamlit form elements for the model."""
        pass

    @classmethod
    def run(cls) -> None:
        """Generic ORM operation interface."""
        header, refresh = st.columns([0.8, 0.2])
        header.header(cls.model.capitalize())
        if refresh.button('Refresh'):
            st.cache_data.clear()

        create, retrieve, update, delete = st.tabs(['Create', 'Retrieve', 'Update', 'Delete'])

        with create:
            cls.create()
        with retrieve:
            cls.retrieve()
        with update:
            cls.update()
        with delete:
            cls.delete()

    @classmethod
    def create(cls) -> None:
        """Generic ORM create operation."""
        with st.form(f'{cls.model}_create'):
            data = cls.form()
            if st.form_submit_button('Create'):
                response = cls.api.post(data)
                cls._write_response(response)

    @classmethod
    def retrieve(cls) -> None:
        """Generic ORM retrieve operation."""
        with st.form(f'{cls.model}_retrieve'):
            obj = st.selectbox(cls.model.capitalize(), cls.api.get().json(), format_func=cls._format)
            obj_id = obj.get('id') if isinstance(obj, dict) else obj
            if st.form_submit_button('Retrieve', disabled=not obj_id):
                response = cls.api.get(obj_id)
                cls._write_response(response)

    @classmethod
    def update(cls) -> None:
        """Generic ORM update operation."""
        obj = st.selectbox(cls.model.capitalize(), cls.api.get().json(), format_func=cls._format)
        obj_id = obj.get('id') if isinstance(obj, dict) else obj
        with st.form(f'{cls.model}_update'):
            data = cls.form(obj_id)

            patch, copy = st.columns([0.2, 0.8])
            if patch.form_submit_button('Update', disabled=not obj_id):
                response = cls.api.patch(obj_id, data)
                st.write(f'`PATCH {response.url}`', response, response.json())
            elif copy.form_submit_button('Copy', disabled=not obj_id):
                response = cls.api.post(data)
                cls._write_response(response)

    @classmethod
    def delete(cls) -> None:
        """Generic ORM delete operation."""
        with st.form(f'{cls.model}_delete'):
            obj = st.selectbox(cls.model.capitalize(), cls.api.get().json(), format_func=cls._format)
            obj_id = obj.get('id') if isinstance(obj, dict) else obj
            if st.form_submit_button('Delete', disabled=not obj_id):
                response = cls.api.delete(obj_id)
                cls._write_response(response)

    @classmethod
    def _write_response(cls, response: requests.Response) -> None:
        """Format and write the response to the streamlit app."""
        match response.request.method:
            case 'POST':
                msg = f'Creating new "{cls.model.capitalize()}" entry'
            case 'GET':
                msg = f'Retrieving "{cls.model.capitalize()}" entry'
            case 'PATCH':
                msg = f'Updating "{cls.model.capitalize()}" entry'
            case 'DELETE':
                msg = f'Deleting "{cls.model.capitalize()}" entry'

        st.divider()
        result = ':green[Success]' if response.ok else ':red[Failed]'
        st.write(f'{msg} - **{result}**')
        st.write(f'`{response.request.method} {response.url} -> [{response.status_code}] {response.reason}`')
        st.json(response.json(), expanded=1 if response.ok else 2)

    @staticmethod
    def _format(obj: dict) -> str:
        """Format the object for display in the selectbox."""
        return f'{obj["id"]} - {obj["name"]}'

    @classmethod
    def _get_defaults(cls, obj_id: int | None = None) -> dict:
        """Get the default values for the model, replacing foreign objects with keys."""
        obj = cls.api.get(obj_id).json() if obj_id is not None else cls.defaults
        for key, value in obj.items():
            if isinstance(value, dict) and 'id' in value:
                obj[key] = value['id']
        return obj


def obj_select(model: str, obj_id: int | None = None, label: str = '') -> int | None:
    """Select a foreign key object from the API.

    Args:
        model: Model name for the ORM.
        obj_id: The ID of the selected object.
        label: The label for the selectbox.

    Returns:
        The selected objects ID or None if not selected.
    """
    objs = GenericAPI(model).get().json()
    idx = next((i for i, obj in enumerate(objs) if obj['id'] == obj_id), None)
    obj = st.selectbox(label or model.capitalize(), objs, format_func=GenericORM._format, index=idx)
    return obj.get('id') if isinstance(obj, dict) else obj


def json_input(label: str, value: dict | list, default: dict) -> dict | list | None:
    """Input a JSON object in a monaco editor.

    Args:
        label: The label for the input.
        value: The default value for the input.
        default: The default value to return if the input is invalid.

    Returns:
        The JSON object or None if the input is invalid.
    """
    label = label.capitalize()
    st.write(label)
    data = st_monaco(value=f'{json.dumps(value, indent=4)}', language='json', height=300)
    try:
        return json.loads(data)
    except TypeError:
        return default
    except json.decoder.JSONDecodeError:
        st.warning(f'Invalid {label} JSON, check your syntax')
        return None

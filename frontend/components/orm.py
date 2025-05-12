"""Generic ORM operation interface."""

from abc import ABC, abstractmethod

import streamlit as st

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

    @classmethod
    @abstractmethod
    def form(cls) -> dict:
        """Generate the streamlit form elements for the model."""
        pass

    @classmethod
    def run(cls) -> None:
        """Generic ORM operation interface."""
        st.header(cls.model.capitalize())
        if st.button('Refresh'):
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
            if st.form_submit_button('POST'):
                response = cls.api.post(data)
                st.write(f'`POST {response.url}`', response, response.json())

    @classmethod
    def retrieve(cls) -> None:
        """Generic ORM retrieve operation."""
        with st.form(f'{cls.model}_retrieve'):
            obj = st.selectbox(cls.model.capitalize(), cls.api.get().json(), format_func=cls._format)
            obj_id = obj.get('id') if isinstance(obj, dict) else obj
            if st.form_submit_button('GET', disabled=not obj_id):
                response = cls.api.get(obj_id)
                st.write(f'`GET {response.url}`', response, response.json())

    @classmethod
    def update(cls) -> None:
        """Generic ORM update operation."""
        with st.form(f'{cls.model}_update'):
            obj = st.selectbox(cls.model.capitalize(), cls.api.get().json(), format_func=cls._format)
            obj_id = obj.get('id') if isinstance(obj, dict) else obj
            data = cls.form()
            if st.form_submit_button('PATCH', disabled=not obj_id):
                data = {k: v for k, v in data.items() if v}
                response = cls.api.patch(obj_id, data)
                st.write(f'`PATCH {response.url}`', response, response.json())

    @classmethod
    def delete(cls) -> None:
        """Generic ORM delete operation."""
        with st.form(f'{cls.model}_delete'):
            obj = st.selectbox(cls.model.capitalize(), cls.api.get().json(), format_func=cls._format)
            obj_id = obj.get('id') if isinstance(obj, dict) else obj
            if st.form_submit_button('DELETE', disabled=not obj_id):
                response = cls.api.delete(obj_id)
                st.write(f'`DELETE {response.url}`', response)

    @staticmethod
    def _format(obj: dict) -> str:
        return f'{obj["id"]} - {obj["name"]}'

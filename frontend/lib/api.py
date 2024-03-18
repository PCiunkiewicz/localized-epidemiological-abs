"""
API requests for trudata-gpt api.
"""
import requests
import streamlit as st

URL = 'http://api:8000/api/v1'


def post_obj(model, data):
    """
    Generic ORM POST request.
    """
    endpoint = f'{URL}/{model}/'
    return requests.post(
        endpoint,
        timeout=10,
        json=data,
    )


@st.cache_data(ttl=60)
def get_obj(model, obj_id=None):
    """
    Generic ORM GET request.
    """
    endpoint = f'{URL}/{model}' if obj_id is None else f'{URL}/{model}/{obj_id}'
    return requests.get(
        endpoint,
        timeout=10,
    )


def patch_obj(model, obj_id, data):
    """
    Generic ORM PATCH request.
    """
    endpoint = f'{URL}/{model}/{obj_id}/'
    return requests.patch(
        endpoint,
        timeout=10,
        json=data,
    )


def delete_obj(model, obj_id):
    """
    Generic ORM DELETE request.
    """
    endpoint = f'{URL}/{model}/{obj_id}/'
    return requests.delete(
        endpoint,
        timeout=10,
    )

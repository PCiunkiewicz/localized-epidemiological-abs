"""Preventions page."""

from typing import override

import streamlit as st

from components.orm import GenericORM, json_input
from utilities.api import GenericAPI

MASK_DEFAULT = {
    'N95': 0.85,
    'NONE': 0,
    'CLOTH': 0.3,
    'SURGICAL': 0.5,
}
VAX_DEFAULT = {
    'MRNA': [0, 0.31, 0.88],
    'ASTRA': [0, 0.31, 0.67],
}


class Preventions(GenericORM):
    """Prevention ORM."""

    model = 'preventions'
    api = GenericAPI(model)
    defaults = {
        'name': '',
        'vax': VAX_DEFAULT,
        'mask': MASK_DEFAULT,
    }

    @override
    @classmethod
    def form(cls, obj_id: int | None = None) -> dict:
        data = {}
        obj = cls._get_defaults(obj_id)

        data['name'] = st.text_input('Name', value=obj['name'])
        data['mask'] = json_input('Mask', value=obj['mask'], default=MASK_DEFAULT)
        data['vax'] = json_input('Vaccine', value=obj['vax'], default=VAX_DEFAULT)

        return data


Preventions.run()

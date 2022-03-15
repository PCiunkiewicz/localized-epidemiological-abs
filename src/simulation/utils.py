"""
The `utils` module contains utility classes
and functions which do not fit in elsewhere.
"""

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

        for key, val in self.items():
            if isinstance(val, dict):
                self[key] = AttrDict(val)

"""API requests for loc-abs backend."""

import requests


class GenericAPI:
    """Generic API class for handling backend requests.

    Attributes:
        base_url: Base URL for the API.
        endpoint: Specific target endpoint.
        session: Session object for making requests.
    """

    base_url: str = 'http://api:8000/api/v1'

    def __init__(self, endpoint: str = '') -> None:
        """Initialize the GenericAPI class with optional endpoint and session."""
        self.url = f'{self.base_url}/{endpoint}' if endpoint else self.base_url
        self.session = requests.Session()

    def post(self, data: dict) -> requests.Response:
        """Generic API POST request."""
        return self.session.post(
            f'{self.url}/',
            timeout=10,
            json=data,
        )

    def get(self, obj_id: int | None = None) -> requests.Response:
        """Generic API GET request."""
        return self.session.get(
            self.url if obj_id is None else f'{self.url}/{obj_id}',
            timeout=10,
        )

    def patch(self, obj_id: int, data: dict) -> requests.Response:
        """Generic API PATCH request."""
        return self.session.patch(
            f'{self.url}/{obj_id}/',
            timeout=10,
            json=data,
        )

    def delete(self, obj_id: int) -> requests.Response:
        """Generic API DELETE request."""
        return self.session.delete(
            f'{self.url}/{obj_id}/',
            timeout=10,
        )

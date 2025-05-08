"""Socket handler for zmq publishers and subscribers."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import numpy as np
import zmq


class SocketHandler(ABC):
    """SocketHandler class for sending and receiving data over ZMQ sockets."""

    context: zmq.Context
    socket: zmq.SyncSocket

    def __init__(self) -> None:
        """Initialize the publisher with a ZMQ context."""
        self.context = zmq.Context()
        self.socket = None

    def send_string(self, data: str, *args, **kwargs) -> None:
        """Send a string over the socket."""
        self.socket.send_string(data, *args, **kwargs)

    def recv_string(self, *args, **kwargs) -> str:
        """Receive a string from the socket."""
        return self.socket.recv_string(*args, **kwargs)

    def send_pyobj(self, data: Any, *args, **kwargs) -> None:
        """Send a Python object over the socket."""
        self.socket.send_pyobj(data, *args, **kwargs)

    def recv_pyobj(self, *args, **kwargs) -> Any:
        """Receive a Python object from the socket."""
        return self.socket.recv_pyobj(*args, **kwargs)

    def send_array(self, data: np.typing.NDArray) -> None:
        """Send a numpy array with metadata."""
        metadata = {'dtype': str(data.dtype), 'shape': data.shape}
        self.socket.send_json(metadata, 0 | zmq.SNDMORE)
        self.socket.send(data)

    def recv_array(self) -> np.typing.NDArray:
        """Reconstruct a numpy array from buffer and metadata."""
        metadata = self.socket.recv_json()
        msg = self.socket.recv()
        buffer = memoryview(msg)
        data = np.frombuffer(buffer, dtype=metadata['dtype'])
        return data.reshape(metadata['shape'])

    @contextmanager
    def sync_socket(self, socket_type: int, port: int = 5556) -> Generator:
        """Create a ZMQ sync socket."""
        self.socket = self.context.socket(socket_type)
        self.configure_socket(port)
        try:
            yield
        finally:
            self.socket.close()

    @abstractmethod
    def configure_socket(self, port: int) -> None:
        """Configure socket options."""
        pass

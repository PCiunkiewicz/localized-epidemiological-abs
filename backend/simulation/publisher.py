"""Message queue publisher for zmq subscribers for transmitting simulation data."""

import time
from multiprocessing import Queue
from multiprocessing.synchronize import Event

import numpy as np
import zmq


def send_array(socket: zmq.SyncSocket, data: np.typing.NDArray) -> None:
    """Send a numpy array with metadata.

    Args:
        socket: ZMQ socket to send data.
        data: Numpy array to send.
    """
    metadata = {'dtype': str(data.dtype), 'shape': data.shape}
    socket.send_json(metadata, 0 | zmq.SNDMORE)
    socket.send(data)


def recv_array(socket: zmq.SyncSocket) -> np.typing.NDArray:
    """Receive a numpy array.

    Args:
        socket: ZMQ socket to receive data.

    Returns:
        data: Reconstructed numpy array.
    """
    metadata = socket.recv_json()
    msg = socket.recv()
    buffer = memoryview(msg)
    data = np.frombuffer(buffer, dtype=metadata['dtype'])
    return data.reshape(metadata['shape'])


def publisher(queue: Queue, event: Event, port: int) -> None:
    """General publisher for zmq subscribers.

    Args:
        queue: Public queue for sending data to zmq publisher.
        event: Stop event for terminating publisher.
        port: ZMQ port accessed by subscribers.
    """
    context = zmq.Context()
    with context.socket(zmq.PUB) as socket:
        socket.bind(f'tcp://*:{port}')
        socket.setsockopt(zmq.SNDHWM, 0)
        while not event.is_set():
            while not queue.empty():
                data = queue.get()  # Should be a dictionary {'topic': topic, 'data': data}
                socket.send_string(data['topic'], zmq.SNDMORE)
                if isinstance(data['data'], np.ndarray):
                    send_array(socket, data['data'])
                else:
                    socket.send_pyobj(data['data'])
            time.sleep(0.001)  # Sleeps 1 milliseconds to be polite with the CPU
        time.sleep(1)

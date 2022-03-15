"""
The `publisher` module contains code for sending and
receiving messages using message queueing with `zmq`.
Special functions have been written for direct handling
of numpy arrays without pickling the Python objects.
"""

import time

import zmq
import numpy as np


def send_array(socket, A, flags=0, copy=True, track=False):
    """Send a numpy array with metadata.
    """
    metadata = {
        'dtype': str(A.dtype),
        'shape': A.shape
    }
    socket.send_json(metadata, flags|zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)


def recv_array(socket, flags=0, copy=True, track=False):
    """Receive a numpy array.
    """
    metadata = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buffer = memoryview(msg)
    A = np.frombuffer(buffer, dtype=metadata['dtype'])
    return A.reshape(metadata['shape'])


def publisher(queue, event, port):
    """General publisher for zmq subscribers.

    Parameters
    ----------
    queue : multiprocessing.Queue
        Public queue for sending data to zmq publisher.
    event : multiprocessing.Event
        Stop event for terminating publisher.
    port : int
        ZMQ port accessed by subscribers.
    """
    context = zmq.Context()
    with context.socket(zmq.PUB) as socket:
        socket.bind(f"tcp://*:{port}")
        socket.setsockopt(zmq.SNDHWM, 0)
        while not event.is_set():
            while not queue.empty():
                data = queue.get()  # Should be a dictionary {'topic': topic, 'data': data}
                socket.send_string(data['topic'], zmq.SNDMORE)
                if isinstance(data['data'], np.ndarray):
                    send_array(socket, data['data'])
                else:
                    socket.send_pyobj(data['data'])
            # time.sleep(0.001)  # Sleeps 1 milliseconds to be polite with the CPU
        time.sleep(1)

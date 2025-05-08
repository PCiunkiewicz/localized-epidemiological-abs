"""Message queue publisher for zmq subscribers for transmitting simulation data."""

import time
from multiprocessing import Queue
from multiprocessing.synchronize import Event
from typing import override

import numpy as np
import zmq

from utilities.socket import SocketHandler


class Publisher(SocketHandler):
    """Publisher class for sending simulation data."""

    def publish(self, queue: Queue, event: Event, port: int = 5556) -> None:
        """General publisher for zmq subscribers.

        Args:
            queue: Public queue for sending data to zmq publisher.
            event: Stop event for terminating publisher.
            port: ZMQ port accessed by subscribers.
        """
        with self.sync_socket(zmq.PUB, port):
            while not event.is_set():
                while not queue.empty():
                    data = queue.get()
                    self.send_string(data['topic'], zmq.SNDMORE)
                    if isinstance(data['data'], np.ndarray):
                        self.send_array(data['data'])
                    else:
                        self.send_pyobj(data['data'])
                time.sleep(0.001)  # Sleeps 1 milliseconds to be polite with the CPU
            time.sleep(1)

    @override
    def configure_socket(self, port: int) -> None:
        self.socket.setsockopt(zmq.SNDHWM, 0)
        self.socket.bind(f'tcp://*:{port}')

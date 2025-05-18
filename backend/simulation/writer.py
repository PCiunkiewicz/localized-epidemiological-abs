"""Results writer subscribing to zmq publisher and writing data to hdf5 file."""

from pathlib import Path
from threading import Event
from typing import override

import numpy as np
import tables as tb
import zmq

from utilities.socket import SocketHandler


class AgentInfo(tb.IsDescription):
    """Agent info table description."""

    age = tb.Int8Col()
    sex = tb.StringCol(1)
    long_covid = tb.BoolCol()
    prevention_index = tb.Float16Col()
    mask = tb.StringCol(10)
    vax = tb.StringCol(10)
    infected = tb.BoolCol()
    hospitalized = tb.BoolCol()
    deceased = tb.BoolCol()
    capacity = tb.Int16Col()


class Writer(SocketHandler):
    """Writer class for receiving data over ZMQ sockets."""

    file: tb.File
    expectedrows: int

    def __init__(self, filename: Path, expectedrows: int = 1000) -> None:
        """Initialize the writer with a hdf5 file."""
        super().__init__()
        self.file = tb.open_file(filename, mode='w')
        self.expectedrows = expectedrows

    def write(self, terminate: Event, port: int = 5556) -> None:
        """Function for writing data to file. Required to support saving virus topics.

        Args:
            terminate: Stop event for terminating writer.
            port: ZMQ port accessed by publisher.
        """
        with self.sync_socket(zmq.SUB, port):
            while not terminate.is_set():
                topic = self.recv_string()
                if topic in ['agents', 'virus']:
                    data = self.recv_array().astype(np.int16)
                    self._append(topic, data)
                else:
                    data = self.recv_pyobj()
                    if topic == 'timesteps':
                        self._append(topic, np.array(data))
                    elif topic == 'agent_info':
                        table = self.file.create_table(self.file.root, 'agent_info', AgentInfo)
                        agent_info = table.row
                        for agent in data:
                            for key, value in agent.items():
                                agent_info[key] = value
                            agent_info.append()
                        break

        self.file.close()

    def _append(self, topic: str, data: np.typing.NDArray) -> None:
        """Append data to EArray, creating array if required."""
        data = np.expand_dims(data, axis=(0))
        if topic not in self.file.root:
            self.file.create_earray(
                self.file.root,
                name=topic,
                obj=data,
                expectedrows=self.expectedrows,
                filters=tb.Filters(complevel=9, complib='blosc2'),
            )

        self.file.root[topic].append(data)

    @override
    def configure_socket(self, port: int) -> None:
        self.socket.connect(f'tcp://localhost:{port}')
        self.socket.setsockopt(zmq.RCVHWM, 0)
        self.socket.setsockopt(zmq.SUBSCRIBE, b'agents')
        self.socket.setsockopt(zmq.SUBSCRIBE, b'agent_info')
        self.socket.setsockopt(zmq.SUBSCRIBE, b'virus')
        self.socket.setsockopt(zmq.SUBSCRIBE, b'timesteps')

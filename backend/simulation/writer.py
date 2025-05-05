"""Results writer subscribing to zmq publisher and writing data to hdf5 file."""

from pathlib import Path

import h5py
import numpy as np
import zmq

from simulation.publisher import recv_array


# TODO: Replace this all with pytables
# https://www.pytables.org/usersguide/libref.html
# https://github.com/PyTables/PyTables/blob/master/examples
def write_hdf(file: h5py.File, topic: str, data: np.typing.NDArray) -> None:
    """Write data to hdf5 file.

    Args:
        file: HDF5 file object.
        topic: Topic name for the dataset.
        data: Data to write to the dataset.
    """
    if topic in file:
        dataset = file[topic]
    else:
        dataset = create_dataset(file, data, topic)

    dataset.resize(dataset.len() + 1, axis=0)
    dataset[dataset.len() - 1] = data


def create_dataset(file: h5py.File, data: np.typing.NDArray, name: str = 'default') -> h5py.Dataset:
    """Create a new dataset in the hdf5 file.

    Args:
        file: HDF5 file object.
        data: Data to write to the dataset.
        name: Name of the dataset.
    """
    return file.create_dataset(name=name, shape=(0,) + data.shape, maxshape=(None,) + data.shape, dtype=data.dtype)


def save_agents(filename: Path, batchsize=32, port: int = 5556) -> None:
    """Function for writing data to file. Required to support saving virus topics.

    Args:
        filename: Path to output file (must be .hdf5).
        batchsize: Number of timestemps to save in each batch.
        port: ZMQ port accessed by publisher.
    """
    file = h5py.File(filename, 'w')
    context = zmq.Context()
    with context.socket(zmq.SUB) as socket:
        socket.connect(f'tcp://localhost:{port}')
        socket.setsockopt(zmq.RCVHWM, 0)
        socket.setsockopt(zmq.SUBSCRIBE, b'agents')
        socket.setsockopt(zmq.SUBSCRIBE, b'agent_info')
        socket.setsockopt(zmq.SUBSCRIBE, b'virus')
        socket.setsockopt(zmq.SUBSCRIBE, b'timesteps')

        virus = None
        agent_info = None

        while True:
            topic = socket.recv_string()
            if topic in ['agents', 'virus']:
                data = recv_array(socket)
                write_hdf(file, topic, data)
            else:
                data = socket.recv_pyobj()
                if topic == 'timesteps':
                    write_hdf(file, topic, np.array(data))
                elif topic == 'agent_info':
                    agent_info = data
                    break

    timesteps = file['timesteps'].__array__()
    agents = file['agents'].__array__()
    if 'virus' in file:
        virus = file['virus'].__array__().round().astype(np.int16)
    file.close()

    with h5py.File(filename, 'w') as file:
        agents = file.create_dataset('agents', data=agents, compression='gzip', compression_opts=9)
        agents.attrs['info'] = agent_info
        file.create_dataset('timesteps', data=timesteps, compression='gzip', compression_opts=9)
        if virus is not None:
            file.create_dataset('virus', data=virus, compression='gzip', compression_opts=9)


def save_agents_fast(filename: Path, port: int = 5556) -> None:
    """Function for writing data to file in bulk.

    Args:
        filename: Path to output file (must be .hdf5).
        port: ZMQ port accessed by publisher.
    """
    store = {}
    context = zmq.Context()
    with context.socket(zmq.SUB) as socket:
        socket.connect(f'tcp://localhost:{port}')
        socket.setsockopt(zmq.RCVHWM, 0)
        socket.setsockopt(zmq.SUBSCRIBE, b'agents')
        socket.setsockopt(zmq.SUBSCRIBE, b'agent_info')
        socket.setsockopt(zmq.SUBSCRIBE, b'timesteps')
        socket.setsockopt(zmq.SUBSCRIBE, b'')

        while True:
            topic = socket.recv_string()
            if topic in ('agents', 'timesteps'):
                store[topic] = recv_array(socket)
            else:
                data = socket.recv_pyobj()
                if topic == 'agent_info':
                    store[topic] = np.array(data, dtype=h5py.special_dtype(vlen=str))
                else:
                    break

    with h5py.File(filename, 'w') as f:
        f.create_dataset('agents', data=store['agents'], compression='gzip', compression_opts=9)
        f.create_dataset('agent_info', data=store['agent_info'], compression='gzip', compression_opts=9)
        f.create_dataset('timesteps', data=store['timesteps'], compression='gzip', compression_opts=9)

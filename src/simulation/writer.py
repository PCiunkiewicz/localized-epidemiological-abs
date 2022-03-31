"""
The `writer` module contains code for receiving and
writing data using message queueing with `zmq` and `hdf5`.
Special functions have been written for direct handling
of numpy arrays without pickling the Python objects.
"""

import time
import shutil

import zmq
import h5py
import numpy as np

from .publisher import recv_array


def write_hdf(f, topic, data):
    if topic in f:
        dataset = f[topic]
    else:
        dataset = create_dataset(f, data, topic)

    dataset.resize(dataset.len() + 1, axis=0)
    dataset[dataset.len() - 1] = data


def create_dataset(f, data, name='default'):
    return f.create_dataset(
        name=name,
        shape=(0,) + data.shape,
        maxshape=(None,) + data.shape,
        dtype=data.dtype,
        # compression='gzip',
        # compression_opts=9
    )


def save_agents(port, filename):
    """Function for writing data to file.

    Parameters
    ----------
    port : int
        ZMQ port accessed by publisher.
    filename : str
        Path to output file (must be .hdf5).
    """
    if filename is None:
        return
    f = h5py.File(filename, 'w')
    context = zmq.Context()
    with context.socket(zmq.SUB) as socket:
        socket.connect(f"tcp://localhost:{port}")
        socket.setsockopt(zmq.RCVHWM, 0)
        socket.setsockopt(zmq.SUBSCRIBE, b'agents')
        socket.setsockopt(zmq.SUBSCRIBE, b'virus')
        socket.setsockopt(zmq.SUBSCRIBE, b'timesteps')
        socket.setsockopt(zmq.SUBSCRIBE, b'trivial')
        socket.setsockopt(zmq.SUBSCRIBE, b'')
        while True:
            topic = socket.recv_string()
            if topic == 'agents':
                data = recv_array(socket)
                write_hdf(f, topic, data)
            elif topic == 'virus':
                data = recv_array(socket)
                write_hdf(f, topic, data)
            elif topic == 'timesteps':
                data = socket.recv_pyobj()
                write_hdf(f, 'timesteps', np.array(data))
            else:
                data = socket.recv_pyobj()
                break
        time.sleep(0.5)

    if data == 'stop':
        timesteps = f['timesteps'].__array__()
        agents = f['agents'].__array__()
        virus = f['virus'].__array__().round().astype(np.int16)
        f.close()

    elif topic == 'trivial':
        timesteps = f['timesteps'].__array__()
        agents = f['agents'].__array__()
        virus = np.zeros(shape=data['virus_shape'], dtype=np.int8)
        f.close()
        # shutil.copy('trivial.hdf5', filename) # need to create trivial output based on agents and map

    with h5py.File(filename, 'w') as f:
        f.create_dataset('agents', data=agents, compression='gzip', compression_opts=9)
        f.create_dataset('timesteps', data=timesteps, compression='gzip', compression_opts=9)
        f.create_dataset('virus', data=virus, compression='gzip', compression_opts=9)

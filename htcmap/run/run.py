import os
import sys
import socket
import datetime
from pathlib import Path

import cloudpickle


def print_node_info():
    print(f'Landed on execute node {socket.getfqdn()} ({socket.gethostbyname(socket.gethostname())}) at {datetime.datetime.utcnow()}.')
    print(f'Execute node operating system: {os.uname()}')

    dir_contents = ", ".join(str(x) for x in Path.cwd().iterdir())
    print(f'Local directory contents: {dir_contents}')


def run_func(arg_hash):
    with open('fn.pkl', mode = 'rb') as file:
        fn = cloudpickle.load(file)

    with open(f'{arg_hash}.in', mode = 'rb') as file:
        args, kwargs = cloudpickle.load(file)

    output = fn(*args, **kwargs)

    with open(f'{arg_hash}.out', mode = 'wb') as file:
        cloudpickle.dump(output, file)


def main():
    print_node_info()
    run_func(arg_hash = sys.argv[1])
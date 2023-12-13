#!/usr/bin/env python3
#
# read all the protocol messages and respond to any "cmds" with one of the tests msgs
# also echo to console the parsed cmd and msg

import logging
import argparse as arg
import re
import socket
import threading
from functools import wraps
from threading import RLock

from handlers.default import DefaultHandler

import coloredlogs

from pyavcontrol import DeviceController, DeviceModel

LOG = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

CLIENTS = []

# special locked wrapper
sync_lock = RLock()


def synchronized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with sync_lock:
            return func(*args, **kwargs)

    return wrapper


class Server(threading.Thread):
    def __init__(self, sock, address, handler):
        threading.Thread.__init__(self)
        self._socket = sock
        self._address = address
        self._handler = handler
        self.register_client()

    @synchronized
    def register_client(self):
        LOG.info("%s:%s connected." % self._address)
        CLIENTS.append(self)

    @synchronized
    def deregister_client(self):
        LOG.info("%s:%s disconnected." % self._address)
        CLIENTS.remove(self)

    def run(self):
        try:
            self.register_client()

            while True:  # continously read data
                data = self._socket.recv(1024)
                if not data:
                    break

                text = data.decode(self._handdler.encoding)

                # remove any termination/separators
                text = text.replace("\r", "").replace("\n", "")

                LOG.debug(f"Received: {text}")
                response = self._handler.handle_command(text)

                if response:
                    response += "\r"  # FIXME: add EOL/command separator
                    data = response.encode(self._handler.encoding)
                    self._socket.send(data)

        finally:
            self._socket.close()
            self.deregister_client()


def main():
    p = arg.ArgumentParser(
        description="Test server that partially emulates a specific device model"
    )
    p.add_argument(
        "--port",
        help="port to listen on (default=4999, typical port used by an IP2SL device)",
        type=int,
        default=4999,
    )
    p.add_argument("--model", default="mx160", help="device model (e.g. mx160)")
    p.add_argument(
        "--messages", help="alternative file of message responses (instead of model)"
    )
    p.add_argument(
        "--host", help="listener host (default=127.0.0.1)", default="127.0.0.1"
    )
    p.add_argument("-d", "--debug", action="store_true", help="verbose logging")
    args = p.parse_args()

    if args.debug:
        logging.getLogger().setLevel(level=logging.DEBUG)

    # listen on the specified port
    url = f"socket://{args.host}:{args.port}/"
    LOG.info(f"Emulating model {args.model} on {url}")

    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((args.host, args.port))
        s.listen(2)

        model = DeviceModel(args.model)
        handler = DefaultHandler(model)

        # accept connections
        while True:
            (sock, address) = s.accept()
            Server(sock, address, handler).start()

    finally:
        if s:
            s.close()


main()

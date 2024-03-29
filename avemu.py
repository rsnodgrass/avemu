#!/usr/bin/env python3

import logging
import argparse as arg
import socket
import threading
from functools import wraps
from threading import RLock

import coloredlogs

from handlers import format_data_into_columns
from handlers.default import DefaultHandler
from pyavcontrol import DeviceModelLibrary

LOG = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

DEFAULT_PORT = 4999
CLIENTS = []

# special locked wrapper
sync_lock = RLock()


def synchronized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with sync_lock:
            return func(*args, **kwargs)

    return wrapper


def host_ip4_addresses():
    ip_list = []
    for i in socket.getaddrinfo(socket.gethostname(), None):
        if i[0] is socket.AF_INET and i[1] is socket.SOCK_STREAM:
            ip = i[4][0]
            # if not localhost, add to the list of IP addresses for interfaces
            if ip != '127.0.0.1':
                ip_list.append(ip)
    return ip_list


class Server(threading.Thread):
    def __init__(self, sock, address, handler, model):
        threading.Thread.__init__(self)
        self._socket = sock
        self._address = address
        self._handler = handler
        self._model = model
        self.register_client()

    @synchronized
    def register_client(self):
        LOG.info('%s:%s connected.' % self._address)
        CLIENTS.append(self)

    @synchronized
    def deregister_client(self):
        LOG.info('%s:%s disconnected.' % self._address)
        CLIENTS.remove(self)

    def run(self):
        try:
            self.register_client()

            # each type of device has a unique EOL, use config from model
            # FIXME: Switch to Config.protocol and Config.command_eol from pyavcontrol in future
            protocol = self._model.definition['protocol']
            cmd_separator = protocol.get('command_separator', '\n')
            cmd_eol = protocol.get('command_eol', '')
            msg_eol = protocol.get('message_eol', '')

            while True:  # continously read data
                data = self._socket.recv(1024)
                if not data:
                    break

                decoded_data = data.decode(self._handler.encoding)
                requests = decoded_data.split(cmd_eol)

                for req in requests:
                    # remove any termination/separators
                    req = req.replace(cmd_eol, '').replace(cmd_separator, '')
                    if not req:
                        continue

                    LOG.debug(f'Received: {req}')

                    if response := self._handler.handle_command(req):
                        response += msg_eol
                        data = response.encode(self._handler.encoding)
                        self._socket.send(data)

        finally:
            self._socket.close()
            self.deregister_client()


def main():
    p = arg.ArgumentParser(
        description='avemu - Test server that partially emulates simple text '
        'based protocols exposed by A/V devices (useful for testing clients '
        'without having physical hardware)'
    )
    p.add_argument(
        '--port',
        help=f"port to listen on (default is emulated device's default port or {DEFAULT_PORT})",
        type=int,
        default=DEFAULT_PORT,
    )
    p.add_argument('--model', help='device model (e.g. mcintosh_mx160)', required=True)
    p.add_argument(
        '--supported', help='list supported models', action=arg.BooleanOptionalAction
    )
    p.add_argument('--host', help='listener host (default=0.0.0.0)', default='0.0.0.0')
    p.add_argument('-d', '--debug', action='store_true', help='verbose logging')
    args = p.parse_args()

    if args.debug:
        logging.getLogger().setLevel(level=logging.DEBUG)

    library = DeviceModelLibrary.create()

    if args.supported:
        print('\nModels supported by avemu:\n')
        print(format_data_into_columns(sorted(list(library.supported_models()))))
        return

    # load the model definition for the device
    model = library.load_model(args.model)
    if not model:
        LOG.error(f"Could not find model '{args.model}' in the pyavcontrol library")
        return

    # default the port to the device's typical port, if available
    port = args.port
    if port == DEFAULT_PORT:
        if (
            device_default_port := model.definition['connection']
            .get('ip', {})
            .get('port')
        ):
            port = device_default_port
            LOG.info(f'Using default port {port} for {args.model}')

    # if listening on all network interfaces, display all the IP addresses for convenience
    all_ips = ''
    if args.host == '0.0.0.0':
        all_ips = f" (also on {','.join(host_ip4_addresses())})"

    url = f'socket://{args.host}:{port}/'
    LOG.info(f'Emulating model {args.model} on {url} {all_ips}')

    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # force reuse (if killed recently)
        s.bind((args.host, port))
        s.listen(2)

        handler = DefaultHandler(model)

        # accept connections
        while True:
            (sock, address) = s.accept()
            Server(sock, address, handler, model).start()

    finally:
        if s:
            s.close()


main()

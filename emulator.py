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

import coloredlogs

from pyavcontrol import DeviceController, DeviceModel

LOG = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")

CLIENTS = []
COMMANDS = {}
COMMAND_PATTERNS = {}
COMMAND_RESPONSES = {}

# special locked wrapper
sync_lock = RLock()


def synchronized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with sync_lock:
            return func(*args, **kwargs)

    return wrapper


class Server(threading.Thread):
    def __init__(self, sock, address, model):
        threading.Thread.__init__(self)
        self._socket = sock
        self._address = address
        self._model = model
        self._encoding = "ascii"
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

                text = data.decode(self._encoding)

                # remove any termination/separators
                text = text.replace("\r", "").replace("\n", "")

                LOG.debug(f"Received: {text}")
                response = handle_command(self._model, text)

                if response:
                    response += "\r"  # FIXME: add EOL/command separator
                    data = response.encode(self._encoding)
                    self._socket.send(data)

        finally:
            self._socket.close()
            self.deregister_client()


def handle_command(model: DeviceModel, text: str):
    values = {}

    action_id = COMMANDS.get(text)
    if action_id:
        LOG.info(f"Received {model.id} {action_id} cmd: {text}")

    for pattern, regexp in COMMAND_PATTERNS.items():
        m = re.match(regexp, text)
        if m:
            action_id = "Unknown"
            values = m.groupdict()
            LOG.info(
                f"Received {model.id} {action_id} cmd: {text} -> {pattern} -> {values}"
            )

    if not action_id:
        LOG.warning(f"No command found for: {text}")
        return None

    # just return a stock response, if response messages expected.
    # NOTE: The returned data will NOT match the actual input, but will be a valid
    # formatted response.
    msg = COMMAND_RESPONSES.get(action_id)
    if msg:
        LOG.debug(f"Replying to {action_id} {text}: {msg}")
    return msg


def build_responses(model: DeviceModel):
    api = model.config.get("api", {})
    for group, group_def in api.items():
        # LOG.debug(f"Building responses for group {group}")

        actions = group_def.get("actions", {})
        for action, action_def in actions.items():
            action_id = f"{group}.{action}"

            # register any response messages
            msg = action_def.get("msg")
            if msg:
                # if the msg is based on a regexp, use a canned response
                if "?P<" in msg:
                    tests = action_def.get("tests", {}).get("msg")
                    print(tests)
                    if tests:
                        msg = next(iter(tests))  # first key
                        LOG.debug(
                            f"Message {model.id} {action_id} is templated, returning canned test message: {msg}"
                        )
                    else:
                        LOG.warning(
                            f"Message {model.id} {action_id} is templated, but there are no canned test messages defined."
                        )
                COMMAND_RESPONSES[action_id] = msg

            # register command regexp patterns (if any)
            cmd_pattern = action_def.get("cmd_pattern")
            if cmd_pattern:
                cmd_pattern = f"^{cmd_pattern}$"
                try:
                    COMMAND_PATTERNS[cmd_pattern] = re.compile(cmd_pattern)
                except Exception as e:
                    LOG.error(
                        f"Skipping {action_id} failed regexp compilation: {cmd_pattern} {e}"
                    )
                continue

            # register basic lookups
            cmd = action_def.get("cmd")
            COMMANDS[cmd] = action_id


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
        build_responses(model)

        # accept connections
        while True:
            (sock, address) = s.accept()
            Server(sock, address, model).start()

    finally:
        if s:
            s.close()


main()

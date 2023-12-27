import logging
import pprint as pp
import re

from . import EmulatorHandler

LOG = logging.getLogger(__name__)


class DefaultHandler(EmulatorHandler):
    def __init__(self, model: dict):
        super().__init__(model)

        self._commands = {}
        self._command_patterns = {}
        self._command_responses = {}

        self._build_canned_responses()
        self._display_help()

    def handle_command(self, text: str) -> str:
        values = {}

        if action_id := self._commands.get(text):
            LOG.info(f"Received {action_id} cmd: {text}")

        for pattern, regexp in self._command_patterns.items():
            if m := re.match(regexp, text):
                action_id = "Unknown"
                values = m.groupdict()
                LOG.info(f"Received {action_id} cmd: {text} -> {pattern} -> {values}")

        if not action_id:
            LOG.warning(f"No command found for: {text}")
            return "***ERROR***"

        # just return a stock response, if response messages expected.
        # NOTE: The returned data will NOT match the actual input, but will be a valid
        # formatted response.
        if msg := self._command_responses.get(action_id):
            LOG.debug(f"Replying to {action_id} {text}: {msg}")
            return msg

    def _display_help(self):
        print("Supported commands:")

        help = ""
        i = 0
        for cmd in self._commands:
            help += f"{cmd:<40}"
            if not i % 2:
                help += "\n"
            i += 1

        print(help)

    #        pp.pprint(self._commands)
    #        pp.pprint(self._command_patterns)

    def _build_canned_responses(self):
        api = self._model.get("api", {})
        for group, group_def in api.items():
            # LOG.debug(f"Building responses for group {group}")

            actions = group_def.get("actions", {})
            for action, action_def in actions.items():
                action_id = f"{group}.{action}"

                # register any response messages
                if msg := action_def.get("msg"):
                    if response := msg.get("regex"):
                        # if the msg is based on a regex, use a canned response
                        if "?P<" in response:
                            if tests := msg.get("tests"):
                                response = next(
                                    iter(tests)
                                )  # first key... FIXME: future randomize?
                                # LOG.debug(
                                # f"Message {action_id} is templated, returning canned test message: {response}"
                                # )
                            else:
                                LOG.warning(
                                    f"Message {action_id} is templated, but no test messages defined in model that can be used as a canned response."
                                )
                            self._command_responses[action_id] = response

                # register command regexp patterns (if any)
                if cmd := action_def.get("cmd"):
                    if cmd_pattern := cmd.get("regex"):
                        cmd_pattern = f"^{cmd_pattern}$"
                        try:
                            self._command_patterns[cmd_pattern] = re.compile(
                                cmd_pattern
                            )
                        except Exception as e:
                            LOG.error(
                                f"Skipping failed regex compilation for {action_id}: {cmd_pattern}",
                                e,
                            )
                            continue

                # register basic lookups
                if cmd := action_def.get("cmd"):
                    if fstring := cmd.get("fstring"):
                        self._commands[fstring] = action_id

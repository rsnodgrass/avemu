import logging
import re

from . import EmulatorHandler
from pyavcontrol import DeviceModel


LOG = logging.getLogger(__name__)


class DefaultHandler(EmulatorHandler):
    def __init__(self, model: DeviceModel):
        EmulatorHandler.__init__(self, model)
        
        self._commands = {}
        self._command_patterns = {}
        self._command_responses = {}
        
        self.build_responses(model)

    def handle_command(self, text: str):
        values = {}

        action_id = self._commands.get(text)
        if action_id:
            LOG.info(f"Received {model.id} {action_id} cmd: {text}")

        for pattern, regexp in self._command_patterns.items():
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
        msg = self._command_responses.get(action_id)
        if msg:
            LOG.debug(f"Replying to {action_id} {text}: {msg}")
            return msg

    def build_responses(self, model: DeviceModel):
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
                        self._command_responses[action_id] = msg

            # register command regexp patterns (if any)
            cmd_pattern = action_def.get("cmd_pattern")
            if cmd_pattern:
                cmd_pattern = f"^{cmd_pattern}$"
                try:
                    self._command_patterns[cmd_pattern] = re.compile(cmd_pattern)
                except Exception as e:
                    LOG.error(
                        f"Skipping {action_id} failed regexp compilation: {cmd_pattern} {e}"
                    )
                    continue

            # register basic lookups
            cmd = action_def.get("cmd")
            self._commands[cmd] = action_id

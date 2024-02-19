import os


def format_data_into_columns(data):
    text = ''

    terminal_width = os.get_terminal_size()[0]
    entries_per_row = terminal_width // 30

    i = 1
    for entry in data:
        text += f'{entry:<30}'
        if not i % entries_per_row:
            text += '\n'
        i += 1

    return text


class EmulatorHandler:
    """
    EmulatortHandler base class that defines interface to handle individual
    commands for a device.
    """

    def __init__(self, model: dict):
        self._model = model

    def handle_command(self, text: str) -> str:
        """
        Handle the command received from the client.
        """
        raise NotImplementedError()

    @property
    def encoding(self) -> str:
        """
        :return the encoding used for data transfered for this model (defaults to ASCII)
        """
        return 'ascii'

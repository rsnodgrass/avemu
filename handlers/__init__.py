import logging


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
        return "ascii"

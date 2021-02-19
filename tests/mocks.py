""" mock objects for hcscom

(c) Patrick Menschel 2021

"""

from serial import Serial

from hcscom.hcscom import split_data_to_values, OutputStatus, FORMAT_THREE_DIGITS, format_to_width_and_decimals, \
    format_val, DisplayStatus


class HcsMock(Serial):
    """ A mock object that is basically a serial port

        providing answers to requests, somewhat lame
    """

    def __init__(self):
        """ a simulator for hcscom """
        self.out_buffer = bytearray()
        self.display_values = [1, 1]
        self.presets = [[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]]
        self.active_preset = self.presets[0]
        self.output_status = OutputStatus.off
        self.display_status = DisplayStatus.cv

        self.value_format = None
        self.width = None
        self.decimals = None
        self.set_format(FORMAT_THREE_DIGITS)
        self.max_voltage = 32.2
        self.max_current = 20.2
        self.get_commands = {"GMAX": None,  # relay a function here later
                             "GETS": None,
                             "GETD": None,
                             "GETM": None,
                             "GOVP": None,
                             "GOCP": None,
                             }
        self.set_commands = {"SOUT": None,
                             "VOLT": None,
                             "CURR": None,
                             "RUNM": None,
                             "SOVP": None,
                             "SOCP": None,
                             "PROM": None,
                             }
        super().__init__()

    def set_format(self, fmt):
        """ helper function to set the format and keep consistency """
        self.value_format = fmt
        self.width, self.decimals = format_to_width_and_decimals(self.value_format)

    def handle_sets(self, command, value_data):
        if command == "SOUT":
            value = int(value_data[0])
            assert value in [OutputStatus.off, OutputStatus.on]
            self.output_status = value
        elif command == "VOLT":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.display_values[0] = values[0]
        elif command == "CURR":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.display_values[1] = values[0]
        elif command == "RUNM":
            value = int(value_data[0])
            assert value in range(1, 4)
            self.active_preset = self.presets[value]
            self.display_values = self.presets[value]
        elif command == "SOVP":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[0] = values[0]
        elif command == "SOCP":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[1] = values[0]
        elif command == "PROM":
            values = split_data_to_values(value_data, width=self.width, decimals=self.decimals)
            self.presets = [values[:2], values[2:4], values[4:]]

    def handle_gets(self, command):
        response = bytearray()
        if command == "GMAX":
            for value in [self.max_voltage, self.max_current]:
                response.extend(format_val(val=value, fmt=self.value_format).encode())
        elif command == "GETS":
            for value in self.active_preset:
                response.extend(format_val(val=value, fmt=self.value_format).encode())
        elif command == "GETD":
            for value in self.display_values:
                response.extend(format_val(val=value, fmt=self.value_format).encode())
            response.extend("{0}".format(self.display_status).encode())
        elif command == "GETM":
            for preset in self.presets:
                for value in preset:
                    response.extend(format_val(val=value, fmt=self.value_format).encode())
        elif command == "GOVP":
            response.extend(format_val(val=self.active_preset[0], fmt=self.value_format).encode())
        elif command == "GOCP":
            response.extend(format_val(val=self.active_preset[1], fmt=self.value_format).encode())
        return response

    def write(self, data: bytes):
        assert data[-1:] == b"\r"
        command = data[:4].decode()
        response = bytearray()
        value_data = data[4:].decode().strip("\r")

        if command in self.set_commands:
            self.handle_sets(command, value_data)
        elif command in self.get_commands:
            response.extend(self.handle_gets(command))

        if len(response) > 0:
            self.out_buffer.extend(response)
            self.out_buffer.extend(b"\r")

        self.out_buffer.extend(b"OK")
        self.out_buffer.extend(b"\r")

        return len(data)

    def read(self, size=1):
        assert size > -1
        buf = self.out_buffer[:size]
        self.out_buffer = self.out_buffer[size:]
        return buf

    def flush(self):
        return

    def inWaiting(self):
        return len(self.out_buffer)

    def open(self):
        return None


class HcsDefectMock(HcsMock):

    def write(self, data: bytes):
        self.out_buffer = b"SOME_UNEXPECTED_ANSWER"
        return 42

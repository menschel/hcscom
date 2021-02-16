""" mock objects for hcscom

(c) Patrick Menschel 2021

"""

from serial import Serial

from hcscom.hcscom import split_data_to_values, OutputStatus, FORMAT_THREE_DIGITS, format_to_width_and_decimals, \
    format_val


class HcsMock(Serial):
    """ A mock object that is basically a serial port

        providing answers to requests, somewhat lame
    """

    def __init__(self):
        """ a simulator for hcscom """
        self.out_buffer = bytearray()
        self.display_values = [1, 1]
        self.presets = [[1, 1], [2, 2], [3, 3]]
        self.active_preset = self.presets[0]
        self.output_status = OutputStatus.off

        self.value_format = FORMAT_THREE_DIGITS
        self.width, self.decimals = format_to_width_and_decimals(self.value_format)
        self.max_voltage = 32.2
        self.max_current = 20.2
        self.get_commands = {"GMAX": None,
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
                             }
        super().__init__()

    def handle_sets(self, command, value_data):
        if command == "SOUT":
            value = int(value_data[0])
            assert value in [OutputStatus.off, OutputStatus.on]
            self.output_status = value
        elif command == "VOLT":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[0] = values[0]
        elif command == "CURR":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[1] = values[0]
        elif command == "RUNM":
            value = int(value_data[0])
            self.active_preset = self.presets[value]
            self.display_values = self.presets[value]
        elif command == "SOVP":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[0] = values[0]
        elif command == "SOVP":
            values = split_data_to_values(data=value_data, width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[1] = values[0]

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
        command = data[:4].decode()
        response = bytearray()
        value_data = data[4:].decode()

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

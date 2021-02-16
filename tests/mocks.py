""" mock objects for hcscom

(c) Patrick Menschel 2021

"""

from serial import Serial

from hcscom.hcscom import split_data_to_values, OutputStatus, FORMAT_THREE_DIGITS, format_to_width_and_decimals, format_val


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

        super().__init__()  # do we need this for a mock ?
        #self.is_open = True

    def write(self, data: bytes):
        command = data[:4].decode()
        response = bytearray()

        if command == "GMAX":
            for value in [self.max_voltage,self.max_current]:
                response.extend(format_val(value, self.value_format).encode())

        if command == "SOUT":
            # set output status
            value = int(data[4:].decode())
            assert value in [OutputStatus.off, OutputStatus.on]
            self.output_status = value

        elif command == "VOLT":
            values = split_data_to_values(data[4:].decode(), width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[0] = values[0]

        elif command == "CURR":
            values = split_data_to_values(data[4:].decode(), width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[1] = values[0]

        elif command == "GETS":
            for value in self.active_preset:
                response.extend(format_val(value, self.value_format).encode())

        elif command == "GETD":
            for value in self.display_values:
                response.extend(format_val(value, self.value_format).encode())

        elif command == "GETM":
            for preset in self.presets:
                for value in preset:
                    response.extend(format_val(value, self.value_format).encode())

        elif command == "RUNM":
            value = int(data[4:].decode())
            self.active_preset = self.presets[value]
            self.display_values = self.presets[value]

        elif command == "GOVP":
            response.extend(format_val(value, self.value_format).encode())

        elif command == "SOVP":
            values = split_data_to_values(data[4:].decode(), width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[0] = values[0]

        elif command == "GOCP":
            response.extend(format_val(value, self.value_format).encode())

        elif command == "SOCP":
            values = split_data_to_values(data[4:].decode(), width=self.width, decimals=self.decimals)
            assert len(values) == 1
            self.active_preset[1] = values[0]

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

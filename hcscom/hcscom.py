""" hcscom
an interface class to manson hcs lab power supplies

@author Patrick Menschel

"""

import serial
import io

from enum import Enum,IntEnum

class responsestatus(Enum):
    ok = "OK"

class outputstatus(IntEnum):
    off = 0
    on = 1

class displaystatus(IntEnum):
    cv = 0
    cc = 1


#TODO: make a format value function to be sure all values always have the expected format in messages

def float_to_bytes(val):
    pass

def bytes_to_float(data,):
    return float(data)/10
    

class hcscom:

    def __init__(self,ser):
        self.ser = ser
        self.sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), newline="\r")
        self.max_voltage = None
        self.max_current = None
        self.decimal_format = "3.1f" # defined by model, valuelength is 3 when format is 2.1f and 4 when format is 2.2f
        try:
            self.max_voltage,self.max_current = self.get_max_values()
        except:
            pass

    def request(self,msg):
        msg_ = bytearray()
        msg_.extend(msg.encode())
        msg_.append(b"\r")
        with self.sio as sio:
            sio.write(msg_)
            ret = None
            linebuffer = [msg,]
            for i in range(2):
                line = sio.readline().decode().strip("\r")
                linebuffer.append()
                if line == responsestatus.ok:
                    return ret
                else:
                    ret = line
        raise RuntimeError("Got unexpected status, {0}".format(linebuffer))


    def get_max_values(self) -> dict:
        res = self.request("GMAX")
        vmax = bytes_to_float(res[:3])
        cmax = bytes_to_float(res[3:6])
        return vmax,cmax

    def switchoutput(self,val):
        assert val in [outputstatus.off, outputstatus.on] 
        return self.request("SOUT{0}".format(val))

    def set_voltage(self,val):
        return self.request("VOLT{0}".format(int(val)*10))

    def set_current(self,val):
        return self.request("CURR{0}".format(int(val)*10))

    def get_presets(self):
        res = self.request("GETS")
        volt = bytes_to_float(res[0:3])
        curr = bytes_to_float(res[3:6])
        return volt,curr

    def get_display_status(self):
        res = self.request("GETD")
        volt = bytes_to_float(res[0:3])
        curr = bytes_to_float(res[3:6])
        status = int(res[6])
        return volt,curr,status

    def set_presets_to_memory(self):
        """ program preset values into memory
            TODO: check if there are always 3 presets
        """
        # PROM
        pass

    def get_presets_from_memory(self):
        # TODO: make this into a dictionary once we have the format function
        res = self.request("GETM")
        volt = float(res[0:3])/10
        curr = float(res[3:6])/10
        volt2 = float(res[6:9])/10
        curr2 = float(res[9:12])/10
        volt3 = float(res[12:15])/10
        curr3 = float(res[15:18])/10
        return volt,curr,volt2,curr2,volt3,curr3

    def load_preset(self,val):
        assert val in range(3)
        return self.request("RUNM{0}".format(val))

    def get_output_voltage_preset(self):
        res = self.request("GOVP")
        volt = bytes_to_float(res[0:3])
        return volt

    def set_output_voltage_preset(self,val):
        return self.request("SOVP{0}".format(int(val)*10))

    def get_output_current_preset(self):
        res = self.request("GOCP")
        volt = bytes_to_float(res[0:3])
        return volt

    def set_output_current_preset(self,val):
        return self.request("SOCP{0}".format(int(val)*10))



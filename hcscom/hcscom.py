""" hcscom
an interface class to manson hcs lab power supplies

(c) Patrick Menschel 2021

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


def splitbytes(data=b"320160",width=3,decimals=1):
    """ helper function to split the values from device"""
    vals = tuple(int(data[idx:idx+width])/(10**decimals) for idx in range(0,len(data),width))
    return vals


class HcsCom:

    def __init__(self,port):
        self.ser = serial.Serial(port=port,baudrate=9600,bytesize=serial.EIGHTBITS,parity=serial.PARITY_EVEN,stopbits=serial.STOPBITS_ONE)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser), newline="\r")
        self.max_voltage = None
        self.max_current = None
        self.value_format = "3.1f" # defined by model, keep this format string until we have a better idea
        self.width,self.decimals = [int(x) for x in self.value_format.rstrip("f").split(".")]
        try:
            self.probe_device()
        except BaseException as e:
            print(e)
            exit(1)
            
        

    def request(self,msg):
        """ send command to device and receive the response """        
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
    
    def probe_device(self) -> dict:
        """ probe for a device
            set the formatting and limits accordingly
        """        
        data = self.request("GMAX")
        if len(data) == 6:
            self.value_format = "3.1f"
        elif len(data) == 8:
            self.value_format = "4.2f"
        self.width,self.decimals = [int(x) for x in self.value_format.rstrip("f").split(".")]
        self.max_voltage,self.max_current = splitbytes(data,width=self.width,decimals=self.decimals)

    def get_max_values(self) -> dict:
        """ return the max values """
        return self.max_voltage,self.max_current
    
#     def get_max_values(self) -> dict:
#         data = self.request("GMAX")
#         vmax,cmax = splitbytes(data,width=self.width,decimals=self.decimals)
#         return vmax,cmax

    def switchoutput(self,val):
        """ switch the output """
        assert val in [outputstatus.off, outputstatus.on] 
        return self.request("SOUT{0}".format(val))

    def set_voltage(self,val):
        """ set the voltage limit """
        return self.request("VOLT{0}".format(int(val)*10))

    def set_current(self,val):
        """ set the current limit """        
        return self.request("CURR{0}".format(int(val)*10))

    def get_presets(self):
        """ get the current active presets """        
        data = self.request("GETS")
        volt,curr = splitbytes(data,width=self.width,decimals=self.decimals)
        return volt,curr

    def get_display_status(self):
        """ get the current display status """        
        data = self.request("GETD")
        volt,curr = splitbytes(data[:-1],width=self.width,decimals=self.decimals)
        status = int(data[-1])
        return volt,curr,status

    def set_presets_to_memory(self):
        """ program preset values into memory
            TODO: check if there are always 3 presets
        """
        # PROM
        pass

    def get_presets_from_memory(self) -> dict:
        """ get the presets from device memory """        
        data = self.request("GETM")
        volt,curr,volt2,curr2,volt3,curr3 = splitbytes(data,width=self.width,decimals=self.decimals)
        
        return {1:(volt,curr),
                2:(volt2,curr2),
                3:(volt3,curr3),
                }

    def load_preset(self,val):
        """ load one of the presets """        
        assert val in range(3)
        return self.request("RUNM{0}".format(val))

    def get_output_voltage_preset(self):
        """ get the preset voltage """
        data = self.request("GOVP")
        volt = splitbytes(data,width=self.width,decimals=self.decimals)
        return volt

    def set_output_voltage_preset(self,val):
        """ set the preset voltage """
        return self.request("SOVP{0}".format(int(val)*10))

    def get_output_current_preset(self):
        """ get the preset current """
        data = self.request("GOCP")
        volt = splitbytes(data,width=self.width,decimals=self.decimals)
        return volt

    def set_output_current_preset(self,val):
        """ set the preset current """
        return self.request("SOCP{0}".format(int(val)*10))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("port")
    args = parser.parse_args()
    port = args.interface
     
    hcs = HcsCom(port=port)

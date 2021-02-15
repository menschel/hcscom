""" hcscom
an interface class to manson hcs lab power supplies

(c) Patrick Menschel 2021

"""

import serial
import io

from enum import Enum,IntEnum

class responsestatus(Enum):
    ok = "OK"

class outputstatus(IntEnum):  # ERROR
    off = 1
    on = 0

class displaystatus(IntEnum):
    cv = 0
    cc = 1

#SYSTEM_SET_LAG = 0.5

FORMAT_THREE_DIGITS = "{:04.1f}" # +1 due to .
FORMAT_FOUR_DIGITS = "{:05.2f}"  # +1 due to .

def format_to_width_and_decimals(fmt):
     width, decimals = [int(x) for x in fmt.split(":")[-1].strip("f}").split(".")]
     return width-1, decimals

def splitbytes(data=b"320160",width=3,decimals=1):
    """ helper function to split the values from device"""
    vals = tuple(int(data[idx:idx+width])/(10**decimals) for idx in range(0,len(data),width))
    return vals

def format_val(val,width,fmt):
    #print(val,width,fmt)
    ret = fmt.format(val).replace(".","")
    #print(ret)
    return ret


class HcsCom:

    def __init__(self,port):
        if isinstance(port,str):
            self.ser = serial.Serial(port=port,baudrate=9600, timeout=1)
        elif isinstance(port,serial.Serial):
            self.ser = port
        else:
            raise ValueError("Not handling {0}".format(type(port)))
        self.ser.flush()
        self.max_voltage = None
        self.max_current = None
        self.value_format = FORMAT_THREE_DIGITS
        self.width,self.decimals = format_to_width_and_decimals(self.value_format)
        try:
            self.probe_device()
        except BaseException as e:
            print(e)
            exit(1)
            
        

    def request(self,msg):
        """ send command to device and receive the response """        
        print(">> {0}".format(msg))
        msg_ = bytearray()
        msg_.extend(msg.encode())
        msg_.extend(b"\r")
        with self.ser as ser:
            #ser.flush()
            #print(">> {0}".format(msg_.decode()))
            ser.write(msg_)
            ret = None
            linebuffer = bytearray()
            while b"OK\r" not in linebuffer:
                data = ser.read(1)
                if data:
                    linebuffer.extend(data)
                    linebuffer.extend(ser.read(ser.inWaiting()))
                    #print(linebuffer)
            for line in linebuffer.decode().split("\r"):
                #print(line, responsestatus.ok, line == responsestatus.ok, type(line),type(responsestatus.ok))
                print("<< {0}".format(line))
                if line == "OK":
                    return ret
                elif line:
                    ret = line
                else:
                    print("Empty Line")
        raise RuntimeError("Got unexpected status, {0}".format(linebuffer))

    def probe_device(self) -> dict:
        """ probe for a device
            set the formatting and limits accordingly
        """        
        data = self.request("GMAX")
        #print(data)
        if len(data) == 6:
            self.value_format = FORMAT_THREE_DIGITS
        elif len(data) == 8:
            self.value_format = FORMAT_FOUR_DIGITS
        #print(self.value_format)
        self.width,self.decimals = format_to_width_and_decimals(self.value_format)
        self.max_voltage,self.max_current = splitbytes(data,width=self.width,decimals=self.decimals)

    def __str__(self):
        return "Device: {0}\n V: {1}V A: {2}".format("unknown",self.max_voltage,self.max_current)

    def get_max_values(self) -> dict:
        """ return the max values """
        return self.max_voltage,self.max_current

    def switchoutput(self,val):
        """ switch the output """
        assert val in [outputstatus.off, outputstatus.on]
        return self.request("SOUT{0}".format(val))

    def set_voltage(self,val):
        """ set the voltage limit """
        return self.request("VOLT{0}".format(format_val(val,self.width,self.value_format)))

    def set_current(self,val):
        """ set the current limit """
        return self.request("CURR{0}".format(format_val(val,self.width,self.value_format)))

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
        return self.request("SOVP{0}".format(format_val(val,self.width,self.value_format)))

    def get_output_current_preset(self):
        """ get the preset current """
        data = self.request("GOCP")
        volt = splitbytes(data,width=self.width,decimals=self.decimals)
        return volt

    def set_output_current_preset(self,val):
        """ set the preset current """
        return self.request("SOCP{0}".format(format_val(val,self.width,self.value_format)))


if __name__ == "__main__":
    import argparse
    import numpy as np
    import time
    parser = argparse.ArgumentParser()
    parser.add_argument("port")
    args = parser.parse_args()
    port = args.port
    hcs = HcsCom(port=port)
    print(hcs)
    hcs.switchoutput(outputstatus.on)
    max_volt,max_curr = hcs.get_max_values()
    print(max_volt)
    for volt in np.arange(1,max_volt,0.5):
        hcs.set_voltage(volt)
        time.sleep(.5)
    hcs.switchoutput(outputstatus.off)

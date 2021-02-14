""" mock objects for hcscom

(c) Patrick Menschel 2021

"""
 
from serial import Serial

from hcscom.hcscom import splitbytes, outputstatus

class hcsmock(Serial):
    
    def __init__(self):
        """ a simulator for hcscom """
        self.outbuffer = bytearray()
        self.display_values = (1,1) 
        self.presets = [(1,1),(2,2),(3,3)]
        self.activepreset = self.presets[0]
        self.outputstatus = outputstatus.off
        
        self.value_format = "{3.1f}"
        self.width,self.decimals = [int(x) for x in self.value_format.rstrip("f{}").split(".")]
        
        super().__init__()  # do we need this for a mock ?
    
    def write(self,data : bytes):
        cmd = data[:4]
        response = bytearray()
        
        if cmd == "SOUT":
            # set output status
            val = int(data[4:].decode())
            assert val in [outputstatus.off, outputstatus.on]
            self.outputstatus = val
            
        elif cmd == "VOLT":
            vals = splitbytes(data[4:],width=self.width,decimale=self.decimals)
            assert len(vals) == 1
            self.activepreset[0] = vals[0]
            
        elif cmd == "CURR":
            vals = splitbytes(data[4:],width=self.width,decimale=self.decimals)
            assert len(vals) == 1
            self.activepreset[1] = vals[0]
            
        elif cmd == "GETS":
            for val in self.activepreset:
                response.extend(self.value_format.format(int(val * (10**self.decimals))))
            
        elif cmd == "GETD":
            for val in self.display_values:
                response.extend(self.value_format.format(int(val * (10**self.decimals))))
            
        elif cmd == "GETM":
            for preset in self.presets:
                for val in preset:
                    response.extend(self.value_format.format(int(val * (10**self.decimals))))
            
        elif cmd == "RUNM":
            val = int(data[4:].decode())
            self.activepreset = self.presets[val]
            self.display_values = self.presets[val]
            
        elif cmd == "GOVP":
            response.extend(self.value_format.format(int(self.activepreset[0] * (10**self.decimals))))
            
        elif cmd == "SOVP":
            vals = splitbytes(data[4:],width=self.width,decimale=self.decimals)
            assert len(vals) == 1
            self.activepreset[0] = vals[0]
            
        elif cmd == "GOCP":
            response.extend(self.value_format.format(int(self.activepreset[1] * (10**self.decimals))))
            
        elif cmd == "SOCP":
            vals = splitbytes(data[4:],width=self.width,decimale=self.decimals)
            assert len(vals) == 1
            self.activepreset[1] = vals[0]

        if len(response) > 0:
            self.outbuffer.extend(response.encode())
            self.outbuffer.extend(b"\r")
            
        self.outbuffer.extend(b"OK")
        self.outbuffer.extend(b"\r")
        
        return len(data)
    
    def read(self,size=1):
        assert size > -1
        buf = self.outbuffer[:size]
        self.outbuffer = self.outbuffer[size:]
        return buf 
            
        
        
        
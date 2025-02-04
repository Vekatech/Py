# MCP47CVB24   (https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP47CXBX4_8-Data-Sheet-20006537B.pdf)

from smbus2 import SMBus

class MCP47CVB24:

# 00h Volatile DAC Wiper Register 0        R/W    0x07FF
# 01h Volatile DAC Wiper Register 1        R/W    0x07FF
# 02h Volatile DAC Wiper Register 2        R/W    0x07FF
# 03h Volatile DAC Wiper Register 3        R/W    0x07FF

# 08h Volatile VREF Register               R/W    0x0000
# 09h Volatile Power-Down Register         R/W    0x0000
# 0Ah Volatile Gain and Status Register    R/W    0x0080

    ADR = (0x60, 0x61, 0x62, 0x63)
    REG = {
        "DAC0": 0x00,
        "DAC1": 0x01,
        "DAC2": 0x02,
        "DAC3": 0x03,
        "VREF": 0x08,
        "PWRDW": 0x09,
        "GAINSTS": 0x0A
    }

    def __init__(self, i2c_bus, i2c_addr=0x60):
        if isinstance(i2c_bus, SMBus):
            self.bus = i2c_bus
        else:
            raise TypeError(f"First arg of MCP47CVB24 must be an instance of smbus2.SMBus, not {type(i2c_bus).__name__}")

        if isinstance(i2c_addr, int):
            if 0 <= i2c_addr <= 127:
                self.addr = i2c_addr 
            else:
                raise ValueError(f"Second arg of MCP47CVB24 must be in the range 0 - 127, not {i2c_addr}")
        else:
            raise TypeError(f"Second arg of MCP47CVB24 must be an integer, not {type(i2c_addr).__name__}")
        self.Vcc = None
        self.settings = None
        self.Mref = None
        self.Vref = None

    def broadcast_reset(self):
        self.bus.write_byte(0x00, 0x06)

    def broadcast_wakeup(self):
        self.bus.write_byte(0x00, 0x0A)

    def read_reg(self, reg):
        data = self.bus.read_i2c_block_data(self.addr, (reg << 3) | 0x6, 2)
        return (data[0] << 8) | data[1]

    def write_reg(self, reg, value):
        self.bus.write_i2c_block_data(self.addr, reg << 3, [value >> 8, value & 0x00FF])

    def cfg(self, vcc=5.0, ref=0x00, down=0x00, gain=0x00):
        self.Vcc = vcc
        self.write_reg(self.REG["VREF"], ref)
        self.write_reg(self.REG["PWRDW"], down)
        self.write_reg(self.REG["GAINSTS"], gain)
        Vref = [0, 0, 0, 0]
        #11 Vref buffered
        #10 Vref unbuffer
        #01 Internal band gap, Vref buffered
        #00 Vdd, Vref unbuffered
        for ch in range(4):
            chREF = (ref >> (ch*2)) & 0x3
            if chREF == 0x00:
                Vref[ch] = vcc
            elif chREF == 0x01:
                Vref[ch] = 1.214 # [1.118 < 1.214 < 1.260]
            else:
                Vref[ch] = True
        self.Mref = tuple(Vref)
        for V in Vref:
            if isinstance(V, bool):
                V = 0
        self.Vref = Vref
        self.settings = (ref, down, gain)

    def init(self, v=5.0, r=0x00, d=0x00, g=0x00):
        self.cfg(v, r, d, g)

    def set_ref(self, ch, ref):
        ch = ch & 0x03
        if isinstance(self.Mref[ch], bool):
            self.Vref[ch] = ref

    def get_data(self, ch):
        return self.read_reg(ch & 0x03)

    def set_data(self, ch, value):
        if value < 0:
            value = 0
        if value > 4095:
           value = 4095
        self.write_reg(ch & 0x03, value)

    def get_v(self, ch):
        V = self.get_data(ch)
        V *= (self.Vref[ch]/4096)
        return round(V, 3)

    def set_v(self, ch, V):
        LSB = (self.Vref[ch]/4096)
        if V < 0:
           V = 0
        if V > self.Vref[ch]:
           V = self.Vref[ch]
        V /= LSB
            self.set_data(ch, int(V))

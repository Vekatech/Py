# ADS122C04   (https://www.ti.com/document-viewer/ads122c04/datasheet)

from smbus2 import SMBus
import time

class ADS122C04:

# 00h |MUX[3:0] | GAIN[2:0] | PGA_BYPASS |
# 01h |DR[2:0] | MODE | CM | VREF[1:0] | TS |
# 02h |DRDY | DCNT | CRC[1:0] | BCS | IDAC[2:0] |
# 03h |I1MUX[2:0] | I2MUX[2:0] | 0 | 0 |

    ADR = (0x40, 0x41, 0x44, 0x45)
    REG = {
        "CFG0": 0x00,
        "CFG1": 0x01,
        "CFG2": 0x02,
        "CFG3": 0x03
    }
    CMD = {
        "RESET": 0x06,
        "START": 0x08,
        "PWRDWN": 0x02,
        "RDATA": 0x10,
        "RREG": 0x20,
        "WREG": 0x40
    }

    def __init__(self, i2c_bus, i2c_addr=0x40):
        if isinstance(i2c_bus, SMBus):
            self.bus = i2c_bus
        else:
            raise TypeError(f"First arg of ADS122C04 must be an instance of smbus2.SMBus, not {type(i2c_bus).__name__}")

        if isinstance(i2c_addr, int):
            if 0 <= i2c_addr <= 127:
                self.addr = i2c_addr 
            else:
                raise ValueError(f"Second arg of ADS122C04 must be in the range 0 - 127, not {i2c_addr}")
        else:
            raise TypeError(f"Second arg of ADS122C04 must be an integer, not {type(i2c_addr).__name__}")
        self.settings = None
        self.Vref = 5.0

    def start(self):
        self.bus.write_byte(self.addr, self.CMD["START"])

    def reset(self):
        self.bus.write_byte(self.addr, self.CMD["RESET"])

    def pwrdwn(self):
        self.bus.write_byte(self.addr, self.CMD["PWRDWN"])

    def read_reg(self, reg):
        return self.bus.read_byte_data(self.addr, self.CMD["RREG"] | (0x0C & (reg << 2)))

    def write_reg(self, reg, value):
        self.bus.write_byte_data(self.addr, self.CMD["WREG"] | (0x0C & (reg << 2)), value)

    def read_data(self):
        data = self.bus.read_i2c_block_data(self.addr, self.CMD["RDATA"], 3)
        raw_adc = (data[0] << 16) | (data[1] << 8) | data[2]
        # Convert to signed integer
        if raw_adc & 0x800000:
            raw_adc -= 1 << 24
        return raw_adc

    def cfg(self, cfg0=0x81, cfg1=0x04, cfg2=0, cfg3=0):
        self.write_reg(self.REG["CFG0"], cfg0) # AINp = AIN0, AINn = AVSS; PGA disabled and bypassed
        self.write_reg(self.REG["CFG1"], cfg1) # Analog supply (AVDD – AVSS) used as reference
        if (cfg1 & 0x06) == 0x00:
            self.Vref = 2.048
        self.write_reg(self.REG["CFG2"], cfg2)
        self.write_reg(self.REG["CFG3"], cfg3)
        self.settings = (cfg0, cfg1, cfg2, cfg3)

    def get_ch(self, ch):
        ch = 0x30 & self.read_reg(self.REG["CFG0"])
        return ch >> 4

    def set_ch(self, ch):
        set = self.read_reg(self.REG["CFG0"])
        self.write_reg(self.REG["CFG0"], (set & ~0x30) | (0x30 & (ch << 4)))

    def init(self, c0=0x81, c1=0x04, c2=0, c3=0):
        self.reset()
        self.cfg(c0, c1, c2, c3)
        if (self.settings[1] & 0x08) == 0x08:
            self.start()

    def get_data(self, wait=0.5):
        if (self.settings[1] & 0x08) == 0x00:
        self.start()
        DRDY = 0
            start_stamp = time.time()
            while (DRDY & 0x80) == 0x00:
                DRDY = self.read_reg(self.REG["CFG2"])
                if (time.time() - start_stamp) > wait:  # Check if timeout exceeded
                    raise TimeoutError(f"DRDY signal not received within {wait} seconds.")
        return self.read_data()

    def get_v(self, wait=0.5):
        # LSB = (2 · VREF / Gain) / 2^24
        V = self.get_data(wait)
        V *= ((2*self.Vref)/16777216)
        return round(V, 3)

    def get_data_from(self, ch, wait=0.5):
        self.set_ch(ch)
        time.sleep(0.06)
        return self.get_data(wait)

    def get_v_from(self, ch, wait=0.5):
        V = self.get_data_from(ch, wait)
        V *= ((2*self.Vref)/16777216)
        return round(V, 3)

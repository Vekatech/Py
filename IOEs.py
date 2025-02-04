# PCAL9538ABSHP   (https://www.mouser.bg/datasheet/2/302/PCAL9538A-3139550.pdf)

from smbus2 import SMBus

class PCA9538A:

# 00h Input port                      R     xxxx xxxx
# 01h Output port                    R/W    1111 1111
# 02h Polarity Inversion             R/W    0000 0000
# 03h Configuration                  R/W    1111 1111

    ADR = (0x70, 0x71, 0x72, 0x73)
    REG = {
        "IN": 0x00,
        "OUT": 0x01,
        "INVIN": 0x02,
        "CFGIO": 0x03
    }

    def __init__(self, i2c_bus, i2c_addr=0x70):
        if isinstance(i2c_bus, SMBus):
            self.bus = i2c_bus
        else:
            raise TypeError(f"First arg of {self.__class__.__name__} must be an instance of smbus2.SMBus, not {type(i2c_bus).__name__}")

        if isinstance(i2c_addr, int):
            if 0 <= i2c_addr <= 127:
                self.addr = i2c_addr 
            else:
                raise ValueError(f"Second arg of {self.__class__.__name__} must be in the range 0 - 127, not {i2c_addr}")
        else:
            raise TypeError(f"Second arg of {self.__class__.__name__} must be an integer, not {type(i2c_addr).__name__}")

    def read_reg(self, reg):
        return self.bus.read_byte_data(self.addr, reg)

    def write_reg(self, reg, value):
        self.bus.write_byte_data(self.addr, reg, value)

    def cfg(self, value):
        self.write_reg(self.REG["CFGIO"], value)

    def get_cfg(self):
        return self.read_reg(self.REG["CFGIO"])

    def get_port(self):
        return self.read_reg(self.REG["IN"])

    def get_bit(self, bit):
        port = self.read_reg(self.REG["IN"])
        if 0 <= bit < 8:
            return (port & (1 << bit)) >> bit
        else:
            return 0

    def set_port(self, value):
        self.write_reg(self.REG["OUT"], value)

    def set_bit(self, bit):
        port = self.read_reg(self.REG["OUT"])
        if 0 <= bit < 8:
            self.write_reg(self.REG["OUT"], port | (1 << bit))

    def clr_bit(self, bit):
        port = self.read_reg(self.REG["OUT"])
        if 0 <= bit < 8:
            self.write_reg(self.REG["OUT"], port & ~(1 << bit))



class PCAL9538A(PCA9538A):

# 00h Input port                      R     xxxx xxxx
# 01h Output port                    R/W    1111 1111
# 02h Polarity Inversion             R/W    0000 0000
# 03h Configuration                  R/W    1111 1111

# 40h Output drive strength 0        R/W    1111 1111
# 41h Output drive strength 1        R/W    1111 1111
# 42h Input latch                    R/W    0000 0000
# 43h Pull-up/pull-down enable       R/W    0000 0000
# 44h Pull-up/pull-down selection    R/W    1111 1111
# 45h Interrupt mask                 R/W    1111 1111
# 46h Interrupt status                R     0000 0000
# 4Fh Output port configuration      R/W    0000 0000

    def __init__(self, i2c_bus, i2c_addr=PCA9538A.ADR[0]):
        super().__init__(i2c_bus, i2c_addr)
        self.REG.update({
            "DRV0": 0x40,
            "DRV1": 0x41,
            "LATCHIN": 0x42,
            "PULLUDEN": 0x43,
            "PULLUDSEL": 0x44,
            "IRQMSK": 0x45,
            "IRQSTS": 0x46,
            "CFGOUT": 0x4F
        })

    def set_pullup(self, mask):
        en = self.read_reg(self.REG["PULLUDEN"])
        sel = self.read_reg(self.REG["PULLUDSEL"])
        self.write_reg(self.REG["PULLUDSEL"], sel | mask)
        self.write_reg(self.REG["PULLUDEN"], en | mask)

    def set_pulldown(self, mask):
        en = self.read_reg(self.REG["PULLUDEN"])
        sel = self.read_reg(self.REG["PULLUDSEL"])
        self.write_reg(self.REG["PULLUDSEL"], sel & ~mask)
        self.write_reg(self.REG["PULLUDEN"], en | mask)

    def set_ODouts(self):
        self.write_reg(self.REG["CFGOUT"], 0x01)

    def set_PPouts(self):
        self.write_reg(self.REG["CFGOUT"], 0x00)

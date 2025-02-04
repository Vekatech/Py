# VK-HATs
#   ADC+DAC+PIO
#   POE+UART+IO
#   WURTH-IMS

from smbus2 import SMBus
from ADCs import ADS122C04
from DACs import MCP47CVB24
from IOEs import PCAL9538A
#from EEPROMs import 24LC02B

class VK_HAT_ADC_DAC_PIO:

    ADC = []
    DAC = []
    PIO = []

    def __init__(self, i2c_bus=0):
        addr = []
        if isinstance(i2c_bus, int):
            if 0 <= i2c_bus <= 3:
                self.bus = SMBus(i2c_bus)
            else:
                raise ValueError(f"An arg of VK_HAT_ADC_DAC_PIO must be in the range 0 - 3, not {i2c_bus}")
        elif isinstance(i2c_bus, SMBus):
            self.bus = i2c_bus
        else:
            raise TypeError(f"An arg of VK_HAT_ADC_DAC_PIO must be an instance of integer or SMBus, not {type(i2c_bus).__name__}")

        if isinstance(i2c_bus, int):
            print("Searching ADC, DAC & PIO chips on the HAT board @ bus %d ..." % i2c_bus)
        else:
            print("Searching ADC, DAC & PIO chips on the HAT board @ inited bus ...")

        for i2c_addr in range(128):
            try:
                self.bus.read_byte(i2c_addr)
                if i2c_addr in ADS122C04.ADR:         
                    self.ADC.append(ADS122C04(self.bus, i2c_addr))
                    print("  Found: ADC @ %#02X (ADS122C04)" % i2c_addr)
                elif i2c_addr in MCP47CVB24.ADR:
                    self.DAC.append(MCP47CVB24(self.bus, i2c_addr))
                    print("  Found: DAC @ %#02X (MCP47CVB24)" % i2c_addr)
                elif i2c_addr in PCAL9538A.ADR:
                    self.PIO.append(PCAL9538A(self.bus, i2c_addr))
                    print("  Found: PIO @ %#02X (PCA9538A/PCAL9538A)" % i2c_addr)
                elif i2c_addr in range(0x50, 0x58):
                    addr.append(i2c_addr)
                else:
                    if i2c_addr == 0x12:
                        print("  Found: PMIC @ %#02X (RAA215300)" % i2c_addr)
                    else:
                        print("  Found: chip @ %#02X (Unknown)" % i2c_addr)
            except:
                if addr and i2c_addr > 0x57:
                    print(f"  Found: EEPROM @ {', '.join([f'{i:#02X}' for i in addr])} (24LC02B)")
                    addr = []

    def close(self):
        self.bus.close()

class VK_HAT_POE_UART_IO:
    # TBD ...
    def __init__(self):
        pass

class WURTH_IMS:
    # TBD ...
    def __init__(self):
        pass
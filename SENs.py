# SDP611   (https://sensirion.com/media/documents/63859DD0/6166CF0E/Sensirion_Differential_Pressure_Datasheet_SDP600Series.pdf)

from smbus2 import SMBus

class SDP611:

# E4h Write Advanced User Register         R/W    0x0000
# E5h Read Advanced User Register          R/W    0x7782  > 9-11 bits controls resolution (9 - 16)

    ADR = (0x40,)
    REG = {
        "WAU": 0xE4,
        "RAU": 0xE5
    }

#60 Pa-1
#6’000 mbar-1
#413’686 psi-1
#14’945 (inch H2O)-1#

    unit = {
        "Pa": 60,
        "mbar": 6000,
        "psi": 413686,
        "inH2O": 14945,
    }

    def __init__(self, i2c_bus, CRC=True):
        if isinstance(i2c_bus, SMBus):
            self.bus = i2c_bus
        else:
            raise TypeError(f"First arg of SDP611 must be an instance of smbus2.SMBus, not {type(i2c_bus).__name__}")

        self.check = CRC

    def reset(self):
        self.bus.write_byte(self.ADR[0], 0xFE)

    def check_CRC(self, data):
        #CRC8 = x8 + x5 + x4 +1
        #data = [MSB, LSB, CRC]
        POLY = 0x31
        if self.check:
            crc = 0x00
            for byte in data[0:2]:
                crc ^= byte
                for _ in range(8):
                    if (crc & 0x80) != 0:   # If MSB is 1
                        crc = ((crc << 1) ^ POLY) & 0xFF
                    else:
                        crc = (crc << 1) & 0xFF
            if crc == data[2]:
                return True
            else:
                return False
        else:
            return True

    def read_data(self):
        #Note that the first measurement result after reset is not valid
        data = self.bus.read_i2c_block_data(self.ADR[0], 0xF1, 3)
        if self.check_CRC(data):
            raw = (data[0] << 8) | data[1]
            if raw & 0x8000:
                raw -= 0x10000
            return raw
        else:
            return 0x0000

    def get_RES(self):
        res = self.bus.read_i2c_block_data(self.ADR[0], self.REG["RAU"], 3)
        if self.check_CRC(res):
            return 9 + ((res[0] & 0x0F) >> 1)
        else:
            return 0

    def set_RES(self, res):
        if 9 <= res <= 16:
            self.bus.write_i2c_block_data(self.ADR[0], self.REG["WAU"], [0x71 | ((res-1) << 1), 0x82])

    def get_DP(self, unit="Pa" ):
        DP = self.read_data()
        if unit in self.unit:
            return round(DP/self.unit[unit], 3)
        else:
            return 0

    def get_FLOW(self):
        pass

#try:
#    while True:
#        P.get_DP("mbar")
#        #print(f"Sensor reading: {dp_value}")
#        # Wait 100 ms
#        time.sleep(0.1)
#except KeyboardInterrupt:
#    print("Loop interrupted by user.")

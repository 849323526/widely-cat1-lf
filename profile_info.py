# from global_var import GlobalMap
from format_conversion import Format_con


class Pro_load(object):
    def __init__(self, packet):
        self.__bytes = 2
        self.__nextSide = 0
        self.__inside = 12
        self.__memoryData = ""
        self.__tool = Format_con()
        self.__inside = 12
        self.__packet = packet
        self.__ip = ""
        self.__port = ""
        self.__vendorId = ""
        self.__length = 0
        self.__devAddr = ""
        self.__mode = ""
        self.__baudrate = []
        self.__delay = 141
        self.__interval = 138
        self.__regnumber = 120
        self.__register = ""

    def writeToMemory(self):
        self.__memoryData.set_map("RSM_IP", self.__ip)
        self.__memoryData.set_map("RSM_PORT", self.__port)
        self.__memoryData.set_map("VENDOR", self.__vendorId)
        self.__memoryData.set_map("DEV_ADDR", self.__devAddr)
        self.__memoryData.set_map("MODE", self.__mode)
        self.__memoryData.set_map("SERIAL_BAUD", self.__baudrate)
        self.__memoryData.set_map("DELAY", self.__delay)
        self.__memoryData.set_map("INTERVAL", self.__interval)
        self.__memoryData.set_map("REGNUMBER", self.__regnumber)
        if self.__mode != "FWD":
            self.__memoryData.set_map("REGISTER", self.__register)

    def build_ip(self):
        self.__nextSide = self.__bytes * 4
        ip = self.__packet[self.__inside:self.__inside + self.__nextSide]
        ip_list = self.__tool.HexStringToList(ip)
        ip = ""
        for i in ip_list:
            ip += str(i) + '.'
        self.__ip = ip[:-1]
        self.__inside += self.__nextSide

    def build_port(self):
        self.__nextSide = self.__bytes * 2
        port = self.__packet[self.__inside: self.__inside + self.__nextSide]
        self.__port = int(port, 16)
        self.__inside += self.__nextSide

    def build_vendor(self):
        self.__nextSide = self.__bytes * 8
        vendor = self.__packet[self.__inside: self.__inside + self.__nextSide]
        vendor_list = self.__tool.HexStringToList(vendor)
        vendor = ""
        for i in vendor_list:
            vendor += chr(i)
        self.__vendorId = vendor
        self.__inside += self.__nextSide

    def build_len(self):
        self.__inside += 4
        self.__nextSide = self.__bytes * 2
        length = self.__packet[self.__inside:self.__inside + self.__nextSide]
        self.__length = int(length, 16)
        self.__inside += self.__nextSide

    def build_devAddr(self):
        self.__nextSide = self.__bytes
        dev_addr = self.__packet[self.__inside:self.__inside + self.__nextSide]
        # dev_addr = str(int(dev_addr, 16))
        # if len(dev_addr) < 2:
        #     self.__devAddr += "0"
        self.__devAddr = dev_addr
        self.__inside += self.__nextSide

    def build_mode(self):
        self.__nextSide = self.__bytes
        mode = self.__packet[self.__inside:self.__inside + self.__nextSide]
        mode = int(mode, 16)
        # if (mode >> 1) & 1 == 1:
        #     self.__mode = "FWD"
        # elif mode & 1 == 1:
        #     self.__mode = "MASTER"
        # elif mode == 0:
        #     self.__mode = "SLAVE"
        if mode == 3:
            self.__mode = "FWD"
        elif mode == 1:
            self.__mode = "MASTER"
        else:
            self.__mode = "SLAVE"
        self.__inside += self.__nextSide

    def build_baudrate(self):
        self.__nextSide = self.__bytes
        baudrate = self.__packet[self.__inside:self.__inside + self.__nextSide]
        baudrate = int(baudrate, 16) * 4800
        if baudrate == 0:
            baudrate = 2400
        elif baudrate == 230400:  # not use 230400
            baudrate = 1200
        elif baudrate == 460800:  # not use 460800
            baudrate = 600
        self.__baudrate.append(baudrate)
        self.__inside += self.__nextSide
        parity = int(self.__packet[self.__inside:self.__inside + self.__nextSide], 16)
        if parity == 0:
            self.__baudrate.append('n')
        elif parity == 1:
            self.__baudrate.append('o')
        elif parity == 2:
            self.__baudrate.append('e')
        self.__inside += self.__nextSide
        databits = int(self.__packet[self.__inside:self.__inside + self.__nextSide], 16)
        self.__baudrate.append(databits)
        self.__inside += self.__nextSide
        stop_bit = int(self.__packet[self.__inside:self.__inside + self.__nextSide], 16)
        self.__delay = (stop_bit >> 2)
        stop_bit &= 3
        self.__baudrate.append(stop_bit)
        self.__inside += self.__nextSide

    def build_interval(self):
        self.__nextSide = self.__bytes
        self.__interval = int(self.__packet[self.__inside:self.__inside + self.__nextSide], 16)
        self.__inside += self.__nextSide

    def build_regnumber(self):
        self.__nextSide = self.__bytes
        self.__regnumber = int(self.__packet[self.__inside:self.__inside + self.__nextSide], 16)
        self.__inside += self.__nextSide

    def build_registerPacket(self):
        self.__register = self.__packet[self.__inside: -8]

    def __init(self):
        from start import Global_map
        self.__memoryData = Global_map

    def main(self):
        self.__init()
        self.build_ip()
        self.build_port()
        self.build_vendor()
        self.build_len()
        self.build_devAddr()
        self.build_mode()
        self.build_baudrate()
        self.build_interval()
        self.build_regnumber()
        if self.__mode != "FWD":
            self.build_registerPacket()
        self.writeToMemory()

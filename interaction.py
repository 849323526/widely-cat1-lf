from crc_module import Modbus_crc8
from queue import Queue

USB_QC = False
QUEUE = Queue(maxsize=100)


class UartQc(object):
    def __init__(self, serial_conf, crc8):
        import sim, modem
        self.__serial = serial_conf
        self.__iccid = str(sim.getIccid()) + chr(UartQc.check_sum(str(sim.getIccid())))
        self.__imsi = str(sim.getImsi()) + chr(UartQc.check_sum(str(sim.getImsi())))
        self.__imei = str(modem.getDevImei()) + chr(UartQc.check_sum(str(modem.getDevImei())))
        self.__crc8 = crc8
        self.__qc_sn = False

    @staticmethod
    def check_sum(s_data):
        check_sum = 0
        for char in s_data:
            print("s_data:%s, ord:%d" % (s_data, ord(char)))
            check_sum += ord(char)
        print("checksum:%d" % check_sum)
        print("new check sum:%d" % (check_sum % 126))
        return check_sum % 126

    def __verify_checksum(self, s_msg):
        receive_checksum = ord(s_msg[-1])
        calculated_checksum = UartQc.check_sum(s_msg[:-1])
        print("check sum|%s:%s|" % (receive_checksum, calculated_checksum))
        return receive_checksum == calculated_checksum

    def __check_snHeader(self, s_sn):
        header = s_sn[:2]
        hex_data = s_sn[3:7]
        header_hexStr = ""
        for i in header:
            if 65 <= ord(i) <= 90:
                header_hexStr += hex(ord(i)).replace("0x", "")
        if hex_data == header_hexStr.upper():
            return True
        else:
            print("Head input error!%s not equal to %s" % (header, hex_data))
            return False

    def __check_snLenth(self, s_sn):
        if len(s_sn) == 16:
            return True
        else:
            print("Length is not 16!")
            return False

    def __judge(self, i_buf_len):
        s_msg = self.__serial.read(i_buf_len).decode()
        print("|%s|" % s_msg)
        if s_msg == "QC READY?":
            print("[QC]Send Ready:")
            self.__serial.write("READY")
        elif s_msg == "ICCID?":
            print("[QC]Send ICCID:%s" % self.__iccid)
            self.__serial.write(self.__iccid)
        elif s_msg == "IMSI?":
            print("[QC]Send IMSI:%s" % self.__imsi)
            self.__serial.write(self.__imsi)
        elif s_msg == "IMEI?":
            print("[QC]Send IMEI:%s" % self.__imei)
            self.__serial.write(self.__imei)
        elif "SN" in s_msg:
            if self.__verify_checksum(s_msg) and self.__check_snLenth(s_msg[3:]) and self.__check_snHeader(s_msg[3:]):
                if self.__qc_sn:
                    self.__serial.write("SN OK" + self.__qc_sn)
                else:
                    global QUEUE
                    s_no_crc8_sn = s_msg[6:-1]
                    QUEUE.put(s_no_crc8_sn)
                    self.__qc_sn = self.__crc8.calc_crc8(s_no_crc8_sn) + s_no_crc8_sn
                    self.__serial.write("SN OK" + self.__qc_sn)
            else:
                self.__serial.write("SN ERROR")
        else:
            print("[QC]RECEIVE ERROR:%s" % s_msg)

    def main(self, args):
        print("\n[QC]Port[%d], recv %d bytes data:" % (args[1], args[2]))
        self.__judge(args[2])


class UsbInteraction(object):
    def __init__(self):
        # self.var = GlobalMap()
        # self.flash_data = self.var.get("all")
        # self.flash = Flash_module()
        self.crc8 = Modbus_crc8()
        self.sn = ""

    def get_inputSn(self):
        print("SN[]:")
        print("SN[]:", end='')
        # sn = input()
        # self.sn = sn
        self.sn = "PM-504D30000B89"

    def build_sn(self):
        self.sn = self.crc8.calc_crc8(self.sn) + self.sn
        print("Integral SN:%s" % self.sn)

    def check_snLenth(self):
        if len(self.sn) == 15:
            return True
        else:
            print("Length is not 15!")
            return False

    def check_snHeader(self):
        header = self.sn[:2]
        hex_data = self.sn[3:7]
        header_hexStr = ""
        for i in header:
            if 65 <= ord(i) <= 90:
                header_hexStr += hex(ord(i)).replace("0x", "")
        if hex_data == header_hexStr.upper():
            self.sn = self.sn[3:]
            return True
        else:
            print("Head input error!%s not equal to %s" % (header, hex_data))
            return False

    def check_sn(self):
        if self.check_snLenth():
            if self.check_snHeader():
                return True
        return False

    def __uart_qc(self):
        from dev_uart import Main_uart
        serial_conf, _ = Main_uart().build_uart_conf()
        c_uart_qc = UartQc(serial_conf, self.crc8)
        serial_conf.set_callback(c_uart_qc.main)
        self.sn = QUEUE.get()

    def main(self):
        if USB_QC:
            while True:
                self.get_inputSn()
                if self.check_sn():
                    break
        else:
            self.__uart_qc()
        self.build_sn()
        return self.sn

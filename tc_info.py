import ustruct, urandom, utime
# from global_var import GlobalMap
from format_conversion import Format_con
from crc_module import Modbus_crc16


class Tc_info(object):
    def __init__(self):
        # self.__memory_data = GlobalMap()
        self.__memory_data = ""
        self.__tool = Format_con()
        self.__crc = Modbus_crc16()
        self.__signature = "PR"
        self.__nuance = b""
        self.__code = b'\x01'
        self.__flags = b'\x09'
        self.__sn = ""
        self.__pr_crc = b"\xFF\xFF"
        self.__pr_type = b"\x00\x40"
        self.__pr_size = b'\x00\x14'
        self.__iccid = ""

    def var_init(self):
        from start import Global_map
        self.__memory_data = Global_map
        self.__signature = "PR"
        self.__nuance = b""
        self.__code = b'\x02'
        self.__flags = b'\x09'
        self.__sn = self.__memory_data.get("SN") + "00"
        self.__pr_crc = b"\xFF\xFF"
        self.__pr_type = b"\x00\x40"
        self.__pr_size = b'\x00\x14'
        self.__iccid = self.__memory_data.get("ICCID")

    def build_nuance(self):
        """
        This module is to obtain a random number, which is 2 bytes of hex
        """
        urandom.seed(utime.ticks_cpu())
        nuance = "".join([urandom.choice("0123456789ABCDEF") for i in range(4)])
        while nuance:
            self.__nuance += ustruct.pack('B', int(nuance[:2], 16))
            nuance = nuance[2:]

    def build_signature(self):
        byte = b""
        for i in self.__signature:
            byte += ustruct.pack('B', ord(i))
        self.__signature = byte

    def build_sn(self):
        byte = b""
        sn_list = self.__tool.HexStringToList(self.__sn)
        for i in sn_list:
            byte += ustruct.pack('B', i)
        self.__sn = byte

    def build_iccid(self):
        byte = b""
        for i in self.__iccid:
            byte += ustruct.pack('B', ord(i))
        # iccid_list = self.__tool.HexStringToList(self.__iccid)
        # for i in iccid_list:
        #     byte += ustruct.pack('B', i)
        self.__iccid = byte

    def build_intactData(self):
        byte_data = self.__signature + self.__nuance + self.__code + self.__flags + self.__sn + self.__pr_crc + self.__pr_type + self.__pr_size + self.__iccid
        string_buf = self.__tool.HexStringToList(self.__tool.bytesToHexString(byte_data))
        crc_buf = self.__crc.calc_crc16(string_buf)
        intact_dataBuf = string_buf + crc_buf
        string_data = ""
        for i in intact_dataBuf:
            string_data += chr(i)
        return string_data

    def main(self):
        self.var_init()
        self.build_nuance()
        self.build_iccid()
        self.build_sn()
        self.build_signature()
        return self.build_intactData()

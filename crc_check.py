from crc_module import Modbus_crc16
from format_conversion import Format_con


class Check_module(object):
    def __init__(self):
        self.__crc = Modbus_crc16()
        self.__tool = Format_con()

    def backcalculation_crc(self, header, string_data):
        string_buf = self.__tool.HexStringToList(string_data)
        header_buf = self.__tool.stringToAscii_hex(header)
        crc_buf = self.__crc.calc_crc16(header_buf + string_buf)
        if crc_buf[0] == crc_buf[1] == 0:
            return True
        else:
            return False

    def main(self, dataBuf):
        # string_buf = self.__tool.HexStringToList(string_data)
        if type(dataBuf) is str:
            dataBuf = self.__tool.HexStringToList(dataBuf)
        dataCrcBuf = dataBuf[-2:]
        crcBuf = self.__crc.calc_crc16(dataBuf[:-2])
        if crcBuf == dataCrcBuf:
            return True
        else:
            # print("CRC Error")
            # print("True:%s" % crcBuf)
            # print("False:%s" % dataCrcBuf)
            return False

import urandom, utime
# from global_var import GlobalMap
from format_conversion import Format_con
from base64_module import Base64_module
from crc_check import Check_module
from start import CRC16


class Creat_info(object):
    def __init__(self):
        self.identifier = ""
        self.__tool = Format_con()
        self.__crc_check = Check_module()
        self.crc = CRC16
        self.base64_module = Base64_module()

    def creat_identifier(self):
        """
        This module is to obtain a random number, which is 4 bytes of hex
        """
        urandom.seed(utime.ticks_cpu())
        self.identifier = "".join([urandom.choice("0123456789ABCDEF") for i in range(8)])

    def get_connectionCode(self, string):
        """
        This is the module to get the connection code
        :param string:Must be a string, and include base64
        :return:If successful to get connection code, will return connection code list
                else return None
        """
        base64_data = (string.replace("REG-ACK ", "")).replace(".\n", "")
        data = self.base64_module.base64_decode(base64_data)
        if len(data) == 20:
            L = []
            data = data[8:-4]
            for i in range(0, 8, 2):
                L.append(int(data[i:i + 2], 16))
            return L
        else:
            return None

    def build_hbData(self, connect_id):
        """
        This module is for creating heartbeat data
        :param connect_id:Must be a list!
        :return:If successful to build hbData, will return hhbData
        """
        header_list = self.__tool.stringToAscii_hex("HB")
        crc16 = self.crc.calc_crc16(header_list + connect_id)
        base64_data = self.base64_module.get_base64(connect_id + crc16)
        return "HB " + base64_data + '\n'

    # def get_sendData(self, header, connect_id, *args):
    #     header_list = self.__tool.stringToAscii_hex(header)
    #     if header == "PAY":
    #         dev_data_list = self.__tool.HexStringToList(args[0])
    #         crc16 = self.crc.calc_crc16(header_list + connect_id + dev_data_list)
    #         base64_data = self.base64_module.get_base64(connect_id + dev_data_list + crc16)
    #     else:
    #         crc16 = self.crc.calc_crc16(header_list + connect_id)
    #         base64_data = self.base64_module.get_base64(connect_id + crc16)
    #     return header + ' ' + base64_data + '\n'

    def build_regData(self):
        """
        This module is for creating register to cloud data
        :return:If successful to build register packet, will return register packet
        """
        from start import Global_map
        self.sn = Global_map.get("SN")
        self.creat_identifier()
        header_list = self.__tool.stringToAscii_hex("REG")
        identifier_list = self.__tool.HexStringToList(self.identifier)
        sn_list = self.__tool.HexStringToList(self.sn)
        # self.__tool.print_hexlist(header_list + identifier_list + sn_list)
        crc16 = self.crc.calc_crc16(header_list + identifier_list + sn_list)
        # self.__tool.print_hexlist(identifier_list + sn_list + crc16)
        base64_data = self.base64_module.get_base64(identifier_list + sn_list + crc16)
        # print(crc16)
        return "REG " + base64_data + '\n'

    def build_payData(self, data, connect_id, random_buf, type_buf):
        """
        This module is for creating send to cloud data
        :param connect_id:Must be a buffer!
        :param data:Must be a string!
        :return:If successful to build payData, will return payData
        """
        # print("connect_id is %s" % connect_id)
        header_list = self.__tool.stringToAscii_hex("PAY")
        data_buf = self.__tool.HexStringToList(data)
        data_buf = self.build_modbusData(data_buf)
        data_buf = self.build_toAdmPacket(random_buf, type_buf, data_buf)
        crc16 = self.crc.calc_crc16(header_list + connect_id + data_buf)
        # print("data buf is %s", data_buf)
        base64_data = self.base64_module.get_base64(connect_id + data_buf + crc16)
        return "PAY " + base64_data + '\n'

    def build_modbusData(self, data_buf):   # 此模块为发送错误码所用
        crc16_buf = self.crc.calc_crc16(data_buf)
        if crc16_buf[0] == crc16_buf[1] == 0:
            return data_buf
        else:
            return data_buf + crc16_buf

    def build_toAdmPacket(self, random_buf, type_buf, data_buf):
        length_buf = [len(data_buf)]
        crc16_buf = self.crc.calc_crc16(random_buf + type_buf + length_buf + data_buf)
        # print("crc 16 is %s", crc16_buf)
        return random_buf + type_buf + length_buf + data_buf + crc16_buf

    def unpacket_pay(self, data):
        # print("ubpacket1: %s" % data)
        data = (data.split(' ')[-1])[:-2]
        # print("ubpacket2: %s" % data)
        data = self.base64_module.base64_decode(data)
        data_buf = self.__tool.HexStringToList(data)
        adm_info = data_buf[4:8]
        random_buf = adm_info[:2]
        function_type = adm_info[2]
        data_buf_length = adm_info[3]
        if self.__crc_check.backcalculation_crc('PAY', data):
            # print("In here")
            # print("data")
            if function_type == 0:
                print("Recv type is 0, will be restart!")
                return False
            if (data_buf_length * 2) == len(data[16:-8]):
                packet = [data[16:-8], random_buf, [function_type]]
                return packet
            else:
                print("In rsm info, length Error")
                print("Data buf length: %d" % data_buf_length * 2)
                print("Actual length: %d" % len(data[16:-8]))
                print(data[16:-8])
                return True
        else:
            return True


if __name__ == '__main__':
    a = Creat_info()
    print(a.creat_identifier())
    # print(a.identifier)
    # a.build_hbData([[10, 12, 15, 10, 15, 5, 2, 6]])

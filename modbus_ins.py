R_COIL = 1
R_DISCRETE = 2
R_HOLDING = 3
R_INPUT = 4
W_COIL = 5
W_HOLDING = 6
W_HOLDINGS = 10


class AdminRegister:
    register_number = 3
    start_register = "FF00"
    packet = "0000FFFFFFFFFFFF0001000000000000000000000000000000000000000000000000000000000000"

    @staticmethod
    def build_packet(s_packet):
        if s_packet != 'Null_':
            return s_packet
        else:
            print("[INS]Build admin register!")
            from start import TOOL
            AdminRegister.packet += AdminRegister.start_register
            s_data = TOOL.intListToHexString([AdminRegister.register_number])
            if len(s_data) < 4:
                s_data = (4 - len(s_data)) * '0' + s_data
            AdminRegister.packet += s_data
            return AdminRegister.packet


class Modbusins_module(object):
    def __init__(self):
        from modbus_db import Modbusdb_moudle
        from format_conversion import Format_con
        from start import Global_map, CRC16
        print(Global_map.get("all"))
        self.__byte = 1
        self.__db = Modbusdb_moudle()
        self.__db.init(AdminRegister.build_packet(Global_map.get("REGISTER")))
        # self.__db.init(
        # "0070FFFFFFFFFFFF000300000000000000000000000000000000000000000000000000000000000003E1000F07C1002008360009")
        self.__tool = Format_con()
        self.__crc16 = CRC16
        self.__devAddr = 0
        self.__devFunCode = 0
        self.__devBody = []
        self.__errInfo = []
        self.__startAddr = 0
        self.__number = 0
        self.__bitIsOn = 0

    def __buildErrData(self):
        L = []
        self.__devAddr = [self.__devAddr]
        self.__devFunCode = [self.__devFunCode | 0x80]
        L.extend(self.__devAddr)
        L.extend(self.__devFunCode)
        L.extend(self.__errInfo)
        # return self.__devAddr + self.__devFunCode + self.__errInfo
        return L

    def __buildTruData(self, body_list):
        L = []
        self.__devAddr = [self.__devAddr]
        self.__devFunCode = [self.__devFunCode]
        byteLength = [int(hex(len(body_list)), 16)]
        L.extend(self.__devAddr)
        L.extend(self.__devFunCode)
        L.extend(byteLength)
        L.extend(body_list)
        # return self.__devAddr + self.__devFunCode + byteLength + body_list
        return L

    def __writeToCoil(self, dataBuf):
        result = self.__db.set_data(W_COIL, self.__startAddr, self.__bitIsOn)
        if result:
            return dataBuf[:-2]
        else:
            self.__errInfo = [2]
            return self.__buildErrData()

    def __writeToHolding(self, dataBuf):
        result = self.__db.set_data(W_HOLDING, self.__startAddr, self.__number)
        if result:
            return dataBuf[:-2]
        else:
            self.__errInfo = [2]
            return self.__buildErrData()

    def __writeToHoldings(self, dataBuf):
        result = self.__db.set_multData(W_HOLDINGS, self.__startAddr, self.__number, dataBuf[7:-2])
        if result:
            return dataBuf[:6]
        else:
            self.__errInfo = [2]
            return self.__buildErrData()

    def __readCoil(self, start_addr, number):
        result = self.__db.get_data(R_COIL, start_addr, number)
        if result:
            return self.__buildTruData(result)
        else:
            self.__errInfo = [2]
            return self.__buildErrData()

    def __readDis(self):
        self.__errInfo = [2]
        return self.__buildErrData()

    def __readInput(self):
        self.__errInfo = [2]
        return self.__buildErrData()

    def __readHolding(self, start_addr, number):
        result = self.__db.get_data(R_HOLDING, start_addr, number)
        if result:
            return self.__buildTruData(result)
        else:
            self.__errInfo = [2]
            return self.__buildErrData()

    def __Do(self, dataBuf):
        if self.__devFunCode == 0x01:
            return self.__readCoil(self.__startAddr, self.__number)
        elif self.__devFunCode == 0x02:
            return self.__readDis()
        elif self.__devFunCode == 0x03:
            return self.__readHolding(self.__startAddr, self.__number)
        elif self.__devFunCode == 0x04:
            return self.__readInput()
        elif self.__devFunCode == 0x05:
            return self.__writeToCoil(dataBuf)
        elif self.__devFunCode == 0x06:
            return self.__writeToHolding(dataBuf)
        elif self.__devFunCode == 0x10:
            return self.__writeToHoldings(dataBuf)

    def __addCrc(self, data_list):
        return self.__tool.intListToHexString(data_list + self.__crc16.calc_crc16(data_list))

    def __checkFunLen(self):
        # func_code = int(func_code, 16)
        if self.__devFunCode <= 0x06:
            if len(self.__devBody) == 4:
                self.__startAddr = (self.__devBody[0] << 8 | self.__devBody[1])
                self.__number = (self.__devBody[2] << 8 | self.__devBody[3])
                return True
            else:
                self.__errInfo = [3]
                return False
        elif self.__devFunCode == 0x10 and len(self.__devBody) >= 7:
            # number = int(body[4:8], 16) * 2
            self.__startAddr = (self.__devBody[0] << 8 | self.__devBody[1])
            self.__number = (self.__devBody[2] << 8 | self.__devBody[3])
            number = self.__number * 2
            length = self.__devBody[4]
            body_length = len(self.__devBody[5:])
            if len(self.__devBody) % 4 != 0 and number == length and body_length == length:
                return True
            else:
                print("check 10 error")
                print(self.__devBody)
                print(length)
                print("end")
                self.__errInfo = [3]
                return False
        else:
            self.__errInfo = [3]
            return False

    def __checkBitNumber(self):
        if self.__devFunCode == 0x05:
            control = (self.__devBody[2] << 8 | self.__devBody[3])
            if control == 0xFF00:
                self.__bitIsOn = 1
                return True
            elif control == 0x0000:
                self.__bitIsOn = 0
                return True
            else:
                return False
        else:
            return True

    def __checkFunCode(self):
        # func_code = int(func_code, 16)
        # if func_code <= 0 or func_code > 6:
        #     if func_code != 0x10:
        #         self.__errInfo = [1]
        #         return False
        #     else:
        #         return True
        # else:
        #     return True
        if self.__devFunCode <= 0x06 or self.__devFunCode == 0x10:
            return True
        else:
            self.__errInfo = [3]
            return False

    def __checkData(self, data):
        inside = 0
        print(data)
        print("len is %d" % len(data))
        self.__devAddr = data[inside:self.__byte][0]
        print("devaddr is %s" % self.__devAddr)
        inside += self.__byte
        self.__devFunCode = data[inside: inside + self.__byte][0]
        print("devfuncode is %s" % self.__devFunCode)
        inside += self.__byte
        self.__devBody = data[inside:-2]
        if self.__checkFunCode() and self.__checkFunLen() and self.__checkBitNumber():
            return True
        else:
            return False

    def main(self, data):
        if not self.__checkData(data):
            print("check Data Error")
            return self.__addCrc(self.__buildErrData())
        else:
            data = self.__Do(data)
            # print("return data:")
            # print(data)
            # print(type)
            # print("end")
            # if type(data) is list:
            return self.__addCrc(data)
            # else:
            #     return data


if __name__ == '__main__':
    c = Modbusins_module()
    print(c.main("010307C10001D482"))

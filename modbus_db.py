class Modbusdb_moudle(object):
    def __init__(self):
        self.__byte = 2
        self.__coilRange = {}
        self.__discreteRange = {}
        self.__holdingRange = {}
        self.__inputRange = {}
        self.__array = [self.__coilRange, self.__discreteRange, self.__holdingRange, self.__inputRange]
        self.__key = ""
        self.__bitArray = [1, 3, 7, 15, 31, 63, 127, 255]

    def __appendRange(self, reg_list, dt_list):
        print(reg_list)
        print(dt_list)
        register_list = [self.__coilRange, self.__discreteRange, self.__inputRange, self.__holdingRange]
        count = 0
        for reg in reg_list:
            if reg != "FFFF":
                data_range = int(reg, 16)
                for i in range(data_range):
                    # offset = int(dt_list[0][0:4], 16)
                    offset = dt_list[0][0:4]
                    number = int(dt_list[0][4:], 16)
                    L = [number, []]
                    if count >= 2:
                        for value in range(number):
                            L[1].append(0)
                    else:
                        for value in range(number // 8):
                            L[1].append(0)
                        if number % 8 != 0:
                            L[1].append(0)
                    register_list[count][offset] = L
                    dt_list.pop(0)
            count += 1

    def init(self, packet):
        reg_list = []
        data_list = []
        inside = self.__byte * 2
        for i in range(4):
            reg_list.append(packet[inside:inside + self.__byte * 2])
            inside += (self.__byte * 2)
        inside = self.__byte * 40
        packet = packet[inside:]
        for i in range(0, len(packet), self.__byte * 4):
            data_list.append(packet[i: i + self.__byte * 4])
        self.__appendRange(reg_list, data_list)
        self.__discreteRange = self.__inputRange = None
        print("coil: %s" % self.__coilRange)
        print("dis: %s" % self.__discreteRange)
        print("input: %s" % self.__inputRange)
        print("holding: %s" % self.__holdingRange)

    def __getBit(self, start_addr, number):
        byteInside = 0
        resultList = []
        startInside = start_addr // 8
        bitInside = start_addr % 8
        n_byte = number // 8
        residue = number % 8
        rangList = self.__coilRange[self.__key][1][startInside:]
        # print("rangList is %s" % rangList)
        # print("n_byte is %s" % n_byte)
        # print("residue is %s" % residue)
        for i in range(n_byte):
            resultList.append(((rangList[i] >> bitInside) | (rangList[i + 1] << (8 - bitInside))) & 0xFF)
            byteInside += 1

        if residue != 0:
            k = 8 - residue
            # print("k - 1 is %d" % (k - 1))
            # print("bitArray is %s" % self.__bitArray[k - 1])
            # print("byteInside is %s" % byteInside)
            # print("rangeList is %s" % rangList[byteInside])
            resultList.append((rangList[byteInside] >> k) & self.__bitArray[k - 1])
        return resultList

    def __getByte(self, start_addr, number):
        result_list = []
        data_list = self.__holdingRange[self.__key][1]
        inside = start_addr - int(self.__key, 16)
        for i in range(number):
            result_list.append(data_list[inside + i] >> 8 & 0xFF)
            result_list.append(data_list[inside + i] & 0xFF)
        # print(result_list)
        return result_list

    def __setByte(self, start_addr, data):
        # print("set data is")
        # print(data)
        # print("end")
        inside = start_addr - int(self.__key, 16)
        self.__holdingRange[self.__key][1][inside] = data

    def __setBit(self, start_addr, bitIsOn):
        inside = start_addr - int(self.__key, 16)
        listInside = inside // 8
        if inside < 8:
            bitInside = inside
        else:
            bitInside = inside % 8
        data = self.__coilRange[self.__key][1][listInside]
        if bitIsOn:
            # print("set on!")
            # print("1 is %s, 2 is %s" % (listInside, bitInside))
            # print("RANGE is %s" % self.__coilRange[self.__key][1][listInside])
            self.__coilRange[self.__key][1][listInside] = (1 << bitInside | data)
        else:
            # print("set off!")
            # print("1 is %s, 2 is %s" % (listInside, bitInside))
            # print("RANGE is %s" % self.__coilRange[self.__key][1][listInside])
            self.__coilRange[self.__key][1][listInside] = (data & ~(1 << bitInside))

    def __setBytes(self, start_addr, data_list):
        inside = start_addr - int(self.__key, 16)
        for i in range(len(data_list)):
            self.__holdingRange[self.__key][1][inside] = data_list[i]
            inside += 1

    def __checkRangeOut(self, register, start_addr, regNumber):
        keys_list = list(self.__array[register - 1].keys())
        keys_list.sort()
        for addr in keys_list:
            key = int(addr, 16)
            if key <= start_addr <= key + self.__array[register - 1][addr][0]:
                if start_addr + regNumber <= key + self.__array[register - 1][addr][0]:
                    self.__key = addr
                    # print("here")
                    return True
        print("check range is out!")
        return False

    def set_multData(self, register, start_addr, number, dataList):
        print("10 in here, will check range")
        # print(register)
        # print(start_addr)
        # print(number)
        # print(data_body)
        # print("end")
        if register == 10:
            if self.__checkRangeOut(3, start_addr, number):
                L = []
                for i in range(0, len(dataList), 2):
                    L.append(dataList[i] << 8 | dataList[i + 1])
                print("*** will set data ***")
                print(L)
                print("*** end ***")
                self.__setBytes(start_addr, L)
                print("*** set OK ***")
                print("holding: %s" % self.__holdingRange)
                print("*** set end ***")
                return True
        return False

    def set_data(self, register, start_addr, data):
        if register == 5:
            if self.__checkRangeOut(1, start_addr, 1):
                print("WILL TO SET BIT DATA")
                self.__setBit(start_addr, data)
                print("set bit ok")
                print("coil: %s" % self.__coilRange)
                print("dis: %s" % self.__discreteRange)
                # print("input: %s" % self.__inputRange)
                # print("holding: %s" % self.__holdingRange)
                return True
        elif register == 6:
            if self.__checkRangeOut(3, start_addr, 1):
                print("WILL TO SET byte DATA")
                self.__setByte(start_addr, data)
                print("set byte ok")
                # print("coil: %s" % self.__coilRange)
                # print("dis: %s" % self.__discreteRange)
                print("input: %s" % self.__inputRange)
                print("holding: %s" % self.__holdingRange)
                return True
        else:
            print("SET DATA ERROR")
            return False

    def get_data(self, register, start_addr, number):
        if self.__checkRangeOut(register, start_addr, number):
            if register == 1:
                # print("will to get bit")
                return self.__getBit(start_addr, number)
            elif register == 3:
                # print("will to get byte")
                return self.__getByte(start_addr, number)
        else:
            return False


if __name__ == '__main__':
    a = Modbusdb_moudle()
    a.init(
        "0070FFFFFFFFFFFF000300000000000000000000000000000000000000000000000000000000000003E1000F07C1002008360009")
    c = int("0836", 16)
    a.get_data(3, c, 8)
    a.set_data(6, c, "1234")
    a.get_data(3, c, 8)

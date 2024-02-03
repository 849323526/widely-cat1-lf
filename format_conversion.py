import ubinascii, ustruct


class Format_con(object):
    @staticmethod
    def listToString(_list):
        return ''.join(_list)

    @staticmethod
    def intListToHexString(_list):
        string = ""
        tf = "%02d"
        # if length == 2:
        #     tf = "%02d"
        # elif length == 4:
        #     tf = "%04d"
        for i in _list:
            # data += tf % int(hex(i).replace("0x", ''))
            string += (hex(i) if len(hex(i)) == 4 else hex(i).replace("0x", "0x0"))
        return string.replace("0x", '').upper()

    @staticmethod
    def bytesToHexString(byte):
        """

        :param byte: 接收一串bytes，转成string形式的hex
        :return: 将返回一串字符串Hex形式
        """
        return ''.join(['%02X' % b for b in byte])

    @staticmethod
    def bytesTointList(byte):
        length = len(byte)
        return list(ustruct.unpack('B' * length, byte))

    @staticmethod
    def StringToSendbytes(string):
        return ubinascii.unhexlify(string)

    @staticmethod
    def binaryToHexbytes(byte):
        return ubinascii.hexlify(byte)

    @staticmethod
    def HexStringToList(hex_string):
        """

        :param hex_string:接受为string形式的Hex
        :return:会返回一个列表，里面均为hex
        """
        if len(hex_string) % 2 == 0:
            hex_list = []
            k = 0
            for i in range(len(hex_string) // 2):
                hex_list.append(int(hex_string[k:k + 2], 16))
                k += 2
            return hex_list
        else:
            print("Error len!")
            return None

    @staticmethod
    def HexStringToAscii(hex_string):
        if len(hex_string) % 2 == 0:
            ascii_array = ""
            k = 0
            for i in range(len(hex_string) // 2):
                ascii_array += chr(int(hex_string[k:k + 2], 16))
                k += 2
            return ascii_array
        else:
            print("Error len!")
            return ""

    @staticmethod
    def stringToAscii_hex(string):
        """

        :param string:接收一串字符串，转成Ascii
        :return:返回一个列表，里面均为hex
        """
        hex_list = []
        for i in string:
            hex_list.append(ord(i))
        return hex_list

    @staticmethod
    def print_hexList(lists):
        """
        This is to print list data, display hex data
        :param lists:
        """
        print('|', end=' ')
        for i in lists:
            # print("0x%02X" % i, end=' ,')
            print("%02X" % i, end=' ')
        print('|')


if __name__ == '__main__':
    a = Format_con()
    # print(a.intListToHexString([102, 98, 48, 51, 48, 48, 48, 48, 48, 48, 48, 54, 100, 49, 57, 50]))
    # print(a.bytesToHexString(b"\x1e\xc6gq\xb3\xa9\xac>\xa4\xc4O\x00\x9eTW\x97\xd4.\x9e}Bo\xff\x82u\x89Th\xfe'\xc6\xcd"))
    print(a.bytesToHexString(b'\xaa\xbb'))
    # print(a.print_hexList(a.stringToAscii_hex("HB")))
    # print(a.print_hexList(a.HexStringToList("DB504D30010111")))
    # print(a.print_hexList(a.HexStringToList("751c1e4b5b1d000d81fe0101000801000000003f38fd2cd709")))
    # print(a.HexStringToList('0029'))
    # print(a.HexStringToList("A0504D30010111"))

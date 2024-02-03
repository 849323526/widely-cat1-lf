import ubinascii


class Base64_module(object):
    @staticmethod
    def get_base64(lists):
        """
        This is encode data to base64
        :param lists:Must be a hex list(not in string!)
        :return: Will return a string
        """
        string = ""
        for i in lists:
            string += (hex(i) if len(hex(i)) == 4 else hex(i).replace("0x", "0x0"))
        return ((ubinascii.b2a_base64(ubinascii.unhexlify(string.replace("0x", '')))).decode()).replace("\n", ".")

    @staticmethod
    def base64_decode(string):
        """
        This is decode base64 data function
        :param string:Must be a string
        :return: return string
        """
        try:
            return ubinascii.hexlify(ubinascii.a2b_base64(string)).decode()
        except Exception as e:
            print("base64 decode error!:%s " % e)
            return False


if __name__ == '__main__':
    a = Base64_module()
    print(a.base64_decode("AQYgAAAgg9I="))

import ujson, _thread


class Flash_module(object):
    def __init__(self, model, version):
        self.path = "/usr/flash.json"
        self.flash_map = {}
        self.__model = model
        self.__version = version

    def write_dataToFlash(self, dict_data):
        """
        This is the module that writes data to flash
        :param dict_data:Must be a dict type
        """
        with open(self.path, 'w') as f:
            f.write(ujson.dumps(dict_data))

    def get_flashData(self):
        """
        This is the module that fetches data from flash
        :return:Will be return data in json
        """
        with open(self.path, 'r') as f:
            flash_data = ujson.loads(f.read())
        return flash_data.items()

    def creat_flashFile(self):
        """
        This is the module for creating flash files
        """
        self.flashData_init()
        with open(self.path, "w") as f:
            f.write(ujson.dumps(self.flash_map))
        self.flash_map = {}

    def check_flashFileExist(self):
        """
        This is the module to check if there is a flash file during initialization
        :return:If it doesn't exist, then return False
                If it exists, then return True
        """
        try:
            with open(self.path, "r"):
                pass
        except:
            return False
        else:
            return True

    def flashData_init(self):
        """
        This is to initialize the flash data module
        """
        self.flash_map["SN"] = ""
        self.flash_map["ICCID"] = ""
        self.flash_map["MODEL"] = self.__model
        self.flash_map["VERSION"] = self.__version
        self.flash_map["TC_DOMAIN"] = "tc.pmk-pro.com"
        self.flash_map["TC_PORT"] = 58021
        self.flash_map["UPDATE_DOMAIN"] = "pmkcx.cn"
        self.flash_map["UPDATE_PORT"] = 20006
        self.flash_map["SERIAL_BAUD"] = [9600, 'n', 8, 1]  # 硬件控制流（0 – FC_NONE， 1 – FC_HW）
        self.flash_map["REG_PACKET"] = ""
        self.flash_map["REG_ACK"] = ""
        self.flash_map["HB"] = ""
        self.flash_map["HB_ACK"] = ""

    def main(self):
        """
        If the flash file does not exist, it will be created, if it exists, the flash data will be returned
        :return:Will be return Flash data
        """
        # return self.flash_map
        if not self.check_flashFileExist():
            self.flashData_init()
            return self.flash_map.items()
            # self.creat_flashFile()
        return self.get_flashData()


if __name__ == '__main__':
    print(_thread.get_heap_size())
    a = Flash_module()
    b = a.main()
    print(b)
    print(_thread.get_heap_size())

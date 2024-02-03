from manual_ota_updater import ManualOta
from mission import set_mission, Task

MK_OTA = ManualOta()


class SpecRegisterInside:  # start register is 0xFF00
    mk_update_reg = 0


class Doing:
    @staticmethod
    def mk_update(i_value):
        if i_value:
            return MK_OTA.start_update()
        else:
            return MK_OTA.start_reduction()


class SpecData(object):
    def __init__(self, *f_mem):
        if f_mem:
            self.__mem_db = f_mem[0]
            if MK_OTA.back_up_file_in_flash:
                print("[SPEC]backup file in flash, will set task")
                self.__mem_db.main([0x01, 0x06, 0xFF, SpecRegisterInside.mk_update_reg, 0x00, 0x01, 0xFF, 0xFF])

    def modbus_analy(self, s_data):
        i_register = int(s_data[4:8], 16) & 0xFF  # get low address
        i_value = int(s_data[8:12], 16)
        if i_register == SpecRegisterInside.mk_update_reg:
            return Doing.mk_update(i_value)
        else:
            return False

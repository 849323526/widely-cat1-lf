import ujson, uos

UPDATE_MODEL = "mk-update-lf"
NOT_UPDATE_MODEL = "none"


def flash_json_read(s_path):
    with open(s_path, "r") as f:
        flash_data = ujson.loads(f.read())
    return flash_data


def flash_json_write(s_path, dict_data):
    with open(s_path, 'w') as f:
        f.write(ujson.dumps(dict_data))


def flash_json_delete(s_path):
    uos.remove(s_path)


class ManualOta(object):
    def __init__(self):
        from flash import Flash_module
        from start import Power, THREAD
        self.__flash = Flash_module('', '')
        self.__flash_original_path = self.__flash.path
        self.__flash_back_up_path = self.__flash_original_path.replace("flash.json", "backup.json")

        self.back_up_file_in_flash = False

        self.__power = Power
        self.__thread = THREAD

        self.__get_status()
        if self.back_up_file_in_flash:
            print("***lock update***")
            self.__lock_update()

    def __power_restart(self, *args):
        self.__power.power_restart(10)

    def __start_power_restart(self):
        self.__thread.start_new_thread(0, self.__power_restart)

    def __lock_update(self):
        flash_json = flash_json_read(self.__flash_original_path)
        flash_json["MODEL"] = NOT_UPDATE_MODEL
        flash_json_write(self.__flash_original_path, flash_json)

    def __unlock_update(self):
        flash_json = flash_json_read(self.__flash_original_path)
        flash_json["MODEL"] = UPDATE_MODEL
        flash_json["VERSION"] = "0.0.0"
        flash_json_write(self.__flash_original_path, flash_json)

    def __get_status(self):
        self.__flash.path = self.__flash_back_up_path
        if self.__flash.check_flashFileExist():
            print("***Backup Active!***")
            self.back_up_file_in_flash = True
            self.__flash.path = self.__flash_original_path
        else:
            print("***Backup does not exist!***")
            self.back_up_file_in_flash = False
            self.__flash.path = self.__flash_original_path

    def __start_new_model_update(self):
        self.__get_status()
        if not self.back_up_file_in_flash:
            flash_data = flash_json_read(self.__flash_original_path)
            uos.rename(self.__flash_original_path, self.__flash_back_up_path)
            flash_data["MODEL"] = UPDATE_MODEL
            flash_data["VERSION"] = "0.0.0"
            flash_json_write(self.__flash_original_path, flash_data)
            return True
        else:
            print("***Unlock model, will update***")
            self.__unlock_update()
            return True

    def __reduction_model(self):
        self.__get_status()
        if self.back_up_file_in_flash:
            flash_json_delete(self.__flash_original_path)
            uos.rename(self.__flash_back_up_path, self.__flash_original_path)
            return True
        else:
            return True

    def start_update(self):
        if self.__start_new_model_update():
            self.__start_power_restart()
            return True
        else:
            return False

    def start_reduction(self):
        if self.__reduction_model():
            self.__start_power_restart()
            return True
        else:
            return False

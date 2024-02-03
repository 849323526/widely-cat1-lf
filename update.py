import uos, ujson, app_fota, utime, ubinascii, uhashlib
from misc import Power

from update_server import Link_udServer


def power_restart_delay(*args):
    if args:
        print("Will restart in %s seconds" % args[0])
        utime.sleep(args[0])
    else:
        print("Will restart in 0 seconds")
    Power.powerRestart()


class Backup_module(object):
    def __init__(self):
        self.__path = "/usr/"
        self.__updatePath = "/usr/.updater"
        self.__updateFile = "update_info.json"
        self.__updateFileMsg = "download.stat"
        self.__flashFile = "flash.json"
        self.__s_main_file_name = "main."
        self.__s_update_file_name = "update."
        self.__s_updateserver_file_name = "update_server."
        self.__unDelFile = [self.__flashFile, "system_config.json", self.__s_main_file_name, self.__s_update_file_name,
                            self.__s_updateserver_file_name]
        self.__getServerInfo = Link_udServer()
        self.__updateList = []
        self.__dataDict = {}
        self.__newModel = ""
        self.__newVersion = ""
        self.__serverData = ""
        self.__updateSuccessFlag = 1

    # def __clearPythonFile(self):
    #     fileList = uos.listdir(self.__path)
    #     for f in fileList:
    #         if ".py" in f:
    #             if self.__mainName not in f and self.__backUpmodue not in f:
    #                 uos.remove(self.__path + f)

    def __clearFile(self, file, path):
        if file == 1:
            uos.chdir("/usr")
            print(uos.listdir(path))
        else:
            print("join file")
            print(path + file)
            uos.chdir(path + file)
            path += file
            path += "/"
        for i in uos.listdir():
            if (
                    self.__s_main_file_name in i or self.__s_updateserver_file_name in i or self.__s_update_file_name in i or ".json" in i) and file == 1:
                print("NOT DEL %s" % i)
                continue
            elif ".py" in i or ".stat" in i or ".mpy" in i or ".pyc" in i:
                # print("in here")
                # print("%s" % path)
                # print(i)
                uos.remove(path + i)
                print("DEL %s" % i)
            else:
                try:
                    # print("here2 %s" % i)
                    # print(uos.listdir(path))
                    uos.rmdir(path + i)
                    # print(uos.listdir(path))
                except:
                    self.__clearFile(i, path)

        print("Flash file is:")
        print(uos.listdir(path))
        uos.chdir('/')

    def __delPythonFile(self, filename):
        file_list = uos.listdir(self.__path)
        if filename in file_list:
            uos.remove(self.__path + filename)

    def __rewriteFlash(self):
        print("-->In flash")
        with open(self.__path + self.__flashFile, 'r') as f:
            flashData = ujson.loads(f.read())
        flashData["MODEL"] = self.__newModel
        flashData["VERSION"] = self.__newVersion
        print("flash data:\n%s" % flashData)
        with open(self.__path + self.__flashFile, 'w') as f:
            f.write(ujson.dumps(flashData))
        print("-->Flash end!")

    def __writeToFile(self, data):
        with open(self.__path + self.__updateFile, 'a') as f:
            f.write(data)

    def __readFile(self):
        with open(self.__path + self.__updateFile, 'r') as f:
            self.__dataDict = ujson.loads(f.read())
        self.__newModel = self.__dataDict["model"]
        self.__newVersion = self.__dataDict["version"]
        print(self.__dataDict)

    def __xor(self, data):
        hash_obj = uhashlib.md5()
        hash_obj.update(data)
        res = hash_obj.digest()
        xor = self.__bytesToHexString(res).lower()
        return xor

    def __bytesToHexString(self, byte):
        """
        :param byte: 接收一串bytes，转成string形式的hex
        :return: 将返回一串字符串Hex形式
        """
        return ''.join(['%02X' % b for b in byte])

    def __openDownloadFile(self, filename):
        # print(self.__updatePath)
        # print(filename)
        with open(self.__updatePath + filename, 'rb') as f:
            byte_data = f.read()
        return byte_data

    def __getMsgMd5(self, filename):
        for i in self.__serverData:
            if i["filename"] == filename:
                return i["md5"]
        return "0"

    def __md5IsTrue(self, downloadName):
        byte_data = self.__openDownloadFile(downloadName)
        file_md5 = self.__xor(byte_data)
        if file_md5 != self.__getMsgMd5(downloadName.replace("/usr/", "")):
            print(file_md5)
            print(self.__getMsgMd5(downloadName))
            print(len(file_md5))
            print(len(self.__getMsgMd5(downloadName)))
            print("Check md5 False! filename is: %s" % downloadName)
            return False
        return True

    def __downloadFile(self):
        fota = app_fota.new()
        print("Download start!")
        count = 0
        for i in self.__updateList:
            # if self.__unDelFile[2] not in i["file_name"] and self.__unDelFile[3] not in i["file_name"] and self.__unDelFile[4] not in i["file_name"]:
            fota.download(i["url"], i["file_name"])
            print("-->downloadFile %d: %s" % (count, i["file_name"]))
            if not self.__md5IsTrue(i["file_name"]):
                print("***Update false!****")
                self.__updateSuccessFlag = 0
                break
            count += 1
            # else:
            #     print("Not download core file:%s" % i["file_name"])
            #     continue
        print("Download finish!")
        print("Flash file is:")
        print(uos.listdir('/usr'))
        print("Flash updater file is")
        print(uos.listdir('/usr/.updater/usr'))
        utime.sleep(1)
        if self.__updateSuccessFlag:
            fota.set_update_flag()

    def __analysisResult(self, data):
        if "NONE" in data:
            return False
        else:
            data = data.replace("FILES_UPDATE_CHECK OLD ", "")
            # self.__writeToFile(data)
            data = ujson.loads(data)
            self.__serverData = data["urls"]
            self.__newModel = data["model"]
            self.__newVersion = data["version"]
            print(self.__serverData)
            for data_dict in data["urls"]:
                data_dict["file_name"] = self.__path + data_dict["filename"]
                self.__updateList.append(data_dict)
            print(self.__updateList)
            return True

    def __updateModule(self):
        updateMsg = self.__getServerInfo.main()
        if updateMsg:
            if self.__analysisResult(updateMsg):
                self.__clearFile(1, "/usr/")
                self.__downloadFile()
                if self.__updateSuccessFlag:
                    self.__rewriteFlash()
                    # self.__reBackupName()
                    power_restart_delay(10)
            else:
                print("Version is true!")
                return False
        else:
            print("To link server false, will restart")
            return False

    def __printFile(self):
        print(uos.listdir(self.__path))

    def __data_call(self):
        import checkNet
        stagecode, subcode = checkNet.wait_network_connected(15)
        if stagecode != 3 and subcode != 1:
            print("stage code is:%d, sub code is:%d" % (stagecode, subcode))
            # power_restart_delay(300)

    def main(self):
        print("In backup file, will update")
        # self.__printFile()
        # self.__clearFile(1, "/usr/")
        # self.__printFile()
        self.__data_call()
        self.__updateModule()


def update_start():
    utime.sleep(4)
    Backup_module().main()

# if __name__ == '__main__':
#     utime.sleep(5)
#     try:
#         while True:
#             start = Backup_module()
#             start.main()
#             utime.sleep(5)
#             Power.powerRestart()
#     except Exception as e:
#         print(e)
#         utime.sleep(300)
#         Power.powerRestart()

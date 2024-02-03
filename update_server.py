import usocket, utime, ujson


class Link_udServer(object):
    def __init__(self):
        self.__path = "/usr/"
        self.__flashFile = "flash.json"
        self.__sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self.__sock.settimeout(5)
        self.__updateIp = ""
        self.__serverAddr = ""
        self.__serverPort = 0
        self.__sn = ""
        self.__model = ""
        self.__version = ""
        self.__dictData = ""

    def __getServerAddr(self):
        start_time = utime.ticks_ms()
        print("Domain name resolution, please wait...")
        while utime.ticks_diff(utime.ticks_ms(), start_time) < 20000:
            try:
                self.__updateIp = usocket.getaddrinfo(self.__serverAddr, self.__serverPort)[0][-1]
            except:
                utime.sleep(1)
                continue
            else:
                if self.__updateIp != "":
                    print("Success to get update server address:%s" % self.__updateIp[0])
                    return True
                else:
                    utime.sleep(1)
                    continue
        print("Get server address error! please check sim card status!")
        return False

    def __connectToServer(self):
        for i in range(3):
            try:
                self.__sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
                self.__sock.settimeout(5)
                self.__sock.connect(self.__updateIp)
            except Exception as e:
                print("Connection server false!,%s" % e)
                utime.sleep(5)
                continue
            else:
                print("Success to connection update server!")
                return True
        # self.__sock.close()
        # self.__power.power_restart(6)
        return False

    def __sendData(self, data):
        try:
            self.__sock.send(data.encode())
            print("Send to cloud:")
            print(data)
            # self.__print.recv_print(data)
        except Exception as e:
            print("Send data false!, %s" % e)
            # self.__power.power_restart(6)
            return False
        else:
            return True

    def __recvData(self):
        """
        This is the module that receives data from the cloud.
        If RSM is registered, the timeout period is 0 seconds.
        If the registration is completed, the timeout period is None, and it has been waiting for reception.
        :return:If recv data, then return data. If timeout, then return False
        """
        try:
            recv_data = (self.__sock.readline()).decode()
            print("From cloud:\nRecv %d byte:" % len(recv_data))
            print(recv_data)
            # self.__print.recv_print(recv_data)
        except Exception as e:
            print("Recv Error %s" % e)
            return False
        else:
            return recv_data

    def __askServer(self):
        strData = str(self.__dictData).replace(" ", '')
        if not self.__sendData("FILES_UPDATE_CHECK " + strData + '\n'):  # 由于TCP是可靠的，因此1次就行
            return False
        result = self.__recvData()
        if result:
            self.__sock.close()
            return result
        print("TimeOut! will connection to tc")
        self.__sock.close()
        return False

    def __getFlash(self):
        with open(self.__path + self.__flashFile, "r") as f:
            flashData = ujson.loads(f.read())
        return flashData["SN"], flashData["MODEL"], flashData["VERSION"], flashData["UPDATE_DOMAIN"], flashData[
            "UPDATE_PORT"]

    def __init(self):
        self.__sn, self.__model, self.__version, self.__serverAddr, self.__serverPort = self.__getFlash()
        self.__dictData = {"sn": self.__sn, "model": self.__model, "version": self.__version}
        self.__dictData = ujson.dumps(self.__dictData)

    def main(self):
        print("Will link to update server!")
        self.__init()
        if self.__getServerAddr():
            self.__connectToServer()
            return self.__askServer()
        else:
            return False

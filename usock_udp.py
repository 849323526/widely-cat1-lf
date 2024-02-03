import usocket, log, utime
# from global_var import GlobalMap
from tc_info import Tc_info
from print_offset import Pretty_print
# from dev_power import Dev_power
from crc_check import Check_module
from format_conversion import Format_con
from profile_info import Pro_load

log.basicConfig(level=log.INFO)
SYSTEM_LOG = log.getLogger("TC")

RECV_TIMEOUT = 6
BUF_SIZE = 256


class Tc_link(object):
    def __init__(self):
        # self.__memoryData = GlobalMap()
        self.__print = Pretty_print()
        self.__getInfo = Tc_info()
        self.__power = ""
        self.__check_crc = Check_module()
        self.__tool = Format_con()
        self.__sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        self.__sock.settimeout(RECV_TIMEOUT)
        # self.__tcAddr = self.__memoryData.get("SERVER_DOMAIN")
        # self.__tcPort = self.__memoryData.get("PORT")
        self.__tcAddr = ""
        self.__tcPort = ""
        self.__tcIp = ""

    def __get_tcAddr(self):
        """
        This is the domain name resolution module, Obtain the corresponding IP address
        :return:If the domain name is resolved successfully and return the ip address, return True
                If failure, maybe a problem with the network connection, device will be restart
        """
        start_time = utime.ticks_ms()
        SYSTEM_LOG.info("Domain name resolution, please wait...")
        while utime.ticks_diff(utime.ticks_ms(), start_time) < 20000:
            try:
                self.__tcIp = usocket.getaddrinfo(self.__tcAddr, self.__tcPort)[0][-1]
            except:
                utime.sleep(1)
                continue
            else:
                if self.__tcIp != "":
                    # SYSTEM_LOG.info("Success to get address:%s" % self.__tcIp[0])
                    return True
                else:
                    utime.sleep(1)
                    continue
        SYSTEM_LOG.error("Get server address error! please check sim card status!")
        self.__power.power_restart(300)
        return False

    def __connectToServer(self):
        """
        This is the connection server module, If the connection fails for 3 times, will be restart
        :return:If connection server ok, then return True, else device will be restart
        """
        for i in range(3):
            try:
                self.__sock.connect(self.__tcIp)
            except Exception as e:
                SYSTEM_LOG.info("Connection false!,%s" % e)
                utime.sleep(5)
                continue
            else:
                SYSTEM_LOG.info("Success to connection tc!")
                return True
        self.__sock.close()
        self.__power.power_restart(300)
        return False

    def __check_packet(self, data):
        if data:
            data = self.__tool.bytesToHexString(data)
            if self.__check_crc.main(data):
                # self.__memoryData.set_map("PACKET", data)
                loadToMemory = Pro_load(data)
                loadToMemory.main()
                return True
            else:
                return False
        else:
            return False

    def __sendData(self, data):
        try:
            self.__sock.send(data.encode())
            print("Send data:")
            self.__print.printString(data)
        except OSError as e:
            SYSTEM_LOG.error("Send data false!, %s" % e)
            return False
        else:
            return True

    def __recvData(self):
        try:
            recv_byteData = self.__sock.recv(BUF_SIZE)
            recv_data = recv_byteData.decode()
            # data = self.sock.recv(256)
            print("Recv %d byte:" % len(recv_data))
            self.__print.printString(recv_data)
        except Exception as e:
            SYSTEM_LOG.error("Not data recv!, %s" % e)
            # return "RECV Error"
            return False
        else:
            return recv_byteData

    def __regToTc(self):
        for i in range(3):
            if not self.__sendData(self.__getInfo.main()):
                utime.sleep(5)
                continue
            if self.__check_packet(self.__recvData()):
                return True
            utime.sleep(5)
        SYSTEM_LOG.error("Reg to tc server fail")
        self.__sock.close()
        SYSTEM_LOG.warning("Sock close!")
        self.__power.power_restart(300)
        return False

    def __init(self):
        from start import Power, Global_map
        self.__power = Power
        self.__memoryData = Global_map
        self.__tcAddr = self.__memoryData.get("TC_DOMAIN")
        self.__tcPort = self.__memoryData.get("TC_PORT")

    def main(self):
        SYSTEM_LOG.info("Tc module success to running!")
        self.__init()
        self.__get_tcAddr()
        self.__connectToServer()
        if self.__regToTc():
            print("\n*Connect to the Tc server finish*\n")
            self.__sock.close()
            return True
        else:
            self.__sock.close()
            return False

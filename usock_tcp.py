"""
下面两个全局变量是必须有的，用户可以根据自己的实际项目修改下面两个全局变量的值，
在执行用户代码前，会先打印这两个变量的值。
"""
import usocket, log, utime

from print_offset import Pretty_print
from rsm_info import Creat_info
from mission import set_mission
# from main import Global_map, Power, Watch_dog

# from dev_power import Dev_power

log.basicConfig(level=log.INFO)
SYSTEM_LOG = log.getLogger("SOCKET")
HB_TYPE = 0
HB_SEND_TIME = 60
RECV_TIMEOUT = 6
# BUF_SIZE = 256
CONNECT_ID = []
RANDOM_BUF = []
FUNCTION_TYPE = []

NW_READY = 1

SEND_FLAG = 0
DATA_QUEUE = []

WATCH_DOG = False
WATCH_DOG_SLEEP = True
FEED_TIME = 30
# SOCKET = ""


def print_error(value):
    msg = "IOT REPLY MODBUS ERROR "
    if value == 4:
        print(msg + str(value))


class Rsm_link(object):
    """
    This is IoT link modules, has some functions
    include get address, register, send data, receive data, send heartbeat
    """
    def __init__(self):
        # global SOCKET
        # SOCKET = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
        self.reg_module = Creat_info()
        self.pre_print = Pretty_print()
        self.__sock = ""  # TCP
        self.__sock_addr = ""
        self.__wd = ""
        self.__recv_time = 0
        self.__error_count = 0

    @staticmethod
    def set_NwStatus(status):
        global NW_READY
        NW_READY = status

    @staticmethod
    def build_sendMission(string_data):
        global SEND_FLAG, DATA_QUEUE
        SEND_FLAG = 1
        DATA_QUEUE.append(string_data)
        # print("Success to get from rs_485 data, will send To cloud")
        # print("SEND_FLAG1: %s" % SEND_FLAG)
        # print("DATA_QUEUE1: %s" % DATA_QUEUE)

    def __delSendQueue(self):
        global SEND_FLAG, DATA_QUEUE
        SEND_FLAG = 0
        DATA_QUEUE.pop(0)

    def packet(self, string_data):
        if len(string_data) == 6:
            print_error(4)
        # print("Cnt -> [%s]" % SEND_FLAG)
        return self.reg_module.build_payData(string_data, CONNECT_ID, RANDOM_BUF, FUNCTION_TYPE)

    def get_addr(self):
        # print("RSM IP: %s" % self.__memoryData.get("IP"))
        # print("RSM PORT: %s" % self.__memoryData.get("PORT"))
        # print("RSM IP: %s" % self.__memoryData.get("RSM_IP"))
        # print("RSM PORT: %s" % self.__memoryData.get("RSM_PORT"))
        self.__sock_addr = (self.__memoryData.get("RSM_IP"), self.__memoryData.get("RSM_PORT"))

    def connect_server(self):
        """
        This is the connection server module, If the connection fails for 3 times, will be restart
        :return:If connection server ok, then return True, else device will be restart
        """
        for i in range(3):
            try:
                # self._sock = SOCKET
                self.__sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
                self.__sock.settimeout(RECV_TIMEOUT)
                self.__sock.connect(self.__sock_addr)
            except Exception as e:
                SYSTEM_LOG.info("Connection false!,%s" % e)
                utime.sleep(5)
                continue
            else:
                SYSTEM_LOG.info("Success to connection rsm server!")
                return True
        # self._sock.close()
        self.Power.power_restart(180)
        return False

    def hb_thread(self, *args):
        from start import LOCK
        """
        This if to send heartbeaet thread.
        :param args:Args has two param, args[0] is send_data function, args[1] is send data string
        """
        hb_SendTime = HB_SEND_TIME * 1000
        while True:
            sleep_time = utime.ticks_diff(utime.ticks_ms(), self.__recv_time)
            if sleep_time >= hb_SendTime:
                # if NW_READY:
                try:
                    LOCK.acquire()
                    args[0](args[1])
                except Exception as e:
                    print("HB Error:%s" % e)
                    self.Power.power_restart(180)
                    break
                finally:
                    self.__recv_time = utime.ticks_ms()
                    LOCK.release()
                # else:
                #     print("in hb, stop")
            else:
                utime.sleep((hb_SendTime - sleep_time) // 1000)

    def hb_start(self):
        """
        This is to create a heartbeat thread
        if HB_TYPE == 1, then send normal heartbeat, but will consume more flow
        if HB_TYPE == 0, then will be send NOP, consume less flow
        """
        from start import THREAD
        if HB_TYPE:
            THREAD.start_new_thread(512, self.hb_thread, self.send_data,
                                    self.reg_module.build_hbData(CONNECT_ID))
        else:
            THREAD.start_new_thread(512, self.hb_thread, self.send_data, "NOP.\n")

    # def recv_thread(self, *args):
    #     while True:
    #         if not self.judgment_data(self.recv_data()):
    #             utime.sleep(1)
    #             # self._sock.close()
    #             self.send_data("BYE.\n")
    #             self.Power.power_restart(6)

    def recv_thread(self, *args):
        while True:
            if not args[1](args[0]()):
                utime.sleep(1)
                # self._sock.close()
                args[2]("BYE.\n")
                self.Power.power_restart(6)

    def recv_start(self):
        from start import THREAD
        THREAD.start_new_thread(0, self.recv_thread, self.recv_data, self.judgment_data, self.send_data)

    def print_memory(self):
        # from start import Global_map
        from location import getLocation
        # from base64_module import Base64_module
        # import ujson
        Location = getLocation()
        print(self.__memoryData.get("all"))
        d_info = Location.find_all_info_main(self.__memoryData.get("all"))
        print(d_info)
        return Location.jsonToBase64(d_info)

    def judgment_data(self, data):
        """
        This is the module that analyzes the received data,
        and performs judgment operations based on the received information
        :param data:Data from the recv_data module, and must be a string
        :return:If the operation is successful, then return True,
                If receive some specific information, return false and dev restart
        """
        if data == 0:
            return True
        elif "PAY" in data:
            # print(data)
            packet = self.reg_module.unpacket_pay(data)
            # self.send_data("PAY BtIDt3kgAgUBgwRA8wDvGtk=.\n")
            if packet == False:
                print("From cloud to get packet error")
                self.send_data("PAY [ERROR]RECEIVEpacket:%s.\n" % data.replace(" ", "#"))
                # self.send_data("BYE.\n")
                return False
            elif packet == True:
                return True
            else:
                global RANDOM_BUF, FUNCTION_TYPE
                # self.__wd.set_wdStatus(True, 60)
                RANDOM_BUF = packet[1]
                FUNCTION_TYPE = packet[2]
                set_mission(2, packet[0])
                return True

        elif "REG-ACK" in data:
            global CONNECT_ID
            CONNECT_ID = self.reg_module.get_connectionCode(data)
            # self.__memoryData.set_map("CONNECT_ID", self.CONNECT_ID)
            if CONNECT_ID:
                return True
        elif "REG-NACK" in data:
            self.send_data("PAY [ERROR]RECEIVEREG-NACK.\n")
            return False
        elif "REG" in data:
            return True
        elif "NOP-ACK" in data:
            return True
        elif "NOP" in data:
            self.send_data("NOP-ACK.\n")
            return True
        elif "getSimInfo" in data:
            self.send_data("INFO " + self.print_memory() + ".\n")
            return True
        elif "BYE" in data:
            self.send_data("PAY [ERROR]RECEIVEBYE.\n")
            return False
        elif "ERROR" in data:
            self.send_data("PAY [ERROR]RECEIVEERROR.\n")
            return False
        else:
            print("Recv unknow data")
            print(data)
            self.send_data("PAY [UnKnowData]RECEIVE%s.\n" % data)
            return True

    def send_data(self, data):
        """
        This is the module that sends data to the cloud, accepting a string parameter
        :param data:Must be a string
        :return:If send OK, then return True.If send error,then device restart(maybe network or cloud connection failed)
        """
        try:
            self.__sock.send(data.encode())
            print("Send to cloud:")
            self.pre_print.printString(data)
        except Exception as e:
            SYSTEM_LOG.error("Send data false!, %s" % e)
            self.Power.power_restart(180)
            return False
        else:
            return True

    def recv_data(self):
        """
        This is the module that receives data from the cloud.
        If RSM is registered, the timeout period is 0 seconds.
        If the registration is completed, the timeout period is None, and it has been waiting for reception.
        :return:If recv data, then return data. If timeout, then return False
        """
        # global SOCKET
        # utime.sleep(2)
        try:
            # recv_data = (self._sock.recv(BUF_SIZE)).decode()
            # recv_data = SOCKET.recv(BUF_SIZE)
            recv_data = (self.__sock.readline()).decode()
            # recv_data = recv_data.decode()
            print("From cloud:\nRecv %d byte:" % len(recv_data))
            self.pre_print.printString(recv_data)
        except OSError as e:
            if self.__error_count == 100:
                self.Power.power_restart(0)
            if str(e) == '11':
                return 0
                # pass
            elif str(e) == '9':
                print("OS_ERROR, %s" % e)
                return 0
            elif str(e) == '0':
                print("[%s]OS_ERROR, but ignore the error" % e)
                self.__error_count += 1
                return 0
            elif str(e) == '110':
                print("[%s]OS_ERROR, read timeout!" % e)
                self.send_data("PAY [OSERROR]RECEIVETIMEOUT %s.\n" % e)
                return "ERROR"
            else:
                import _thread, gc
                self.send_data("PAY [OSERROR]RECEIVE%s.\n" % e)
                SYSTEM_LOG.error("OS_ERROR!, %s" % e)
                print("System remaining memory %s" % _thread.get_heap_size())
                print("The allocated heap RAM bytes are %s" % gc.mem_alloc())
                print("The remaining heap RAM bytes are %s\n" % gc.mem_free())
                return "ERROR"
                # self.judgment_data("ERROR")
        else:
            # self.judgment_data(recv_data)
            self.__recv_time = utime.ticks_ms()
            return recv_data

    def regToRsm(self):
        """
        This is the module that sends the registration package to RSM
        If no reply is received, the sending will be repeated 3 times, if all fail, then restart
        :return:If REG-ACK is received, then return True, else device will be restart
        """
        if self.send_data(self.reg_module.build_regData()):
            if self.judgment_data(self.recv_data()):
                return True
        # self._sock.close()
        print("Time out! will close connection!")
        self.send_data("BYE.\n")
        SYSTEM_LOG.warning("Sock close!")
        self.Power.power_restart(180)
        return False

    def linkToRsm(self):
        from start import Global_map, Power, Watch_dog
        self.Power = Power
        self.__memoryData = Global_map
        self.__wd = Watch_dog
        self.get_addr()
        self.connect_server()
        SYSTEM_LOG.info("Try to link RSM..")
        if self.regToRsm():
            print("\n*Connect to the Rsm server finish*\n")
            self.hb_start()
            self.__sock.settimeout(None)
            self.recv_start()

    def main(self):
        """
        This is the main program module of TCP connection
        """
        if SEND_FLAG:
            # print("here 8, %s" % utime.ticks_ms())
            self.send_data(self.packet(DATA_QUEUE[0]))
            # print("Remaining count is %d " % SEND_QUEUE)
            self.__delSendQueue()
            # print("Iot send end!")
            # print("SEND_FLAG2 is %s" % SEND_FLAG)
            # print("DATA_QUEUE2 is %s" % DATA_QUEUE)
            # if not SEND_FLAG:
            #     print("watch dog start")
            # self.__wd.set_wdStatus(False, FEED_TIME)
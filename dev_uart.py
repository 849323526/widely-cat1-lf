from machine import UART


class Main_uart(object):
    def __init__(self):
        self.__memory_data = ""
        # print("here")
        # print(self.__memory_data.get("all"))
        self.__uartPort = UART.UART2  # 0 = DEBUG, 1 = BT, 2 = MAIN, 3 = USB CDC
        self.__serial_conf = ""
        self.__buadrate = ""
        self.__parity = ""
        self.__databits = ""
        self.__stop_bit = ""
        self.__uart = ""
        self.__bytes_timeoutMs = ""

    def __init(self):
        from start import Global_map
        self.__memory_data = Global_map
        self.__serial_conf = self.__memory_data.get("SERIAL_BAUD")
        print("get flash baud is %s" % self.__serial_conf)
        self.__buadrate = self.__serial_conf[0]
        if self.__serial_conf[1] == 'n':
            self.__parity = 0
        elif self.__serial_conf[1] == 'e':
            self.__parity = 1
        elif self.__serial_conf[1] == 'o':
            self.__parity = 2
        else:
            print("Flash buadrate Error")
        self.__databits = self.__serial_conf[2]
        self.__stop_bit = self.__serial_conf[3]
        # self.__flowctl = self.__serial_conf[4]
        self.__uart = ""
        if self.__parity == 0:
            self.__bytes_timeoutMs = (1 + self.__stop_bit + self.__databits) / self.__buadrate * 1000
        else:
            self.__bytes_timeoutMs = (1 + self.__stop_bit + self.__databits + 1) / self.__buadrate * 1000

    def build_uart_conf(self):
        self.__init()
        self.__uart = UART(self.__uartPort, self.__buadrate, self.__databits, self.__parity, self.__stop_bit, 0)
        self.__uart.control_485(UART.GPIO1, 1)
        return self.__uart, self.__bytes_timeoutMs

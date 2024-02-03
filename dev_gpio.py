from machine import Pin


class Control485_module(object):
    def __init__(self):
        self.__rs485_control = Pin(Pin.GPIO1, Pin.OUT, Pin.PULL_DISABLE, 0)  # GPIO1 – 引脚号10


    def set_rs485Send(self):
        # print("reads1 is %d" % self.__rs485_control.read())
        self.__rs485_control.write(1)
        # print("reads2 is %d" % self.__rs485_control.read())

    def set_rs485Recv(self):
        # print("readr1 is %d" % self.__rs485_control.read())
        self.__rs485_control.write(0)
        # print("readr2 is %d" % self.__rs485_control.read())


class Led_module(object):
    def __init__(self):
        self.__led_blue = Pin(Pin.GPIO28, Pin.OUT, Pin.PULL_DISABLE, 1)
        self.__led_red = Pin(Pin.GPIO27, Pin.OUT, Pin.PULL_DISABLE, 1)

    def led_r_ligth(self):
        self.__led_red.write(1)

    def led_r_quench(self):
        self.__led_red.write(0)

    def led_b_light(self):
        self.__led_blue.write(1)

    def led_b_quench(self):
        self.__led_blue.write(0)
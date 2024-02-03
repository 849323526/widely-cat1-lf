import utime

ORDER_QUEUE = []
MISSION_QUEUE = []
TIMER_FLAG = 1


# ------TASK---------#
class Task:
    UART_RECEIVE = 1
    IOT_RECEIVE = 2
    FWD_MODEL = 3
    IOT_ASK_SLAVE = 4
    UART_TO_SLAVE = 5
    THREAD_READ_TO_UART = 6
    IOT_WRITE_TO_UART = 7
    IOT_WRITE_SPECIAL_REG = 8
    MK_TO_MEM = 9
    THREAD_WRITE_TO_UART = 10
    DEV_OTA = 20


def set_mission(order, data_list):
    global ORDER_QUEUE, MISSION_QUEUE, TIMER_FLAG
    ORDER_QUEUE.append(order)
    MISSION_QUEUE.append(data_list)
    if order == 1:
        TIMER_FLAG = 0
    else:
        TIMER_FLAG = 1


def set_timerFlag(flag):
    global TIMER_FLAG
    TIMER_FLAG = flag


class UartConfig:
    time_out = 2000  # 2s


class Ms_module(object):
    def __init__(self, uart_conf):
        from crc_check import Check_module
        from print_offset import Pretty_print
        from format_conversion import Format_con
        from usock_tcp import Rsm_link
        from dev_gpio import Led_module
        from timer_test import Timers
        from start import Global_map, GPIO
        from modbus_ins import Modbusins_module
        from admin_reg import SpecData
        self.__crc_check = Check_module()
        self.__print = Pretty_print()
        self.__tool = Format_con()
        self.__set_rs485 = GPIO
        self.__mode = Global_map.get("MODE")
        self.__pfAddr = int(Global_map.get("DEV_ADDR"), 16)
        self.__interval = Global_map.get("INTERVAL")
        try:
            if Global_map.get("SERIAL_BAUD")[0] <= 1200:
                UartConfig.time_out = 5000
        except:
            print("[TASK INIT]Baud get error")
        print("[TASK INIT]Uart time out is:%d" % UartConfig.time_out)
        self.__mode = Global_map.get("MODE")
        if self.__mode == "FWD":
            self.__task_id = Task.FWD_MODEL
        elif self.__mode == "SLAVE":
            self.__task_id = Task.IOT_ASK_SLAVE
        else:
            self.__task_id = Task.FWD_MODEL
        self.__mbOrder = Modbusins_module()
        self.__spec_data = SpecData(self.__mbOrder)
        self.__led = Led_module()
        self.__timer = Timers()
        self.__uart = uart_conf
        self.__count = 0
        self.__iot = Rsm_link.build_sendMission
        self.__led_count = 0

    def __led_flash(self, args):
        if self.__led_count % 2 == 0:
            self.__led.led_r_ligth()
        else:
            self.__led.led_r_quench()
        self.__led_count += 1
        if self.__led_count == 6:
            self.__led_count = 0
            self.__timer.timer_stop(3)

    def __check_addr(self, devAddr):
        if devAddr == self.__pfAddr:
            return True
        else:
            return False

    def check_crc(self, dataBuf):
        if self.__crc_check.main(dataBuf):
            self.__tool.print_hexList(dataBuf)
            self.__led.led_r_quench()
            return True
        else:
            return False

    def separate_list(self, data):
        if len(data) % 16 == 0:
            for i in range(len(data) // 16):
                self.__count += 1
                i *= 16
                set_mission(self.__task_id, data[i:i + 16])
        else:
            self.__count += 1
            set_mission(self.__task_id, data)

    def wait_rtData(self):
        start_time = utime.ticks_ms()
        while TIMER_FLAG:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > UartConfig.time_out:
                return False
            utime.sleep(0.1)
        set_timerFlag(1)
        return True

    def __uart_write(self, b_data):
        self.__uart.write(b_data)

    def sendToUart(self, data):
        print("Send To uart:")
        print('|' + data + '|')
        self.__uart_write(self.__tool.StringToSendbytes(data))
        if self.__mode != "SLAVE":
            if self.wait_rtData():
                print("Cnt -> [%d]" % self.__count)
                self.__count -= 1
                self.__led.led_r_quench()
                recv_data = self.__tool.bytesToHexString(MISSION_QUEUE[-1])
                print("Recv data:[%s]" % recv_data)
                self.del_cmd(-1)
                if self.__count == 0:
                    self.__timer.timer_start(50, 3, self.__led_flash)
                return recv_data
            else:
                self.__clear_cmd()
                self.__count = 0
                self.__led.led_r_ligth()
                return "01" + hex(int(data[2:4], 16) | 0x80).replace("0x", '') + "04"

    def sendToIot(self, data):
        self.__iot(data)

    def del_cmd(self, inside):
        global ORDER_QUEUE, MISSION_QUEUE
        ORDER_QUEUE.pop(inside)
        MISSION_QUEUE.pop(inside)

    def __clear_cmd(self):
        global ORDER_QUEUE, MISSION_QUEUE
        ORDER_QUEUE.clear()
        MISSION_QUEUE.clear()

    def __check_offset(self, s_data):
        s_offset_h = s_data[4:6].upper()
        if s_offset_h == "FF":
            s_fuc = s_data[2:4]
            s_cloud_data = self.__tool.HexStringToList(s_data)
            if s_fuc == "03":
                self.sendToIot(self.__mbOrder.main(s_cloud_data))
            else:  # 06 or 10
                b_result = self.__spec_data.modbus_analy(s_data)
                if b_result:
                    self.sendToIot(self.__mbOrder.main(s_cloud_data))
                else:
                    self.sendToIot("FB8602")
            return True
        else:
            return False

    def ay_instructions(self):
        """
        The function will analyze mission
        if mission == 1:
            will to print from the rs485 data, and check crc
        elif mission == 2:

        """
        cmd = ORDER_QUEUE[0]
        dataList = MISSION_QUEUE[0]
        self.del_cmd(0)
        if cmd == Task.UART_RECEIVE:
            dataBuf = self.__tool.bytesTointList(dataList)
            if self.check_crc(dataBuf) and self.__mode == "SLAVE" and self.__check_addr(dataBuf[0]):
                set_mission(5, dataList)
        elif cmd == Task.IOT_RECEIVE:
            self.separate_list(dataList)
        elif cmd == Task.FWD_MODEL:
            if not self.__check_offset(dataList):
                self.sendToIot(self.sendToUart(dataList))
            else:
                self.__count -= 1
            utime.sleep_ms(self.__interval)
        elif cmd == Task.IOT_ASK_SLAVE:
            print("[TASK]start IOT_ASK_SLAVE, %s" % utime.ticks_ms())
            if not self.__check_offset(dataList):
                dataBuf = self.__tool.HexStringToList(dataList)
                self.sendToIot(self.__mbOrder.main(dataBuf))
            self.__count -= 1
            print("end mission, %s" % utime.ticks_ms())
        elif cmd == Task.UART_TO_SLAVE:
            # print("cmd is 5")
            print("[TASK]start UART_TO_SLAVE, %s" % utime.ticks_ms())
            # print("data is %s" % dataList)
            dataBuf = self.__tool.bytesTointList(dataList)
            self.sendToUart(self.__mbOrder.main(dataBuf))
            print("end mission, %s" % utime.ticks_ms())

    def main(self):
        """
        The function is handle mission,
        if have a mission, will do something
        """
        if MISSION_QUEUE:
            # print("order: %s" % ORDER_QUEUE)
            # print("mission: %s" % MISSION_QUEUE)
            self.ay_instructions()
            return True

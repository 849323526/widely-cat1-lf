import usys, usocket, log, checkNet, utime, _thread, gc, dataCall, net
from machine import WDT

from global_var import GlobalMap
from timer_test import Timers
from usock_udp import Tc_link
from dev_power import Dev_power
from flash import Flash_module
from qc import Qc_module
from dev_uart import Main_uart
from thread_test import Py_thread
from dev_gpio import Led_module, Control485_module
from crc_module import Modbus_crc16
from format_conversion import Format_con

log.basicConfig(level=log.INFO)
SYSTEM_LOG = log.getLogger("SYSTEM")

LOCK = _thread.allocate_lock()
GPIO = Control485_module()
THREAD = Py_thread()
Global_map = GlobalMap()
Power = Dev_power()
LED = Led_module()
CRC16 = Modbus_crc16()
TIMER = Timers()
TOOL = Format_con()

SERIAL_CONF = ""
rs485_module = ""

LED_STATUS = 0


def getModel(PROJECT_NAME):
    import ure
    return ure.search('( \(.*?\))', PROJECT_NAME).group(1)[2:-1]


def memoryLoad(PROJECT_NAME, PROJECT_VERSION):
    """
    This is to load the data in the flash into the memory
    """
    global Global_map
    flash_data = Flash_module(getModel(PROJECT_NAME), PROJECT_VERSION)
    # flash_data.main()
    # print("In memory load")
    for i in flash_data.main():
        # print(i)
        Global_map.set_map(i[0], i[1])
    Global_map.set_map("PROJECT_NAME", getModel(PROJECT_NAME))
    Global_map.set_map("PROJECT_VERSION", PROJECT_VERSION)
    # print("end!")


def updateJudgment(PROJECT_NAME, PROJECT_VERSION):
    import uos
    if "flash.json" in uos.listdir("/usr/"):
        print("Qc pass, will to update")
        from update import update_start
        memoryLoad(PROJECT_NAME, PROJECT_VERSION)
        print("SN:%s" % Global_map.get('SN'))
        print("ICCID:%s" % Global_map.get('ICCID'))
        update_start()
    else:
        print("Qc not pass, don't to update")


def view_serial(args):
    print(args)
    # print("Port[%d], recv %d" % (args[1], args[2]))
    rs485_module.main(args)


def serialInit():
    from modbus_drv import Md_module
    global rs485_module
    uart_module = Main_uart()
    serial_conf, byte_send_time = uart_module.build_uart_conf()
    rs485_module = Md_module(serial_conf, byte_send_time)
    # print(bytes_timeoutMs)
    # print(SERIAL_CONF)
    serial_conf.set_callback(rs485_module.main)
    # TIMER.timer_start(6, 0, view_serial)
    # serial_conf.set_callback(rs485_module.main)
    return serial_conf, byte_send_time


def linkToTC():
    tc_module = Tc_link()
    if tc_module.main():
        return True
    else:
        return False


def getMemoryStatus():
    while True:
        utime.sleep(180)
        SYSTEM_LOG.info("RAM1 available space is %d(byte)" % gc.mem_free())
        gc.collect()
        SYSTEM_LOG.info("RAM2 available space is %d(byte)" % gc.mem_free())
        SYSTEM_LOG.info("Gc clean OK, next cleaning time is 3 minutes later")
        # SYSTEM_LOG.info("Remaining memory size is %d byte" % _thread.get_heap_size())
        # SYSTEM_LOG.info("RAM used space is %d byte" % gc.mem_alloc())
        SYSTEM_LOG.info("RAM used space is %d byte\n" % gc.mem_alloc())


def led_main():
    """
    This is led thread of control, have 3 kinds status:
    STATUS == 0: LED BLUE and LED RED always light
    STATUS == 1: LED BLUE will fast flash, LED RED always light(until serial recv true crc data will quench)
    STATUS == 2: LED BLUE will slow flash, LED RED always light(until serial recv true crc data will quench)
    """

    def init_led_status():
        LED.led_r_ligth()
        LED.led_b_light()

    def wait_qc_led_status():
        LED.led_r_quench()
        utime.sleep(2)
        LED.led_r_ligth()
        utime.sleep(2)

    def wait_net_led_status():
        LED.led_b_quench()
        LED.led_r_ligth()
        utime.sleep(2)
        LED.led_r_quench()
        LED.led_b_light()
        utime.sleep(2)

    def link_tc_led_status():
        LED.led_b_quench()
        utime.sleep(0.2)
        LED.led_b_light()
        utime.sleep(0.2)

    def link_rsm_led_status():
        LED.led_b_quench()
        utime.sleep(0.5)
        LED.led_b_light()
        utime.sleep(0.5)

    def normal_led_status():
        LED.led_b_quench()
        utime.sleep(2)
        LED.led_b_light()
        utime.sleep(2)

    def ota_led_status():
        LED.led_r_ligth()
        utime.sleep(0.5)
        LED.led_r_quench()
        utime.sleep(0.5)

    def qc_pass():
        LED.led_r_ligth()
        utime.sleep(0.5)
        LED.led_r_quench()
        utime.sleep(0.5)
        LED.led_r_ligth()
        utime.sleep(0.5)
        LED.led_r_quench()
        utime.sleep(0.5)
        LED.led_b_light()
        utime.sleep(0.5)
        LED.led_b_quench()
        utime.sleep(0.5)
        LED.led_b_light()
        utime.sleep(0.5)
        LED.led_b_quench()
        utime.sleep(0.5)

    while True:
        init_led_status()
        while LED_STATUS == 0:
            wait_net_led_status()
        init_led_status()
        while LED_STATUS == 1:
            wait_qc_led_status()
        while LED_STATUS == 2:
            link_tc_led_status()
        while LED_STATUS == 3:
            link_rsm_led_status()
        while LED_STATUS == 4:
            normal_led_status()
        while LED_STATUS == 5:
            ota_led_status()
        while LED_STATUS == 6:
            qc_pass()


def ledInit():
    THREAD.start_new_thread(512, led_main)


class init_module(object):
    def __init__(self, PROJECT_NAME):
        self.timer_module = Timers()
        self.qc_module = Qc_module()
        self.check_net = ""
        self.__s_project_name = PROJECT_NAME

    def timer_gc_start(self):
        THREAD.start_new_thread(1, getMemoryStatus)

    def cb_nw_start(self):
        from check_net import nw_cb
        dataCall.setCallback(nw_cb)

    def __print_info(self):
        self.check_net = checkNet.CheckNetwork(self.__s_project_name, Global_map.get("PROJECT_VERSION"))
        self.check_net.poweron_print_once()
        Power.last_shutdownStatus()

    def __wait_networkReady(self):
        print("Datacall in progress , please wait...")
        stage_code, sub_code = self.check_net.wait_network_connected(30)
        if stage_code != 3 and sub_code != 1:
            print("stage code is:%d, sub code is:%d" % (stage_code, sub_code))
            Power.power_restart(300)
        print("CSQ:%d" % net.csqQueryPoll())

    def main(self):
        global LED_STATUS
        self.__print_info()
        LED_STATUS = 1
        if not self.qc_module.main():
            return False
        LED_STATUS = 0
        self.__wait_networkReady()
        self.cb_nw_start()
        self.timer_gc_start()
        return True


def qcPass(PROJECT_NAME):
    _init = init_module(PROJECT_NAME)
    if not _init.main():
        return False
    else:
        return True


class Watch_dog(object):
    def __init__(self):
        self.__wd_time_out = 60
        self.__wd_is_feed = False
        self.wd = WDT(self.__wd_time_out)
        THREAD.start_new_thread(0, self.__thread_set_wd_feed)

    def __thread_set_wd_feed(self, *args):
        i_feed_time = self.__wd_time_out // 3
        while True:
            self.__wd_is_feed = True
            utime.sleep(i_feed_time)

    def feed(self):
        if self.__wd_is_feed:
            self.wd.feed()
            print("[WD]Feed out, %s" % utime.ticks_ms())
            self.__wd_is_feed = False


def add_rf_to_memory(s_name, s_data):
    global Global_map
    print("%s: %s" % (s_name, s_data))
    Global_map.set_map(s_name, s_data)
    return s_name, s_data


def get_location():
    import net
    tup_buf = net.getCellInfo()
    LTE = tup_buf[2]
    print("***Location get***")
    # print(tup_buf)
    # print("***")
    if LTE:
        l_lte_data = []
        for i in LTE:
            if i[0] == 0:
                l_lte_data = i
                break
        if not l_lte_data:
            l_lte_data = LTE[0]
        add_rf_to_memory("cid", str(l_lte_data[1]))
        add_rf_to_memory("mcc", str(l_lte_data[2]))
        add_rf_to_memory("mnc", str(l_lte_data[3]))
        add_rf_to_memory("tac", str(l_lte_data[5]))
        add_rf_to_memory("rssi", str(l_lte_data[7]))
        add_rf_to_memory("rsrq", str(l_lte_data[8]))
    else:
        add_rf_to_memory("cid", "0")
        add_rf_to_memory("mcc", "0")
        add_rf_to_memory("mnc", "0")
        add_rf_to_memory("tac", "0")
        add_rf_to_memory("rssi", "0")
        add_rf_to_memory("rsrq", "0")
    add_rf_to_memory("CSQ", str(net.csqQueryPoll()))
    print("***")


def start(PROJECT_NAME, PROJECT_VERSION):
    from mission import Ms_module
    from usock_tcp import Rsm_link
    global LED_STATUS
    utime.sleep(5)
    gc.enable()
    updateJudgment(PROJECT_NAME, PROJECT_VERSION)
    ledInit()
    while True:
        memoryLoad(PROJECT_NAME, PROJECT_VERSION)
        if not qcPass(PROJECT_NAME):
            LED_STATUS = 6
            Power.power_restart(1800)
            continue
        LED_STATUS = 2
        linkToTC()
        LED_STATUS = 3
        break

    IOT_MODULE = Rsm_link()
    serial_conf, byte_timeout = serialInit()
    IOT_MODULE.linkToRsm()
    tasks = Ms_module(serial_conf)
    # uart = Md_module(serial_conf, byte_timeout)
    get_location()
    wd = Watch_dog()
    Global_map.del_map("REGISTER")
    LED_STATUS = 4
    # print(Global_map.get('all'))
    gc.collect()
    while True:
        IOT_MODULE.main()
        tasks.main()
        # uart.main()
        wd.feed()

import utime, log, gc

log.basicConfig(level=log.INFO)
RS_LOG = log.getLogger("RS_SERIAL")


class Md_module(object):
    def __init__(self, serial_conf, timeout):
        from mission import set_mission
        from start import TIMER
        self.__char_timeoutMs = round(timeout * 1.5)
        self.__bytes_timeoutMs = round(timeout * 3.5)
        self.__serial = serial_conf
        self.__start_time = 0
        self.__last_len = 0
        self.__tmq = TIMER
        self.__mission = set_mission

    def __clear_buf(self):
        start_time = utime.ticks_ms()
        print("Error data:")
        while True:
            buf_len = self.__serial.any()
            if buf_len:
                print(self.__serial.read(buf_len))
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 35 and not self.__serial.any():
                print("Clear end!")
                break
            else:
                continue

    def __recv_buf(self, bufLen):
        # buf_len = self.__serial.any()
        # print("From rs-485 recv %d bytes" % bufLen)
        # print(self.__serial.read(buf_len))
        data = self.__serial.read(bufLen)
        self.__mission(1, data)

    def recv_data(self):
        while True:
            buf_len = self.__serial.any()
            if not self.__start_time:  # if start_time == 0:  --> init
                last_len = buf_len
                self.__start_time = utime.ticks_ms()
            else:
                diff_time = utime.ticks_diff(utime.ticks_ms(), self.__start_time)
                if diff_time <= self.__char_timeoutMs:
                    if buf_len != last_len:
                        last_len = buf_len
                        self.__start_time = utime.ticks_ms()
                else:
                    if buf_len == last_len:
                        if diff_time <= self.__bytes_timeoutMs:
                            continue
                        else:
                            self.__recv_buf(buf_len)
                            break
                    else:
                        self.__clear_buf()
                        break
        self.__start_time = 0
    #
    # def __int(self):
    #     self.__tmq.timer_start_one_shot(1, 0, self.recv_data)

    def main(self, args):
        """
        The function is check rs485 is not timeout,
        if timeout, will clear the uart buffer
        else will append a mission to the mission module
        """
        # print("In timer %d" % utime.ticks_ms())
        print("Port[%d], recv %d bytes" % (args[1], args[2]))
        self.__recv_buf(args[2])
        # if self.__serial.any():
        #     self.recv_data()


if __name__ == '__main__':
    pass

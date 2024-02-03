from machine import Timer


class Timers(object):
    def __init__(self):
        self.timer0 = Timer(Timer.Timer0)
        self.timer1 = Timer(Timer.Timer1)
        self.timer2 = Timer(Timer.Timer2)
        self.timer3 = Timer(Timer.Timer3)
        self.case = [self.timer0, self.timer1, self.timer2, self.timer3]

    def timer_start(self, millisecond, timer_type, functions):
        """
        This is timers start modules
        :param millisecond:Must be a int type, and millisecond form
        :param timer_type:Specify which timer to start, must be a int type
        :param functions:Is a function pointer
        """
        status = self.case[timer_type].start(period=millisecond, mode=self.case[timer_type].PERIODIC, callback=functions)
        if status == -1:
            print("Error! Tmq %d start error! [%d]" % (timer_type, status))
        else:
            print("Tmq %d success start! [%d]" % (timer_type, status))
            print("millisecond is %d" % millisecond)

    def timer_start_one_shot(self, delay, timer_type, functions):
        status = self.case[timer_type].start(period=delay, mode=self.case[timer_type].ONE_SHOT,
                                             callback=functions)
        if status == -1:
            print("Error! Tmq %d start error! [%d]" % (timer_type, status))

    def timer_stop(self, timer_type):
        """
        This is stop timers function
        :param timer_type:Specify which timer to stop, must be a int type
        """
        self.case[timer_type].stop()

    def timer_allStop(self):
        """
        This is stop all timers function
        """
        for i in self.case:
            self.case[i].stop()


#
# def start(args):
#     print("hallo")
#     print("OK?")


# if __name__ == '__main__':
#     a = Timers()
#     a.timer_start(3000, 1, start)
#     b = 200
#
#     while b > 0:
#         print("i am run")
#         utime.sleep(0.5)
#         b -= 1
#
#     a.timer_stop(1)

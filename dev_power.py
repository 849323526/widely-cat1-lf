from misc import Power
import utime, log

log.basicConfig(level=log.INFO)
SYSTEM_LOG = log.getLogger("POWER")


class Dev_power(object):
    @staticmethod
    def power_restart(*args):
        """
        This is the device restart module
        """
        if len(args):
            delay = args[0]
        else:
            delay = 0
        SYSTEM_LOG.warning("Device will be restart!, delay (%d)s" % delay)
        utime.sleep(delay)
        Power.powerRestart()

    @staticmethod
    def last_shutdownStatus():
        """
        This is the module to get the reason for the last device shutdown
        """
        result = Power.powerDownReason()
        open_result = Power.powerOnReason()
        if result == 1:
            SYSTEM_LOG.info("The reason for the last shutdown was Normal power shutdown")
        elif result == 2:
            SYSTEM_LOG.info("The reason for the last shutdown was Voltage is too high")
        elif result == 3:
            SYSTEM_LOG.info("The reason for the last shutdown was Voltage is too low")
        elif result == 4:
            SYSTEM_LOG.info("The reason for the last shutdown was Over temperature")
        elif result == 5:
            SYSTEM_LOG.info("The reason for the last shutdown was WDT")
        elif result == 6:
            SYSTEM_LOG.info("The reason for the last shutdown was VRTC is low")
        else:
            SYSTEM_LOG.info("The reason for the last shutdown was Unknow, status:%s" % result)
        SYSTEM_LOG.info("PowerOnReason is %s" % open_result)

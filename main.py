import usys, utime, system

system.replSetEnable(1)
# utime.sleep(5)
usys.path.append('/usr')
PROJECT_NAME = "Pumatek Innovation(R) wireless data collector (widely-cat1-lf)"
PROJECT_VERSION = "0.0.0"

if __name__ == '__main__':
    try:
        from start import start
        start(PROJECT_NAME, PROJECT_VERSION)
    except ImportError as e:
        from update import update_start, power_restart_delay
        print("Not file %s" % e)
        update_start()
        power_restart_delay(60)
    except Exception as e:
        print(e)
        from update import power_restart_delay
        power_restart_delay(60)

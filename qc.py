import sim, modem


class Qc_module(object):
    def __init__(self):
        from start import Global_map
        from interaction import UsbInteraction
        from flash import Flash_module
        self.memory_dict = ""
        self.flash_module = Flash_module(Global_map.get("PROJECT_NAME"), Global_map.get("PROJECT_VERSION"))
        self.power = ""
        self.input_sn = UsbInteraction()
        self.sn = ""
        self.iccid = ""
        self.imsi = ""
        self.imei = ""

    def qc_failure(self):
        self.power.power_restart(180)

    def __check_card_info(self, s_sim_name, f_sim_getinfo):
        import utime
        start_time = utime.ticks_ms()
        while f_sim_getinfo() == -1:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 10000:
                print("%s:ERROR" % s_sim_name)
                # print(f_sim_getinfo())
                # print(sim.getIccid())
                break
            # print(f_sim_getinfo())
            utime.sleep(0.3)
        s_sim_info = f_sim_getinfo()
        print("%s:%s" % (s_sim_name, s_sim_info))
        return s_sim_info

    def check_cardStatus(self):
        info = sim.getStatus()
        if info != 1:
            from sc_statusTb import print_scStatus
            import utime
            print_scStatus(info)
            print("Please wait sim card ready...")
            start_time = utime.ticks_ms()
            while sim.getStatus() != 1:
                if utime.ticks_diff(utime.ticks_ms(), start_time) > 10000:
                    print("Sim card time out!")
                    self.qc_failure()
                utime.sleep(0.3)
        print("SIM:Is ready!")

    def check_sim(self):
        self.check_cardStatus()
        # self.check_iccid()
        # self.check_imsi()
        # self.check_imei()
        self.iccid = self.__check_card_info("ICCID", sim.getIccid)
        self.imsi = self.__check_card_info("IMSI", sim.getImsi)
        self.imei = self.__check_card_info("IMEI", modem.getDevImei)
        if self.iccid and self.imsi and self.imei:
            return True
        else:
            self.qc_failure()
            return False

    def write_dataToFlash(self, sn):
        self.memory_dict["SN"] = self.sn = sn
        self.memory_dict["ICCID"] = self.iccid
        self.memory_dict["IMSI"] = self.imsi
        self.memory_dict["IMEI"] = self.imei
        self.flash_module.write_dataToFlash(self.memory_dict)

    def check_sn(self):
        if self.memory_dict["SN"] == "":
            self.write_dataToFlash(self.input_sn.main())
            return False
        print("SN:%s" % self.memory_dict["SN"])
        return True

    # def getFlashData(self):
    #     return self.flash_module.get_flashData()

    def __init(self):
        from start import Power, Global_map
        self.var_module = Global_map
        self.memory_dict = self.var_module.get("all")
        self.power = Power

    def main(self):
        self.__init()
        print("*QC START*")
        self.check_sim()
        if self.check_sn():
            print("*QC END*")
            return True
        else:
            print("*QC READY*")
            return False

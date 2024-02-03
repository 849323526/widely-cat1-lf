import cellLocator


def get_location(*args):
    if len(args) != 0:
        token = args[0]
    else:
        token = "0EcbeZRz777BJH48"
    domain = "www.queclocator.com"
    port = 80
    time_out = 8
    pdp = 1
    location_tup = cellLocator.getLocation(domain, port, token, time_out, pdp)
    if type(location_tup) is tuple:
        return location_tup
    else:
        return False


CSQ = "CSQ"
LOCATION = "Location"
MNC = "mnc"
MCC = "mcc"
TAC = "tac"
CID = "cid"
RSSI = "rssi"
RSRQ = "rsrq"
SIMINFO = "SimInfo"
ICCID = "ICCID"
IMSI = "IMSI"
IMEI = "IMEI"


class getLocation(object):
    def __init__(self):
        self.d_i_csq = {CSQ: "0"}
        self.d_location = {LOCATION: {MNC: "0",
                                      MCC: "0",
                                      TAC: "0",
                                      CID: "0",
                                      RSSI: "0",
                                      RSRQ: "0"}}
        self.d_sim_info = {SIMINFO: {ICCID: "0",
                                     IMSI: "0",
                                     IMEI: "0"}}

    def __combination_dict(self):
        d = {}
        d.update(self.d_i_csq)
        d.update(self.d_location)
        d.update(self.d_sim_info)
        return d

    def __build_siminfo_dict(self, iccid, imsi, imei):
        self.d_sim_info[SIMINFO][ICCID] = iccid
        self.d_sim_info[SIMINFO][IMSI] = imsi
        self.d_sim_info[SIMINFO][IMEI] = imei

    def __build_location_dict(self, mnc, mcc, tac, cid, rssi, rsrq):
        self.d_location[LOCATION][MNC] = mnc
        self.d_location[LOCATION][MCC] = mcc
        self.d_location[LOCATION][TAC] = tac
        self.d_location[LOCATION][CID] = cid
        self.d_location[LOCATION][RSSI] = rssi
        self.d_location[LOCATION][RSRQ] = rsrq

    def find_all_info_main(self, d_memory_buf):
        csq = d_memory_buf[CSQ]
        mnc = d_memory_buf[MNC]
        mcc = d_memory_buf[MCC]
        tac = d_memory_buf[TAC]
        cid = d_memory_buf[CID]
        rssi = d_memory_buf[RSSI]
        rsrq = d_memory_buf[RSRQ]
        iccid = d_memory_buf[ICCID]
        imsi = d_memory_buf[IMSI]
        imei = d_memory_buf[IMEI]

        self.d_i_csq[CSQ] = csq
        self.__build_location_dict(mnc, mcc, tac, cid, rssi, rsrq)
        self.__build_siminfo_dict(iccid, imsi, imei)
        return self.__combination_dict()

    def jsonToBase64(self, json_data):
        import ujson
        from format_conversion import Format_con
        from base64_module import Base64_module
        s_data = ujson.dumps(json_data)
        return Base64_module.get_base64(Format_con.stringToAscii_hex(s_data))

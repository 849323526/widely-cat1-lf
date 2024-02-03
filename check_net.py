
# def reconnectToserver():
#     import checkNet, net, utime
#     from test import PROJECT_NAME, PROJECT_VERSION, IOT_MODULE
#     check_net = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)
#     # net.setModemFun(4)
#     # utime.sleep(2)
#     # if net.setModemFun(1) == 0:
#     print("Wait to dataCall")
#     while True:
#         try:
#             check_net.wait_network_connected()
#         except Exception as e:
#             print(e)
#         else:
#             break
#     print("Try to reconnect rsm server")
#     IOT_MODULE.set_NwStatus(0)


def nw_cb(args):
    """
    The function is check network status callback function, if network not connected!, will power restart!
    """
    pdp = args[0]
    nw_sta = args[1]
    if nw_sta == 1:
        print("*** network %d connected! ***" % nw_sta)
    else:
        import sim
        from sc_statusTb import print_scStatus
        from start import Dev_power
        print("*** network %d not connected! ***" % nw_sta)
        print_scStatus(sim.getStatus())
        Dev_power.power_restart(0)
        # reconnectToserver()
        # print("end")
        # if net.setModemFun(4) == 0:
        #     utime.sleep(2)
        #     if net.setModemFun(1) == 0:
        #         return True
        # print("set error, will be restart")
        # Dev_power.power_restart(6)
        # return False


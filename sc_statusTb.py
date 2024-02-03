def print_scStatus(value):
    """
    The function is sim card status table
    """
    if value == 0:
        print("*** SIM was removed. ***")
    elif value == 1:
        print("*** SIM is ready. ***")
    elif value == 2:
        print("*** Expecting the universal PIN./SIM is locked, waiting for a CHV1 password. ***")
    elif value == 3:
        print("*** Expecting code to unblock the universal PIN./SIM is blocked, CHV1 unblocking password is required. ***")
    elif value == 4:
        print("*** SIM is locked due to a SIM/USIM personalization check failure. ***")
    elif value == 5:
        print("*** SIM is blocked due to an incorrect PCK; an MEP unblocking password is required. ***")
    elif value == 6:
        print("*** Expecting key for hidden phone book entries. ***")
    elif value == 7:
        print("*** Expecting code to unblock the hidden key. ***")
    elif value == 8:
        print("*** SIM is locked; waiting for a CHV2 password. ***")
    elif value == 9:
        print("*** SIM is blocked; CHV2 unblocking password is required. ***")
    elif value == 10:
        print("*** SIM is locked due to a network personalization check failure. ***")
    elif value == 11:
        print("*** SIM is blocked due to an incorrect NCK; an MEP unblocking password is required. ***")
    elif value == 12:
        print("*** SIM is locked due to a network subset personalization check failure. ***")
    elif value == 13:
        print("*** SIM is blocked due to an incorrect NSCK; an MEP unblocking password is required. ***")
    elif value == 14:
        print("*** SIM is locked due to a service provider personalization check failure. ***")
    elif value == 15:
        print("*** SIM is blocked due to an incorrect SPCK; an MEP unblocking password is required. ***")
    elif value == 16:
        print("*** SIM is locked due to a corporate personalization check failure. ***")
    elif value == 17:
        print("*** SIM is blocked due to an incorrect CCK; an MEP unblocking password is required. ***")
    elif value == 18:
        print("*** SIM is being initialized; waiting for completion. ***")
    elif value == 19:
        print("*** Use of CHV1/CHV2/universal PIN/code to unblock the CHV1/code to unblock the CHV2/code to unblock the universal PIN/ is blocked. ***")
    elif value == 20:
        print("*** Invalid SIM card. ***")
    else:
        print("*** Unknow status. ***")
    return value

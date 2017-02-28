import pexpect

def ping(requests_address, ping_times=4, timeout_set=5):
    ping_result = pexpect.spawn("ping -c%s %s" % (str(ping_times), requests_address),timeout=timeout_set)
    ping_result_list = ["9999.99"] * 4
    ping_status = "OK"
    try:
        for line in ping_result:
            perline = line.decode('utf-8')
            if "Usage" in perline:
                ping_status = "Need address"
            if "unknown" in perline or "not known" in perline or "Cannot assign" in perline:
                ping_status = "Unknow server"
            if "Permission" in perline:
                ping_status = "Need Permission"
            if "rtt" in perline:
                ping_result_list = perline[23:-5].split("/",3)
    except pexpect.exceptions.TIMEOUT:
        ping_status = "Time out"
        pass
    finally:
        # RETURN -> ('ping_status', ['min', 'avg', 'max', 'mdev'])
        return ping_status, ping_result_list
from sys import platform
import resource
import psutil


def get_resources():
    # Documentation: https://docs.python.org/3/library/resource.html
    application = {}
    application["ru_utime"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_utime,
                               "description": "time in user mode (float)"}

    application["ru_stime"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_stime,
                               "description": "time in system mode (float)"}

    application["ru_maxrss"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                "description": "maximum resident set size in kb"}

    application["ru_ixrss"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_ixrss,
                               "description": "shared memory size"}

    application["ru_idrss"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_idrss,
                               "description": "unshared memory size"}

    application["ru_isrss"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_isrss,
                               "description": "unshared stack size"}

    application["ru_minflt"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_minflt,
                                "description": "page faults not requiring I/O"}

    application["ru_majflt"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_majflt,
                                "description": "page faults requiring I/O"}

    application["ru_nswap"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_nswap,
                               "description": "number of swap outs"}

    application["ru_inblock"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_inblock,
                                 "description": "block input operations"}

    application["ru_oublock"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_oublock,
                                 "description": "block output operations"}

    application["ru_msgsnd"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_msgsnd,
                                "description": "messages sent"}

    application["ru_msgrcv"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_msgrcv,
                                "description": "messages received"}

    application["ru_nsignals"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_nsignals,
                                  "description": "signals received"}

    application["ru_nvcsw"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_nvcsw,
                               "description": "voluntary context switches"}

    application["ru_nivcsw"] = {"value": resource.getrusage(resource.RUSAGE_SELF).ru_nivcsw,
                                "description": "involuntary context switches"}

    # Documentation at https://pythonhosted.org/psutil/
    system = {}
    system["cpu_count"] = {"value": psutil.cpu_count(),
                           "description": "number of logical CPUs in the system"}

    system["cpu_percent"] = {"value": psutil.cpu_percent(percpu=True, interval=1),
                             "description": "current system-wide CPU utilization as a percentage"}

    system["memory_virtual"] = {"value": psutil.virtual_memory(),
                                "description": "statistics about system memory usage"}

    system["memory_swap"] = {"value": psutil.swap_memory(),
                             "description": "system swap memory statistics"}

    if "win" in platform:
        path = "c:"
    else:
        path = "/"
    system["disk_usage"] = {"value": psutil.disk_usage(path),
                            "description": "disk usage statistics for %s" % path}

    system["disk_io_counters"] = {"value": psutil.disk_io_counters(perdisk=True),
                                  "description": "system-wide disk I/O statistics "}

    system["process_list"] = {"value": {},
                              "description": "running processes on the local machine"}

    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            system["process_list"]["value"][pinfo["pid"]] = pinfo

    resources = {"application": application,
                 "system": system}

    return resources

from functools import wraps
import logging
from Core.request import Request
from Core.exceptions import ConfigException
from enum import Enum

DEFAULTSTARTMSG = "Starting operation {}"
DEFAULTENDMSG = "Ending operation {}"

class OutputType(Enum):
    console_output = 1
    file_output = 2



def receiver_log(level=logging.DEBUG, output_mode:OutputType=1, log_name:str=None, start_msg:str=None, end_msg:str=None):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            name_log = log_name if log_name else func.__module__
            log = logging.getLogger(name_log)
            start_log_msg = start_msg if start_msg else DEFAULTSTARTMSG.format(func.__name__)
            end_log_msg  = end_msg if end_msg else DEFAULTENDMSG.format(func.__name__)
            req = args[1]
            if not isinstance(req, Request):
                raise ConfigException("Request not found")
            
            request_name = " {}".format(str(req))
            if output_mode == 2:
                handler = logging.FileHandler('amuru.log')
                handler.setLevel(level)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                log.addHandler(handler)

            log.log(level, start_log_msg + request_name)
            result = func(*args, **kwargs)
            log.log(level, start_log_msg + request_name)

            return result
        return func_wrapper
    return func_decorator
            

            



# coding: utf-8

class HzTrace(object):
    trace_output_flg = False
    
    @staticmethod
    def get_trace_output():
        return HzTrace.trace_output_flg

    @staticmethod
    def set_trace_output(flg):
        HzTrace.trace_output_flg = flg

    @staticmethod
    def trace_comm_message(msg):
        if(HzTrace.trace_output_flg):
            print(msg)

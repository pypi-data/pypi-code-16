#coding:utf-8
__author__ = 'creeper'

# Must run below code in ipython
# import plotly.graph_objs as go
import sqlite3
# import pandas as pd
# import plotly.plotly as py
from pprint import pprint
import os
from lab.settings import JSON_ROOT,PROJECT_ROOT

# class SuTimedOut(object):
#     def __init__(self):
#         self.db_path = os.path.join(os.path.dirname(PROJECT_ROOT),'db.sqlite3')
#         self.conn = sqlite3.connect(self.db_path)
#         self.df = pd.read_sql_query("SELECT * from lab_analysis_tools_suconnectedtimedout", self.conn)
#         self.conn.close()
#
#     def _getLen(self, x):
#         if len(x) == 0:
#             return 0
#         else:
#             return len(x.split("|"))
#
#     def run(self):
#         unstable_devices = map(self._getLen, self.df.unstable_devices)
#         repeat_devices = map(self._getLen, self.df.repeat_devices)
#         newbird_devices = map(self._getLen, self.df.newbird_devices)
#         trace_unstable = go.Bar(
#             x=self.df.tid,
#             y=unstable_devices,
#             name='unstable',
#             # marker=dict(
#             #     color='rgb(49,130,189)'
#             # )
#         )
#
#         trace_repeat = go.Bar(
#             x=self.df.tid,
#             y=repeat_devices,
#             name='repeat',
#             # marker=dict(
#             #     color='rgb(49,130,189)'
#             # )
#         )
#
#         trace_newbird = go.Bar(
#             x=self.df.tid,
#             y=newbird_devices,
#             name='newbird',
#             # marker=dict(
#             #     color='rgb(49,130,189)'
#             # )
#         )
#
#         data = [trace_unstable, trace_repeat, trace_newbird]
#         layout = go.Layout(
#             xaxis=dict(
#                 # set x-axis' labels direction at 45 degree angle
#                 # tickangle=-45,
#                 # axis is not auto range
#                 autorange=False,
#                 title='Task Id',
#             ),
#             yaxis=dict(
#                 title='Devices Nums',
#             ),
#             barmode='stack',
#             title='SU_TIMED_OUT_SUMMARY'
#         )
#         fig = go.Figure(data=data, layout=layout)
#         py.plot(fig, filename='SU_TIMED_OUT_SUMMARY')


# class SuTimedOutProportionPercentage(object): # 所有执行完的任务中，su连接超时次数占所有任务数百分比列出设备名
#     def __init__(self):
#         self.db_path = os.path.join(os.path.dirname(PROJECT_ROOT),'db.sqlite3')
#         self.conn = sqlite3.connect(self.db_path)
#         self.df = pd.read_sql_query("SELECT * from lab_analysis_tools_taskdevice", self.conn)
#         self.conn.close()
#
#     def run(self):
#         is_failed = self.df['result'] == 'fail'
#         is_su_out = self.df['fail_detail'].str.contains('SU_CONNECTION_TIMEOUT')
#         target = self.df[is_failed & is_su_out]
#         su_out_devices_count = target['name'].value_counts()
#         number_task = len(self.df['task_id'].value_counts())
#         su_out_devices_count_float = su_out_devices_count.astype(float)
#         su_out_devices_percentage = su_out_devices_count_float / number_task
#         target = go.Bar(
#             x=list(su_out_devices_percentage.index),
#             y=list(su_out_devices_percentage.values),
#             name='target',
#         )
#         data = [target]
#         layout = go.Layout(
#             xaxis=dict(
#                 # set x-axis' labels direction at 45 degree angle
#                 tickangle=-25,
#                 # axis is not auto range
#                 autorange=False,
#                 title='Device Name',
#             ),
#             yaxis=dict(
#                 title='Percentage',
#             ),
#             barmode='stack',
#             title='SU_TIMED_OUT_PROPORTION_PERCENTAGE'
#         )
#         fig = go.Figure(data=data, layout=layout)
#         py.plot(fig, filename='SU_TIMED_OUT_PROPORTION_PERCENTAGE')

# class SuTimedOutSearchByDevice(object): # 通过设备名称查找su连接超时问题的任务详情
#     def __init__(self):
#         self.db_path = os.path.join(os.path.dirname(PROJECT_ROOT),'db.sqlite3')
#         self.conn = sqlite3.connect(self.db_path)
#         self.df = pd.read_sql_query("SELECT * from lab_analysis_tools_taskdevice", self.conn)
#         self.conn.close()
#
#     def run(self, device_name):
#         if device_name in self.df['name'].values:
#             device_dataframe = self.df[self.df['name'] == device_name]
#             device_dataframe_sorted = device_dataframe.sort_values(by='task_id')
#             device_dataframe_sorted_boolean = device_dataframe_sorted['fail_detail'].str.contains('SU_CONNECTION_TIMEOUT').astype(float)
#
#             target = go.Bar(
#                 x=list(device_dataframe_sorted.task_id),
#                 y=list(device_dataframe_sorted_boolean),
#                 name='target',
#             )
#             data = [target]
#             layout = go.Layout(
#                 xaxis=dict(
#                     # set x-axis' labels direction at 45 degree angle
#                     # tickangle=-45,
#                     # axis is not auto range
#                     autorange=False,
#                     title='Task Id',
#                 ),
#                 yaxis=dict(
#                     title='',
#                 ),
#                 barmode='stack',
#                 title='SU_TIMED_OUT_' + device_name
#             )
#             fig = go.Figure(data=data, layout=layout)
#             py.plot(fig, filename='SU_TIMED_OUT_' + device_name)
#         else:
#             #没有找到对应的设备，暂不做处理
#             pass

# class SuTimedOutStability(object): #su连接超时不稳定设备表格
#     def __init__(self):
#         self.db_path = os.path.join(os.path.dirname(PROJECT_ROOT),'db.sqlite3')
#         self.conn = sqlite3.connect(self.db_path)
#         self.df = pd.read_sql_query("SELECT * from lab_analysis_tools_suconnectedtimedout", self.conn)
#         self.conn.close()
#
#     def _generate(self,original_series):
#         for item in original_series:
#             mylist = item.split("|")
#             for inline_item in mylist:
#                 if inline_item != '':
#                     yield inline_item
#
#     def run(self):
#         unstable_devices_generator = self._generate(self.df.unstable_devices)
#         unstable_devices_series = pd.Series(unstable_devices_generator)
#         unstable_devices_series_count = unstable_devices_series.value_counts()
#
#         target = go.Bar(
#             x=list(unstable_devices_series_count.index),
#             y=list(unstable_devices_series_count.values),
#             name='target',
#         )
#         data = [target]
#         layout = go.Layout(
#             xaxis=dict(
#                 # set x-axis' labels direction at 45 degree angle
#                 tickangle=-25,
#                 # axis is not auto range
#                 autorange=False,
#                 title='Device Name',
#             ),
#             yaxis=dict(
#                 title='Proportion Times',
#             ),
#             barmode='stack',
#             title='SU_TIMED_OUT_UNSTABILITY_PROPORTION_TIMES'
#         )
#         fig = go.Figure(data=data, layout=layout)
#         py.plot(fig, filename='SU_TIMED_OUT_UNSTABILITY_PROPORTION_TIMES')

# class NotFoundResultZipV(object):
#     def __init__(self):
#         self.db_path = os.path.join(os.path.dirname(PROJECT_ROOT),'db.sqlite3')
#         self.conn = sqlite3.connect(self.db_path)
#         self.df = pd.read_sql_query("SELECT * from lab_analysis_tools_notfoundresultzip", self.conn)
#         self.conn.close()
#
#     def _getLen(self, x):
#         if len(x) == 0:
#             return 0
#         else:
#             return len(x.split("|"))
#
#     def run(self):
#         unstable_devices = map(self._getLen, self.df.unstable_devices)
#         repeat_devices = map(self._getLen, self.df.repeat_devices)
#         newbird_devices = map(self._getLen, self.df.newbird_devices)
#         trace_unstable = go.Bar(
#             x=self.df.tid,
#             y=unstable_devices,
#             name='unstable',
#             # marker=dict(
#             #     color='rgb(49,130,189)'
#             # )
#         )
#
#         trace_repeat = go.Bar(
#             x=self.df.tid,
#             y=repeat_devices,
#             name='repeat',
#             # marker=dict(
#             #     color='rgb(49,130,189)'
#             # )
#         )
#
#         trace_newbird = go.Bar(
#             x=self.df.tid,
#             y=newbird_devices,
#             name='newbird',
#             # marker=dict(
#             #     color='rgb(49,130,189)'
#             # )
#         )
#
#         data = [trace_unstable, trace_repeat, trace_newbird]
#         layout = go.Layout(
#             xaxis=dict(
#                 # set x-axis' labels direction at 45 degree angle
#                 # tickangle=-45,
#                 # axis is not auto range
#                 autorange=False,
#                 title='Task Id',
#             ),
#             yaxis=dict(
#                 title='Devices Nums',
#             ),
#             barmode='stack',
#             title='NOT_FOUND_RESULT_ZIP'
#         )
#         fig = go.Figure(data=data, layout=layout)
#         py.plot(fig, filename='NOT_FOUND_RESULT_ZIP')


if __name__ == "__main__":
    # su_timed_out = SuTimedOut()
    # su_timed_out.run()
    pass

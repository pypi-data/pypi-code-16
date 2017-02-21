# coding=utf-8

import functools

__author__ = 'Maple.Liu'


class BaseDecorator(object):
    """
    View装饰器，调用之前需要重写以下函数：
    - request_pre_process
    - request_exception_process

    from base_bridge.views.decorators import BaseDecorator
    class BeforeView(BaseDecorator):
        @classmethod
        def request_pre_process(cls, request):
            '''
            Do something
            '''
            pass

        @classmethod
        def request_exception_process(cls, request, e):
            '''
            Do something
            '''
            pass

    @BeforeView.catch_exception_without_parameters
    def some_view(request):
        pass
    """

    @classmethod
    def request_pre_process(cls, request):
        """
        对请求预处理（如日志）
        :param request:
        :return:
        """
        pass

    @classmethod
    def request_exception_process(cls, request, e):
        """
        对请求进行异常处理（如发邮件）
        :param request:
        :return:
        """
        pass

    @classmethod
    def catch_exception_without_parameters(cls, func):
        """
        - 视图函数异常错误处理装饰器
        - 调用该装饰器的时候可以对request_preprocess函数进行定制定义
        """

        @functools.wraps(func)
        def new_func(request):
            cls.request_pre_process(request)
            try:
                back = func(request)
                return back
            except Exception as e:
                cls.request_exception_process(request, e)
        return new_func


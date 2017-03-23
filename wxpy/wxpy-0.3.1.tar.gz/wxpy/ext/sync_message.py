from threading import Thread
from wxpy.utils import ensure_list


def sync_message(msg, chats, template=None, run_async=True):
    """
    将消息同步到多个微信群中

    * 支持消息类型: 文本、图片、名片
    * 必要时自动拆为多条消息发送 (例如发送图片时)
    * 机器人发送的消息会被忽略

    :param msg: 需同步的消息对象
    :param chats: 需同步的聊天对象列表
    :param template: 消息显示模板，默认为::

        '{sender}:\\n{content}'

            * sender: 消息的发送者名称
            * content: 消息的内容
    :param run_async: 是否异步执行，为 True 时不堵塞线程
    """

    def process():
        pass

    if run_async:
        Thread(target=process, daemon=True).start()
    else:
        process()

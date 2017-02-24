# coding: utf-8

import multiprocessing
import ConfigParser
import time
from os import path
import click
import simplejson as json
from simplejson import JSONDecodeError
from deployv.messaging.messagev import BasicMessage
from deployv.messaging import rabbitv
from deployv.messaging import receiverv, senderv
from deployv.helpers import utils
from deployv.base import commandv


logger = utils.setup_deployv_logger('deployv')  # pylint: disable=C0103


class WorkerProcess(multiprocessing.Process):
    """ Worker process that waits infinitly for task msgs and calls
        the :meth:`~deployv.commands.workerv.WorkerProcess.callback` whenever it gets a msg
    """
    def __init__(self, configuration_class, sender_class, receiver_class,
                 worker_id, node_id, config_file):
        assert issubclass(configuration_class, rabbitv.BaseRabbitConfiguration)
        assert issubclass(sender_class, senderv.RabbitSenderV)
        assert issubclass(receiver_class, receiverv.RabbitReceiverV)
        multiprocessing.Process.__init__(self)
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self._use_template = config.getboolean('deployer', 'use_template')
        self._db_owner = config.get('postgres', 'db_user')
        self._db_owner_passwd = config.get('postgres', 'db_password')
        self._database_folder = config.get('deployer', 'database_folder')
        self._working_folder = config.get('deployer', 'working_folder')
        self._nginx_folder = config.get('deployer', 'nginx_folder')
        self._domain = config.get('deployer', 'domain')
        self._max_instances = int(config.get('deployer', 'max_instances'))
        self._docker_url = config.get('deployer', 'docker_url')
        self._use_nginx = config.get('deployer', 'use_nginx').upper() == 'TRUE'
        self.__wid = worker_id
        self.__node_id = node_id
        self.stop_working = multiprocessing.Event()
        self.count = 0
        self._config_class = configuration_class
        self._config_file = config_file
        self._receiver = receiver_class(configuration_class(config_file),
                                        self.callback,
                                        self.__node_id)
        self._sender = sender_class(configuration_class(config_file, result=True), self.__node_id)

    def run(self):
        """ Worker method, open a channel through a pika connection and
            start consuming
        """
        logger.info("W%s - waiting for something to do", self.__wid)
        self._receiver.run()

    def signal_exit(self):
        """ Exit when finished with current loop """
        self._receiver.stop()
        self.stop_working.set()

    def exit(self):
        """ Exit worker, blocks until worker is finished and dead """
        self.signal_exit()
        while self.is_alive():  # checking `is_alive()` on zombies kills them
            time.sleep(1)

    def kill(self):
        """ This kill immediately the process, should not be used """
        self._receiver.stop()
        self.terminate()
        self.join()

    def callback(self, channel, method, properties, body):
        """ This method is executed as soon as a message arrives, according to the
            `pika documentation
            <http://pika.readthedocs.org/en/latest/examples/blocking_consume.html>`_. The
            parameters are fixed according to it, even if the are unused
        """
        logger.info('Received a message worker %s', self.__wid)
        logger.debug('%s worker received "%s"',
                     self.__wid,
                     json.dumps(json.loads(body), sort_keys=True, indent=4))
        message = self.check_message(body, channel, method)
        if message.receiver_node_id != self.__node_id:
            logger.error('Message in the wrong queue, does not match my wid: %s', self.__node_id)
            return False
        if message is False:
            return False
        self._sender.send_message(message.get_ack_message())
        logger.debug('Ack sent')
        module = message.message_body.get('module')
        command_name = message.message_body.get('command')
        parameters = message.message_body.get('parameters')
        parameters.get('container_config').update({
            'database_folder': self._database_folder,
            'working_folder': self._working_folder,
            'domain': self._domain,
            'use_template': self._use_template,
            'db_owner': self._db_owner,
            'db_owner_passwd': self._db_owner_passwd
        })
        parameters.update({
            'node': {
                'max_instances': self._max_instances,
                'docker_url': self._docker_url,
                'use_nginx': self._use_nginx,
                'nginx_folder': self._nginx_folder
            }
        })
        channel.basic_ack(delivery_tag=method.delivery_tag)
        if module == 'commandv':
            command = commandv.CommandV(parameters)
            message_body = {
                'command': command_name,
                'module': module,
            }
            if hasattr(command, command_name):
                try:
                    function = getattr(command, command_name)
                    logger.debug('Parameters: %s',
                                 json.dumps(parameters, sort_keys=True, indent=4))
                    res = function()
                except Exception as error:  # pylint: disable=W0703
                    logger.exception('An uncaught exception raised during the execution')
                    message_body.update({'error': 'Uncaught exception: {error}'
                                        .format(error=utils.get_error_message(error))})
                    message.set_message_body(message_body,
                                             message_type='error')

                else:
                    logger.debug('Function result :%s',
                                 json.dumps(res, sort_keys=True, indent=4))
                    time.sleep(10)
                    message_body.update(res)
                    message.set_message_body(message_body,
                                             message_type='result')
            else:
                message_body.update({'error': 'Command {cmd} does dot exits in module {module}'
                                    .format(cmd=command, module=module)})
                message.set_message_body(message_body,
                                         message_type='error')
            response = message.build_message()
            logger.debug('Message to send %s',
                         json.dumps(response, sort_keys=True, indent=4))
            self._sender.send_message(response)
        logger.info('%s worker done', self.__wid)

    def check_message(self, message, channel, method):
        """ Check if the message is properly formed and can be parsed, if nt a message with the
            error will be generated

        :param message: The message to be checked
        :param channel: The channel used for communication so the method can ack and drop it
            from the queue
        :param method: Delivery method used, is needed to get the message tag in order to
            know the message tag used in the queue
        :return: The message object (:class:`~deployv.messaging.messagev.BasicMessage`)
            if no error, else False
        """
        try:
            res_msg = BasicMessage(message)
            res_check = utils.check_message(res_msg.original_message)
            if res_check is not None:
                raise JSONDecodeError(res_check, message, 0)
        except JSONDecodeError as error:
            logger.error('The message is malformed: %s', error.message)
            response = {
                'error':
                {
                    'message': error.message,
                    'code': -32700,
                }
            }
            res = BasicMessage()
            res.sender_node_id = self.__wid
            res.receiver_node_id = res_msg.original_message.get('sender_node_id')
            res.set_message_body(response, message_type='error')
            channel.basic_ack(delivery_tag=method.delivery_tag)
            self._sender.send_message(res.build_message())
            return False
        return res_msg


@click.command()
@click.option("-f", "--config_file", help="Json file with the configuration",
              default=False, required=True)
@click.option("-l", "--log_level", help="Log level to show",
              default='INFO')
def run(config_file, log_level):
    assert path.isfile(config_file)
    logger.setLevel(log_level)
    reader_p = []
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    n_workers = int(config.get('deployer', 'workers'))
    node_id = config.get('deployer', 'node_id')
    for worker in range(n_workers):
        work = WorkerProcess(rabbitv.FileRabbitConfiguration,
                             senderv.RabbitSenderV,
                             receiverv.RabbitReceiverV,
                             worker,
                             node_id,
                             config_file)
        work.daemon = True
        work.start()
        reader_p.append(work)

    try:
        for worker in reader_p:
            worker.join()
    except KeyboardInterrupt:
        pass


# The main method is only for tests purspuses, this will be deleted in the stable version
# TODO: Drop this before stable relese
if __name__ == '__main__':
    run()

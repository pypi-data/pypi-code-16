import traceback
import os
import sys
import shaman

from logging import getLogger, handlers, INFO, Formatter

from shaman.src.abstract_message import Message, control_messages, MessageFormat


class Consumer(object):
    def __init__(self, basepath, config, worker_num, in_queue):
        """
        AbstractConsumer constructor, don't modify this method, use init_consumer.
        """
        self.worker_num = worker_num
        self._consumer_config = config
        self.in_queue = in_queue

        self.name = self._consumer_config['GENERAL']['worker_prefix'] + str(self.worker_num)
        for dir in self._consumer_config['GENERAL']['stages_dir'].split(';'):
            sys.path.append(shaman.__path__[0] + "/" + dir)
        sys.path.append(self._consumer_config['GENERAL']['custom_stage_dir'])


        self.imported_classes = {}

        self.workers_logging_dir = self._consumer_config['GENERAL']['workers_logging_dir']

        self.setup_logging()

        for stage_name in self._consumer_config['STAGES']:
            stage = eval('{'+str(self._consumer_config['STAGES'][stage_name])+'}')
            if 'python_class_filename' in stage:
                stage_class = getattr(__import__(stage['python_class_filename']), stage['classname'])
            else:
                stage_class = getattr(__import__(stage_name), stage['classname'])

            stage_conf = self._consumer_config[stage_name]
            new_stage = stage_class(stage_conf)

            self.imported_classes[stage_name] = {'class_obj': new_stage,
                                                 'order': int(stage_conf['order'])}
            new_stage.set_logger(self.my_logger)
            new_stage.set_consumer_name(self.name)

        self.init_consumer(basepath, config)
        self._is_in_shutdown_state = False

    #def _read_graphite_config(self):
    #    self.graphite_enabled = False
    #    if 'GRAPHITE' in self._consumer_config:
    #        self.graphite_enabled = self._consumer_config['GRAPHITE']['enabled'].lower() == 'true'

    #   if self.graphite_enabled:
    #        self.graphite_host = self._consumer_config['GRAPHITE']['host']
    #        self.graphite_port = int(self._consumer_config['GRAPHITE']['port'])
    #        self.graphite_global_key = self._consumer_config['GRAPHITE']['global_key']

    #def init_graphite(self):
    #    if self.graphite_enabled:
    #        self.on_message_graphite = GraphiteSenderTimer(self.graphite_host,
    #                                                  self.graphite_port,
    #                                                  self.graphite_global_key,
    #                                                  self.name,
    #                                                  metrics_name='message_process_time',
    #                                                  logger=self.my_logger,
    #                                                  enabled=True)

    #        self.on_message = self.on_message_graphite.timeit_graphite(self.on_message)

    def setup_logging(self):
        self.my_logger = getLogger(self.name)
        self.my_logger.setLevel(INFO)

        self.logfile = self.workers_logging_dir+os.sep+'worker_'+str(self.worker_num) + '.log'
        handler = handlers.RotatingFileHandler(
            self.logfile,
            mode='a+',
            maxBytes=20480000, backupCount=5)

        log_formatter = Formatter(
            fmt='%(asctime)s:%(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(log_formatter)

        self.my_logger.addHandler(handler)

    def init_consumer(self, basepath, config):
        """
        :param basepath: path to a project. Could be /opt/shaman (default) or
        custom (if you cloned a project from github).
        :param config: parsed configuration (dictionary) of a worker.
        Contains configuration parameters of a worker: worker_number, logdir, prefix_name, etc.
        Also contain the configuration parameters for stages.
        """
        self.name = 'worker'
        self.workers_logging_dir = '/'
        self.config = config

    def init_after_process_start(self):
        #if self._consumer_config['GRAPHITE']['enabled'].lower() == 'true':
        #    self.init_graphite()
        self._sort_stages()

    def consume(self):
        """
        Creates a Message object (container).
        Runs all stages in a cycle.
        Logges the results.
        Cleans the fields of a Message.
        Repeates until shutdown signal is not catched.
        :return:
        """
        self.init_after_process_start()
        self.py_version = int(sys.version[0])

        new_message_object = Message()

        while not self._is_in_shutdown_state:
            self.on_message(new_message_object)

            if new_message_object.format == MessageFormat.CONTROL:
                if new_message_object.control_message == 'shutdown':
                    self._is_in_shutdown_state = True

            #self.commit_queue.put(new_message_object.stdin_line)
            #print(dir(new_message_object))
            new_message_object.clean_fields()

        self.my_logger.info('Exiting...')
        self.shutdown_all_stages()
        sys.exit(0)


    def _sort_stages(self):
        self.stage_ordered_list = []
        for name in self.imported_classes.keys():
            analyzer_obj = self.imported_classes[name]['class_obj']
            analyzer_order = self.imported_classes[name]['order']
            self.stage_ordered_list.append((analyzer_order, analyzer_obj))

        self.stage_ordered_list.sort(key=lambda x: x[0])

        # Passing in_queue to first stage only if reading from stdin. First stage should be queue reader/parser
        if self.in_queue:
            self.stage_ordered_list[0][1].__dict__['in_queue'] = self.in_queue

    def clear_message_from_memory(self, msg):
        del msg

    def shutdown_all_stages(self):
        for stage in self.stage_ordered_list:
            # calling shutdown for all stages
            stage[1].shutdown()
        self.my_logger.info("Shutdown all stages done")

    def on_message(self, msg):
        try:
            for stage_index, stage in enumerate(self.stage_ordered_list):
                analyzer_obj = stage[1]
                re_mess = analyzer_obj._do_stage(msg)

        except Exception as e:
            ## finalize stages before going down
            for st_index, stage in enumerate(self.stage_ordered_list):
                if st_index != stage_index:
                    analyzer_obj = stage[1]
                    analyzer_obj.finish_batch()
                    analyzer_obj.shutdown()

            self.my_logger.error('Traceback: {}'.format(traceback.format_exc()))
            raise e

    def run(self):
        self.consume()

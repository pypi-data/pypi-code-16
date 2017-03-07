#!python

"""Main script for trollflow based processors."""

import logging
import logging.config
import sys
import time
from threading import Lock
import os

from trollflow.workflow_streamer import WorkflowStreamer
from trollflow.utils import ordered_load, stop_worker


def generate_daemon(config_item):
    """Return a daemon based on the YAML configuration"""
    return config_item['components'][-1]['class']


def generate_thread_workflow(config_item):
    wfs = WorkflowStreamer(config=config_item)
    wfs.setDaemon(True)
    wfs.start()
    return wfs


TYPES = {'daemon': generate_daemon,
         'workflow': generate_thread_workflow,
         }


def read_yaml_config(fname):
    """Read YAML config file"""
    # Read config
    with open(fname, "r") as fid:
        config = ordered_load(fid)

    return config


def setup_logging(config):
    """Setup logging"""

    # Check if log config is available, use it if it is
    if "log_config" in config["config"]:
        logging.config.fileConfig(config["config"]["log_config"],
                                  disable_existing_loggers=False)


def create_threaded_workers(config):
    """Create workers"""

    workers = []
    for item in config['work']:
        workers.append(TYPES[item['type']](item))

    queue = None
    prev_lock = None
    for worker in workers:
        if queue is not None:
            worker.input_queue = queue
        try:
            queue = worker.output_queue
        except AttributeError:
            queue = worker.queue

        try:
            worker.prev_lock = prev_lock
        except AttributeError:
            pass
        lock = Lock()
        try:
            worker.lock = lock
        except AttributeError:
            pass
        prev_lock = lock

    return workers


def wait_threads(workers, logger):
    """Loop workers until keyboard interrupt is detected, after which join
    the queues and stop the worker instances."""
    loop = True
    while loop:
        try:
            time.sleep(5)
        except (KeyboardInterrupt, MemoryError):
            logger.info("Closing flow processing items")
            for worker in workers:
                stop_worker(worker)
            loop = False


def main():
    """Main()"""

    config = read_yaml_config(sys.argv[1])

    try:
        if config["config"]["use_utc"]:
            os.environ["TZ"] = "UTC"
            time.tzset()
    except KeyError:
        pass

    setup_logging(config)
    logger = logging.getLogger("flow_processor")
    logger.info("Initializing flow processor")

    workers = create_threaded_workers(config)
    logger.info("Ready to process new data")
    wait_threads(workers, logger)

    logger.info("Flow processor has been shutdown.")

if __name__ == "__main__":
    main()

"""The business logic"""
import json
import logging
import os
import signal
import time
from RPi import GPIO

from sersir.utils import ping, AuditLog
from sersir.jenkins.requests import jobs_status

logger = logging.getLogger(__name__)


def detect_failed_jobs_changes(state_old, job_failed_names):
    """Calculate the diff of the old state and currently failed job names"""
    state = state_old.copy()

    new_failed = []
    good_again = []
    # Find new failed builds and insert them into our state object
    for job_name in job_failed_names:
        if job_name not in state.keys():
            state[job_name] = time.time()
            new_failed.append(job_name)

    # Check for removed (good again) jobs and delete them from our state object
    for job_name, _ in state_old.items():
        if job_name not in job_failed_names:
            del state[job_name]
            good_again.append(job_name)

    return state, new_failed, good_again


def filter_ignored_jobs(jobs, ignored_projects):
    return (job for job in jobs if job['name'] not in ignored_projects)


def filter_failed_jobs(jobs):
    # The jobs have no direct attribute, which marks them as failed
    return (job for job in jobs if job['color'] == "yellow" or job['color'] == "red")


class Runner:
    """Wrap the setup and long running code"""

    def __init__(self, config):
        self.config = config

        self.state = {}
        self.systemd_available = False
        self.systemd_module = None

        self.audit_log = None

    def setup(self):
        format_string = '%(asctime)s %(levelname)s %(name)s: %(message)s'

        # Check if we are running within systemd
        if "NOTIFY_SOCKET" in os.environ:
            try:
                format_string = '%(levelname)s %(name)s: %(message)s'
                import systemd.daemon as sd_d

                self.systemd_available = True
                self.systemd_module = sd_d
            except ImportError:
                raise RuntimeError("Probably started with systemd type notify, but can't load required module. Aborting execution")

        logging.basicConfig(level=self.config.debug_level, format=format_string)

        logger.info('Logging configured')

        self.audit_log = AuditLog(self.config.audit_log_file)
        self.audit_log.write(event_type='STARTED', name=os.getpid())

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.config.lamp_gpio_board_pin, GPIO.OUT, initial=GPIO.LOW)
        logger.info('Setup successful of the gpio pin %s', self.config.lamp_gpio_board_pin)

        self.load_state_file()

        if len(self.state) > 0:
            GPIO.output(self.config.lamp_gpio_board_pin, GPIO.HIGH)

        if self.systemd_available:
            self.systemd_module.notify(self.systemd_module.Notification.READY)

    def run(self):
        while True:
            # Check if host is alive
            ping(self.config.host)

            # Request jobs from jenkins host
            jobs = jobs_status(host=self.config.host, user=self.config.user, token=self.config.token, scheme=self.config.scheme, path=self.config.path)
            logger.info('Loaded data')

            job_failed_names = [job['name'] for job in filter_failed_jobs(
                filter_ignored_jobs(jobs, self.config.ignored_projects)
            )]

            # Log failed jobs
            logger.debug('Following jobs have a failed status: %s', ', '.join([job_name for job_name in job_failed_names]))

            state_old = self.state.copy()

            self.state, new_failed, good_again = detect_failed_jobs_changes(self.state, job_failed_names)

            logger.info('Old failed job count %s, new failed job count %s, good again job count %s',
                        len(state_old), len(new_failed), len(good_again))

            logger.debug('New failed jobs: %s', ', '.join(new_failed))
            logger.debug('Good again jobs: %s', ', '.join(good_again))

            for job_name in new_failed:
                self.audit_log.write(event_type='NEW_FAILED', name=job_name)
            for job_name in good_again:
                self.audit_log.write(event_type='GOOD_AGAIN', name=job_name)

            # GPIO pin conditions
            if len(self.state) > 0:
                GPIO.output(self.config.lamp_gpio_board_pin, GPIO.HIGH)
                logger.info('Turned on the lamp')
            else:
                GPIO.output(self.config.lamp_gpio_board_pin, GPIO.LOW)
                logger.info('Turned off the lamp')

            # State serialization and shifting to state file
            if len(new_failed) > 0 or len(good_again) > 0:
                self.save_state_file()

            logger.debug('Sleeping for %s', self.config.sleep_time)
            time.sleep(self.config.sleep_time.total_seconds())

    def shutdown(self, signum, _):
        if self.systemd_available:
            self.systemd_module.notify(self.systemd_module.Notification.STOPPING)
        self.audit_log.write(event_type='STOPPED', name='Signal caught ' + str(signum))
        GPIO.cleanup()
        logger.warning('Stopped')
        import sys
        sys.exit(0)

    def load_state_file(self):
        try:
            logger.debug('Try to load state from state file')
            with open(self.config.state_file, 'r') as file:
                self.state = json.load(file)['state']
            logger.debug('Successfully loaded state from state file')
        except:
            logger.warning('Could not load state from state file')
            self.state = {}

    def save_state_file(self):
        with open(self.config.state_file, 'w') as file:
            json.dump({'written': time.time(), 'state': self.state}, file)
            logger.debug('Shifted state to state file')

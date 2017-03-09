# -*- coding: utf-8 -*-
import datetime
import time

import signal
from pytz import timezone

tz_brussel = timezone('Europe/Brussels')


class CircuitState():
    CLOSED = 1
    OPEN = 2
    HALF_OPEN = 3


class CircuitException(Exception):
    pass


class CircuitTimeoutException(Exception):
    pass


class DaemonCircuitBreaker(object):
    def __init__(self, circuit, logger, expected_exceptions, failure_threshold=5, timeout_default=60, max_timeout=300,
                 invocation_timeout=60):
        self.circuit = circuit
        self.invocation_timeout = invocation_timeout
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.logger = logger
        self.expected_exceptions = expected_exceptions
        self.last_failure_time = None
        self.first_failure_time = None
        self.timeout_default = timeout_default
        self.timeout = self.timeout_default
        self.max_timeout = max_timeout
        self.half_open_count = 0
        self.state = CircuitState.CLOSED

    def call(self, *args, **kwargs):
        while True:
            if self.state == CircuitState.CLOSED or self.state == CircuitState.HALF_OPEN:
                result = self._do_call(*args, **kwargs)
                if self.failure_count == 0:
                    return result
            elif self.state == CircuitState.OPEN:
                self.logger.warn('circuit open => {0} '.format(self.circuit))
                self.logger.warn('failed {0} time(s)'.format(self.failure_count))
                self.logger.warn('first failure {0}'.format(self.first_failure_time.isoformat()))
                self.logger.warn('last failure {0}'.format(self.last_failure_time.isoformat()))
                self.logger.warn('going to sleep')
                time.sleep(self.timeout_default)
            else:  # pragma: no cover
                raise CircuitException('incorrect circuit state')
            self.state = self._calculate_state()

    def _handle_timeout(self, signum, frame):
        raise CircuitTimeoutException(
            "{0} timed out after {1} seconds".format(frame.f_code.co_name, self.invocation_timeout))

    def _do_call(self, *args, **kwargs):
        signal.signal(signal.SIGALRM, self._handle_timeout)
        signal.alarm(self.invocation_timeout)
        try:
            result = self.circuit(*args, **kwargs)
            self.reset()
            return result
        except Exception as ex:
            if ex.__class__ in self.expected_exceptions or ex.__class__ is CircuitTimeoutException:
                self.logger.error(ex)
                self._record_failure()
            else:
                raise ex
        finally:
            signal.alarm(0)

    def _reset_timeout(self):
        self.half_open_count += 1
        self.timeout += self.half_open_count * self.half_open_count
        if self.timeout > self.max_timeout:
            self.timeout = self.max_timeout

    def _record_failure(self):
        self.failure_count += 1
        if self.state == CircuitState.HALF_OPEN:
            self._reset_timeout()
        self.last_failure_time = datetime.datetime.now(tz_brussel)
        if not self.first_failure_time:
            self.first_failure_time = datetime.datetime.now(tz_brussel)

    def _calculate_state(self):
        if self.failure_count >= self.failure_threshold and (datetime.datetime.now(
                tz_brussel) - self.last_failure_time).seconds >= self.timeout:
            return CircuitState.HALF_OPEN
        elif self.failure_count >= self.failure_threshold:
            return CircuitState.OPEN
        else:
            return CircuitState.CLOSED

    def reset(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.first_failure_time = None
        self.timeout = self.timeout_default
        self.half_open_count = 0

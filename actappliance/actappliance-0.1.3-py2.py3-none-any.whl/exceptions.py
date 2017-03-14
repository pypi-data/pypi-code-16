import logging
from actappliance.act_errors import act_errors, ACTError


class CLIError(ACTError):
    """A CLI error occurred."""


class RESTError(ACTError):
    """A REST error occurred"""


class ApplianceError(Exception):
    """
    Generic Appliance exception to raise and log different fatal errors.
    """

    def __init__(self, msg):
        super(ApplianceError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class ActHostError(Exception):

    def __init__(self, msg):
        super(ApplianceError).__init__(type(self))
        self.msg = "E: %s" % msg


class KeywordError(Exception):
    pass


def retry_if_result_none(result):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return result is None


def retry_if_result_not_none(result):
    """Return False if we should retry (in this case when result isn't None), False otherwise"""
    return result is not None


def retry_if_act_result_empty(act_response_obj):
    """Return True if result is populated"""
    try:
        ok = act_response_obj['result'] == []
    except KeyError:
        # Retry if result doesn't exist. This allows the call to continue until it functions
        # Primary use is to search job history until the result is available
        logging.debug('No result found in ActResponse, flagging for retry.')
        ok = True
    except TypeError:
        logging.exception("It is very likely your function doesn't have a return where it should.")
        raise
    return ok


def retry_if_act_result_populated(act_response_obj):
    """
    Return True if result is empty/falsey.
    This will raise error if result doesn't exist
    """
    try:
        if act_response_obj['result']:
            ok = True
        else:
            ok = False
    except KeyError:
        logging.debug('No result found in ActResponse, reraising.')
        # If this is ever changed must return False as retries will happen if return is None
        raise
    except TypeError:
        logging.exception("It is very likely your function doesn't have a return where it should.")
    return ok


def retry_if_acterror(exception):
    """Return True if we should retry (in this case when it's an ACTError or subclass of ACTError), False otherwise"""
    logging.debug("Exception passed to retry_if_acterror is: {}".format(exception))
    # The exception is the instance
    return issubclass(exception.__class__, ACTError)


def retry_if_no_acterror(exception):
    """Opposite of retry_if_acterror"""
    return not issubclass(exception.__class__, ACTError)


def retry_if_applianceerror(exception):
    """Retry if ApplianceError occurs"""
    return isinstance(exception, ApplianceError)


def retry_if_unknownobject(exception):
    return isinstance(exception, act_errors[10016])


def retry_until_unknownobject(exception):
    return not isinstance(exception, act_errors[10016])


def retry_if_workflow_is_deleted(exception):
    """**Deprecated** please use retry_until_unknownobject"""
    return not isinstance(exception, act_errors[10016])


def retry_if_workflow_is_running(act_response_obj):
    """Retry unless ActResponse['result'] is populated and doesn't contain 'RUNNING'"""
    # retry if empty result
    ok = True
    if retry_if_act_result_populated(act_response_obj):
        if 'RUNNING' not in act_response_obj['result']:
            ok = False
    return ok


def retry_until_runtime(exception):
    return isinstance(exception, RuntimeError)

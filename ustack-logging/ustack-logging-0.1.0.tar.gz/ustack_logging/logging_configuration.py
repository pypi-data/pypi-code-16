import datadog
from datadog_logger import log_error_events
import kubernetes_downward_api
import logging


def configure_logging(environ):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(module)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z", level=logging.INFO)

    try:
        datadog.initialize(api_key=environ["DATADOG_API_KEY"], app_key=environ["DATADOG_APP_KEY"])

        podinfo = kubernetes_downward_api.parse(["/etc/podinfo"])

        log_error_events(tags=[
            "environment:{0}".format(podinfo["namespace"]),
            "service:{0}".format(podinfo["labels"]["app"]),
            "role:{0}".format(podinfo["labels"]["role"])
        ])
    except:
        logging.warning("Could not initialize DataDog error logging, with error:", exc_info=True)

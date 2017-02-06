import os
import json
import time
import boto3
from botocore.client import Config
import ecs_ondemand

def handler_sns(obj):
	for record in obj:
		if "Sns" in record:
			ecs = boto3.client("ecs")
			message = json.loads(record["Sns"]["Message"])
			ecs_ondemand.run(message)


event_handlers = {
	"Records": handler_sns,
}


def handler(event, context):
	for header, value in event.items():
		if header in event_handlers:
			event_handlers[header](value)
		else:
			raise Exception("No handler for event {}".format(header))


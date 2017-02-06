import os
import sys
import boto3
import botocore

desc = {

	"image": "",
	"data": "",
	"role": "",
	"cluster": ""
}

def _get_name_from_image(image):
	return image.replace("/", "_")

def run(event, debug=False):
	print(os.environ)
	event_name = _get_name_from_image(event["image"])

	region = os.environ.get("AWS_REGION")
	logs = boto3.client("logs", region_name=region)

	log_group_name = "/ecs-ondemand/{}".format(event_name)
	try:
		response = logs.create_log_group(
			logGroupName=log_group_name,
		)

	except botocore.exceptions.ClientError as exception:
		if exception.response["Error"]["Code"] != 'ResourceAlreadyExistsException':
			raise exception

	task_def = {
		"family": event_name,
		"containerDefinitions": [
			{
				"name": "runner",
				"image": event["image"],
				"memoryReservation": 512,
				"essential": True,
				# "privileged": true,
				"logConfiguration": {
					"logDriver": "awslogs",
					"options": {
						"awslogs-group": log_group_name,
						"awslogs-region": region,
						"awslogs-stream-prefix": "runner"
					}
				}
			}
		]
	}

	if debug:
		print(task_def)

	if event.get("task"):
		task_def["taskRoleArn"] = event["role"]

	ecs = boto3.client("ecs", region_name=region)
	ecs.register_task_definition(**task_def)

	task = {

		"cluster": event["cluster"],
		"taskDefinition": event_name,
		"overrides": {
			"containerOverrides": [
				{
					"name": "runner",
					"environment": [
						{
							"name": "DATA",
							"value": event.get("data", "")
						}
					]
				}
			]
		},
		"count": 1,
		"startedBy": "ecs on demand"
	}
	if event.get("environment"):
		for key, value in event.get("environment").values():
			task["overrides"]["containerOverrides"]["environment"][key] = value

	fire_task = ecs.run_task(**task)

	print(fire_task)

if __name__ == "__main__":

	event = {}
	try:
		event = {
				"image": sys.argv[1],
				"cluster": sys.argv[2],
				# "data": ,
				# "role": "",
		}
	except:
		print("Usage: python ecs_ondemand.py <image> <cluster> [data] [role]")
		sys.exit(1)

	run(event)

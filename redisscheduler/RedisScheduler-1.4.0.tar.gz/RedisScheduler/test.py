print(' -- Test Begin -- ')

from RedisScheduler import RedisScheduler
from time import sleep

# Start Email Subscriber
listener = RedisScheduler()

SQS_ACCESS_KEY = 'AKIAJXIJIR6244Q3F6UA'
SQS_SECRET_KEY = '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'
SQS_REGION = 'ap-south-1'

listener.set_sqs_keys(access_key=SQS_ACCESS_KEY, secret_key=SQS_SECRET_KEY, queue_name='emails', region=SQS_REGION)
listener_response = listener.start_listening(handler='sqs')

print(listener_response)

setter = RedisScheduler()
while 1:
    email_data = {"multiple":0,"emailTo":"anirudha@venturesity.com","emailSubject":"Test Subject","emailBodyText":"Test Body","emailCc":"","emailBcc":"","emailType":"general","attachments":[],"emailBody":{"body":"Testing Body on server"}}

    scheduled_time = "2017-02-27T14:40:00+05:30"

    setting_event = setter.register_event(email_data, scheduled_time)
    sleep(5)

print(' -- Test END -- ')

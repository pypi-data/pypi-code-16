import os
import sys
import urllib
from subprocess import call
import time
from hadmlservices import callbacks

AWS_REGION = "us-east-1"

def update(cb, key, message):
    print message
    cb.update_job(key, message)

def user_data(root_dir,
              input_s3,
              output_s3,
              model_params):
    
    cb = callbacks.CB();
    update(cb, "job_state", "creating input and output dirs")
    for x in [root_dir + "/input", root_dir + '/output']:
        if not os.path.exists(x):
            os.mkdir(x, 0777)
        os.chmod(x, 0777)    
    
    update(cb, "job_state", "downloading log agent")
    agent = root_dir + '/awslogs-agent-setup.py'
    url = ("https://s3.amazonaws.com/aws-cloudwatch/" +
           "downloads/latest/awslogs-agent-setup.py")
    f = urllib.URLopener()
    f.retrieve(url, agent)

    # work around for ubuntu 16.04
    update(cb, "job_state", "installing awslogs.service")
    path = os.path.dirname (os.path.abspath (__file__))
    call(["cp", path + "/awslogs.service", "/lib/systemd/system/awslogs.service"])
    os.chmod("/lib/systemd/system/awslogs.service", 0644)

    update(cb, "job_state", "launching log agent")
    os.chmod(agent, 0700)
    path = os.path.dirname (os.path.abspath (__file__))
    call([agent, "-n", "-r", AWS_REGION, "-c", path + "/awslogs.conf"])

    update(cb, "job_state", "copying input data")
    update(cb, "started", time.strftime('%Y-%m-%d %H:%M:%S'))
    call(["aws", "s3", "sync", input_s3, root_dir + "/input"])
    
    update(cb, "job_state", "executing run_script")
    if model_params:
        call([root_dir + "/run_script",
              root_dir + "/input",
              root_dir + "/output",
              model_params])
    else:
        call([root_dir + "/run_script",
              root_dir + "/input",
              root_dir + "/output"])

    update(cb, "job_state", "copying output data")
    call(["aws", "s3", "sync", "--acl", "bucket-owner-full-control",
           root_dir + "/output", output_s3])

    update(cb, "job_state", "finished")
    update(cb, "finished", time.strftime('%Y-%m-%d %H:%M:%S'))

    print("asynchronously terminating instance")
    cb.terminate_instance()
    return

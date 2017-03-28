#!/usr/bin/python

import sys
import os
import re
import jenkins
import subprocess
import argparse
from ConfigParser import SafeConfigParser
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jenkins-build')

# read the configure file to get jenkins settings
def read_jenkins_conf(cli):
    confs={}
    if cli.conf is not None and os.path.isfile(cli.conf):
        parser = SafeConfigParser(allow_no_value=True)
        parser.read(cli.conf)
        section_name = 'jenkins'
        if section_name in parser.sections():
            options = parser.options(section_name)
            if 'jenkins' in options:
                confs['jenkins'] = parser.get(section_name, 'jenkins')
            if 'user' in options:
                confs['user'] = parser.get(section_name, 'user')
            if 'password' in options:
                confs['password'] = parser.get(section_name, 'password')
    return confs

# merge the jenkins settings with command line options
def merge_jenkins_conf(cli):
    jcs = {}
    confs = read_jenkins_conf(cli)
    logger.debug("conf from file {} ".format(confs))
    if cli.jenkins is not None :
       jcs['jenkins'] = cli.jenkins
    elif 'jenkins' in confs:
       jcs['jenkins'] = confs['jenkins']
    else:
       logger.error("'--jenkins' setting is missing from cmd line or conf file")
       sys.exit(1)

    if cli.user is not None :
       jcs['user'] = cli.user
    elif 'user' in confs:
       jcs['user'] = confs['user']
    else:
       logger.error( "'--user' setting is missing from cmd line or conf file")
       sys.exit(1)

    if cli.password is not None :
       jcs['password'] = cli.password
    elif 'password' in confs:
       jcs['password'] = confs['password']
    else:
       logger.error("'--password' setting is missing from cmd line or conf file")
       sys.exit(1)

    return jcs

# read the configure file to get the build settings
def read_build_conf(cli):
    jobname=None
    parameters={}
    if cli.conf is not None and os.path.isfile(cli.conf):
        parser = SafeConfigParser(allow_no_value=True)
        parser.read(cli.conf)
        sections = parser.sections()
        if 'job' in sections:
            options = parser.options('job')
            if 'name' in options:
                jobname = parser.get('job', 'name')
                if len(jobname) == 0:
                    jobname = None
        if 'parameters' in sections:
            for name, value in parser.items('parameters'):
                parameters[name] = value
    return (jobname, parameters)

# merge the build settings with command line options
def merge_build_conf(cli):
    jobname = None
    parameters = {}
    (jobname, parameters) = read_build_conf(cli)
    logger.debug("job name from conf file: {} ".format(jobname))
    logger.debug("parameters from conf file: {} ".format(parameters))
    if cli.job is not None :
       logger.debug("job name from cmd line: {} ".format(cli.job))
       jobname = cli.job
    if jobname is None:   
       logger.error("'--job' setting is missing from cmd line or buildconf file")
       sys.exit(1)

    if cli.parameters is not None:
       logger.debug("parameters from cmd line: {} ".format(cli.parameters))
       for parameter in cli.parameters:
           pv = parameter.split('=')
           parameters[pv[0]] = pv[1]

    return (jobname, parameters)

# get the query settings from command line
def get_query_conf(cli):
    jobname = None
    buildnum=None
    queueid=None
    if cli.job is not None :
       logger.debug("job name from cmd line: {} ".format(cli.job))
       jobname = cli.job
    if jobname is None:
       logger.error("'--job' setting is missing")
       sys.exit(1)

    if cli.buildnum is not None:
       logger.debug("buildnum from cmd line: {} ".format(cli.buildnum))
       buildnum = cli.buildnum

    if cli.queueid is not None:
       logger.debug("queueid from cmd line: {} ".format(cli.queueid))
       queueid = cli.queueid

    if buildnum is None and queueid is None:
       logger.error("'--buildnum' or '--queueid' setting is missing")
       sys.exit(1)

    return (jobname, buildnum, queueid)


# get the cancel settings from command line
def get_cancel_conf(cli):
    jobname = None
    buildnum=None
    queueid=None
    if cli.job is not None :
       logger.debug("job name from cmd line: {} ".format(cli.job))
       jobname = cli.job
    if jobname is None:
       logger.error("'--job' setting is missing from cmd line or buildconf file")
       sys.exit(1)

    if cli.buildnum is not None:
       logger.debug("buildnum from cmd line: {} ".format(cli.buildnum))
       buildnum = cli.buildnum

    if cli.queueid is not None:
       logger.debug("queueid from cmd line: {} ".format(cli.queueid))
       queueid = cli.queueid

    if buildnum is None and queueid is None:
       logger.error("'--buildnum' or '--queueid' setting is missing")
       sys.exit(1)

    return (jobname, buildnum, queueid)

# get the log settings from command line
def get_buildlog_conf(cli):
    jobname = None
    buildnum = None
    queueid = None
    logfile =None
    if cli.job is not None :
       logger.debug("job name from cmd line: {} ".format(cli.job))
       jobname = cli.job
    if jobname is None:
       logger.error("'--job' setting is missing from cmd line")
       sys.exit(1)

    if cli.buildnum is not None:
       logger.debug("build num from cmd line: {} ".format(cli.buildnum))
       buildnum = cli.buildnum

    if cli.queueid is not None:
       logger.debug("queueid from cmd line: {} ".format(cli.queueid))
       queueid = cli.queueid

    if cli.logfile is not None:
       logger.debug("logfile from cmd line: {} ".format(cli.logfile))
       logfile = cli.logfile

    return (jobname, buildnum, queueid, logfile)


# check whether job is buildable
def is_job_buildable(server,jobname):
    if server.job_exists(jobname) != True :
        logger.error("job {} doesn't exist!".format(jobname))
        return False
    building = server.get_job_info(jobname)['buildable']
    return building

# get all history build numbers
def get_all_build_number(server,jobname):
    numbers = []
    if server.job_exists(jobname) != True :
        logger.error("job {} does not exist!")
        return numbers
    builds = server.get_job_info(jobname)['builds']
    for build in builds:
        numbers.append(build['number'])
    return numbers
  
# get build num from queueid
def get_buildnum_with_queueid(server,jobname,queueid):
    logger.info("get build num from queueid")
    numbers = get_all_build_number(server,jobname)
    buildnum = None
    for number in numbers:
        build = server.get_build_info(jobname,number)
        if build['queueId'] == int(queueid):
            buildnum = build['number']
            break
    return buildnum

# trigger a build and return the queueid
def trigger_build(server,jenkins_user, jenkins_password,jobname,parameters=None):
    if is_job_buildable(server,jobname) == False :
        logger.error("job is not buildable")
        return None
    if parameters is None:
        parameters = {}
    url = server.build_job_url(jobname,parameters)
    bcmd = "curl -i -s -X post '{}' --user '{}:{}'".format(url,jenkins_user, jenkins_password)
    logger.debug(bcmd)
    
    p = subprocess.Popen(bcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    responses = p.stdout.readlines()
    logger.debug(responses)

    for line in responses:
        pl = line.strip()
        if pl.startswith('Location:'):
            match = re.search(r'Location:\s*http://.*/queue/item/(\d+)/', pl)
            return match.group(1)
    return None


# check whether the queueid build is in the queue
def check_build_in_queue(server,queueid):
    logger.info("check build in queue")
    queues = server.get_queue_info()
    found = False
    for task in queues:
        if task['id'] == int(queueid):
            found = True
            logger.info("found queueid {} in queue".format(queueid))
            logger.info("queue_id={}".format(queueid))
            logger.info("job_name={}".format(task['task']['name']))
            logger.info("job_url={}".format(task['task']['url']))
            return True
    if found is False:
        logger.warning("not find queueid {} in queue".format(queueid))
        return False

#check history build status with queueid
def check_build_status_queueid(server,jobname,queueid):
    logger.info("check history builds")
    status = None
    buildnum = None
    buildurl = None
    found = False
    buildnum = get_buildnum_with_queueid(server,jobname,queueid)
    if buildnum is None:
        logger.info("not found queueid build in history builds")
    else:
        build = server.get_build_info(jobname,buildnum)
        if build['building'] is True:
            status = 'BUILDING'
        else:
            status = build['result']
        buildnum = build['number']
        buildurl = build['url']
        logger.info("found queueid {} build in history builds".format(queueid))
        logger.info("queue_id={}".format(queueid))
        logger.info("job_name={}".format(jobname))
        logger.info("build_num={}".format(buildnum))
        logger.info("build_url={} ".format(buildurl))
        logger.info("build_result={} ".format(status))
    return status

#check build status with build number
def check_build_status_buildnum(server,jobname,buildnum):
    logger.info("check history builds")
    logger.info("job_name={}".format(jobname))
    logger.info("build_num={}".format(buildnum))
    status = None
    numbers = get_all_build_number(server,jobname)
    logger.debug(numbers)
    if int(buildnum)  not in numbers:
        logger.warning("not found buildnum {} in history builds".format(buildnum))
        return status
    build = server.get_build_info(jobname,int(buildnum))
    logger.info("build_url={}".format(build['url']))
    if build['building'] is True:
        status = 'BUILDING'
    else:
        status = build['result']
    return status

# stop a running build with build number
def stop_running_build(server,jobname,buildnum):
    logger.info("stop running build,{},{}".format(jobname,buildnum))
    server.stop_build(jobname,buildnum)
    logger.info("wait some time and check the build status again")
    time.sleep(3)
    status = check_build_status_buildnum(server,jobname,buildnum)
    if status == "ABORTED":
        logger.info("succeed to stop running build")
    else:
        logger.info("failed to stop running build")
    return status


#cancel runnung build  with queueid
def cancel_running_build_queueid(server,jobname,queueid):
    logger.info("check history builds")
    status = None
    buildnum = None
    buildurl = None
    found = False
    buildnum = get_buildnum_with_queueid(server,jobname,queueid)
    if buildnum is None:
        logger.warning("not found queueid {} build in history builds".format(queueid))
    else:
        logger.info("found build number {}  with queueid {}".format(buildnum,queueid))
        build = server.get_build_info(jobname,buildnum)
        if build['building'] is True:
            logger.info("queueid {} build is building".format(queueid))
            status = stop_running_build(server,jobname,buildnum)
        else:
            logger.warning("queueid {} build was completed".format(queueid))
            status = build['result']
            buildnum = build['number']
            buildurl = build['url']
            logger.info("queue_id={}".format(queueid))
            logger.info("job_name={}".format(jobname))
            logger.info("build_num={}".format(buildnum))
            logger.info("build_url={} ".format(buildurl))
            logger.info("build_result={} ".format(status))
    return status

#cancel build with queueid
def cancel_build_with_queueid(server,jobname,queueid):
    logger.info("cancel build with queueid {}".format(queueid))
    status = None
    if check_build_in_queue(server,queueid):
        logger.info("cancel the queueid {} build".format(queueid))
        server.cancel_queue(int(queueid))
        logger.info("wait some time and check the queueid {} in queue again".format(queueid))
        time.sleep(3)
        if check_build_in_queue(server,queueid):
            logger.info("failed to cancel queued build")
            status = "QUEUED"
        else:
            logger.info("succeed to cancel queued build")
            status="CANCELLED"
    else:
        logger.info("cancel running build with queueid {}".format(queueid))
        status = cancel_running_build_queueid(server,jobname,queueid)
    return status

# action for sub command 'build'
def build(cli,jcs):
    server = jenkins.Jenkins(jcs['jenkins'], jcs['user'], jcs['password'])
    (job,parameters) = merge_build_conf(cli)
    logger.info("trigger a build")
    logger.info("jenkins_url={}".format(jcs['jenkins']))
    logger.info("job_name={}".format(job))
    logger.info("build_parameters={}".format(parameters)) 
    queueid = trigger_build(server,jcs['user'], jcs['password'], job, parameters)
    if queueid is not None:
        logger.info("succeed to trigger a build")
        logger.info("queue_id={}".format(queueid))
    else:
        logger.error("failed to trigger a build")
        sys.exit(1)
    

# action for sub command 'query'
def query(cli, jcs):
    logger.info("query a build")
    server = jenkins.Jenkins(jcs['jenkins'], jcs['user'], jcs['password'])
    (jobname, buildnum, queueid) = get_query_conf(cli)
    if  buildnum is not None:
        status = check_build_status_buildnum(server,jobname,buildnum)
    elif queueid is not None:
        if check_build_in_queue(server,queueid) is True:
            status = "QUEUED"
        else:
            status = check_build_status_queueid(server,jobname,queueid)
    if status is None:
        logger.warning("failed to determine build status")
        logger.info("build_status={} ".format(status))
        sys.exit(1)
    else:
        logger.info("build_status={} ".format(status))


# # action for sub command 'cancel'
def cancel(cli, jcs):
    logger.info("cancel a build")
    server = jenkins.Jenkins(jcs['jenkins'], jcs['user'], jcs['password'])
    (jobname, buildnum, queueid) = get_cancel_conf(cli)
    if buildnum is not None:
        status = check_build_status_buildnum(server,jobname,buildnum)
        if status is None:
            logger.warning("failed to determine build status")
            logger.info("build_status={} ".format(status))
            sys.exit(1)
        elif status == "BUILDING":
            status = stop_running_build(server,jobname,buildnum)
            logger.info("build_status={}".format(status))
        elif status == "ABORTED":
            logger.info("build was aborted")
            logger.info("build_status={}".format(status))
        else:
            logger.info("build was completed")
            logger.info("build_status={}".format(status))
            sys.exit(1)
    elif queueid is not None:
        status = cancel_build_with_queueid(server,jobname,queueid)
        if status is None:
            logger.warning("failed to determine build status")
            logger.info("build_status={}".format(status))
            sys.exit(1)
        elif status == "CANCELLED" or status == "ABORTED" :
            logger.info("build_status={}".format(status))
        else: 
            logger.info("build_status={}".format(status))
            sys.exit(1)

## action for sub command 'log'
def buildlog(cli,jcs):
    logger.info("fetch a build log")
    server = jenkins.Jenkins(jcs['jenkins'], jcs['user'], jcs['password'])
    (jobname, buildnum, queueid, logfile) = get_buildlog_conf(cli)
    if buildnum is None:
        logger.info("buildnum is None")
        if queueid is not None:
            logger.info("get the build num with queueid {}".format(queueid))
            buildnum = get_buildnum_with_queueid(server,jobname,queueid)
            if buildnum is None:
                logger.warning("not find the build num with queueid {}".format(queueid))
                logger.info("build_status=None")
                sys.exit(1)

    numbers = get_all_build_number(server,jobname)
    if int(buildnum)  not in numbers:
        logger.warning("not found buildnum {} in history builds".format(buildnum))
        logger.info("build_status=None")
        sys.exit(1)

    slog = server.get_build_console_output(jobname,buildnum)
    logger.info("job_name={}".format(jobname))
    logger.info("build_num={}".format(buildnum))
    if logfile is None:
        logger.info("build log : \n{}".format(slog))
    else:
        logger.info("write log to file {}".format(logfile))
        with open(logfile,'w') as log:
            log.write(slog)
    

# parse the command line options
def create_parser():
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument(
        '--conf',
        help="jenkins configuration file")
    parser.add_argument(
        '--user', '-u',
        help="Jenkins user for authentication, which overrides that specified in the configuration file.")
    parser.add_argument(
        '--password', '-p',
        help="Password of Jenkins user, which overrides that specified in the configuration file.")
    parser.add_argument(
        '--jenkins', '-j',
        help="Jenkins URL , which overrides that specified in the configuration file.")

    subparsers = parser.add_subparsers(help='commands')

    # A build command
    build_parser = subparsers.add_parser('build', help='trigger a build')
    build_parser.add_argument('--job', action='store', help='job name to trigger a build')
    build_parser.add_argument('--parameters',action='store', help='parameters to trigger a build', nargs='*')
    build_parser.set_defaults(func=build)

    #query a build 
    query_parser = subparsers.add_parser('query', help='query a build status')
    query_parser.add_argument('--job', action='store', help='job name',required=True)
    qg = query_parser.add_mutually_exclusive_group(required=True)
    qg.add_argument('--buildnum',action='store',type=int, help='build number')
    qg.add_argument('--queueid',action='store', type=int, help='build queue id')
    query_parser.set_defaults(func=query)

    #cancel/stop a build 
    cancel_parser = subparsers.add_parser('cancel', help='cancel/stop a queued/running build ')
    cancel_parser.add_argument('--job', action='store', help='job name',required=True)
    cg = cancel_parser.add_mutually_exclusive_group(required=True)
    cg.add_argument('--buildnum',action='store',type=int, help='build number')
    cg.add_argument('--queueid',action='store', type=int, help='build queue id')
    cancel_parser.set_defaults(func=cancel)

    #get build log
    buildlog_parser = subparsers.add_parser('log', help='fetch a build log')
    buildlog_parser.add_argument('--job', action='store', help='job name',required=True)
    blg = buildlog_parser.add_mutually_exclusive_group(required=True)
    blg.add_argument('--buildnum',action='store',type=int, help='build number')
    blg.add_argument('--queueid',action='store', type=int, help='build queue id')
    buildlog_parser.add_argument('--logfile',action='store', help='file name to store the build log')
    buildlog_parser.set_defaults(func=buildlog)

    return parser

# the main entry point
def main():
    parser = create_parser()
    cli= parser.parse_args()
    logger.debug(cli)
    confs = merge_jenkins_conf(cli)
    logger.debug(confs)
    cli.func(cli,confs)
    sys.exit(0)



# main function 
if __name__ == '__main__':
    sys.exit(main())


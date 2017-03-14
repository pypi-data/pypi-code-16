"""SUBSCRIBER.PY

Listen to all channels simc-autobahn publishes to.

Usage:
    subscriber.py start
    subscriber.py -h | --help

Options:
    -h --help           Show this screen.

"""
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from functools import partial
import configparser
from os import path
from docopt import docopt

conf = configparser.ConfigParser()
conf.read(path.join(path.dirname(__file__), '..', 'config.ini'))


class MyComponent(ApplicationSession):

    def onJoin(self, details):
        self.log.info(f"session ready on {conf['wamp']['uri']}, {conf['wamp']['realm']}")

        def onmsg(*args):
            self.log.info("\t".join([str(x) for x in args]))

        try:
            topics = [
                conf['wamp']['topic_keep_alive'],
                conf['worker']['topic_simc_log'],
                conf['caller']['topic_caller_log'],
                'wamp.subscription.on_subscribe',
                'wamp.registration.on_unregister'
            ]
            for el in iter(topics):
                self.subscribe(partial(onmsg, el), el)
                self.log.info(f"subscribed to topic {el}")
        except Exception as e:
            self.log.error(f"could not subscribe to topic: {e}")


if __name__ == '__main__':
    args = docopt(__doc__)
    runner = ApplicationRunner(url=conf['wamp']['uri'], realm=conf['wamp']['realm'])
    runner.run(MyComponent)


# """Baumeister
#
# Usage:
#     baumeister.py (start|stop|status|build|redeploy) (lokal|evo)
#
# """
# from docopt import docopt
# import subprocess
#
#
# docker_tag = "simc-autobahn"
#
#
# def build_cmd(cmd):
#     if args['evo']:
#         return ["docker", "-H", "evo:4243"] + cmd
#     else:
#         return ["docker"] + cmd
#
#
# def stop_all():
#     s = subprocess.check_output(build_cmd(["ps", "-q", "--filter", f"ancestor={docker_tag}"]), universal_newlines=True)
#     if s:
#         print(subprocess.check_output(build_cmd(["stop"] + s.splitlines())))
#     else:
#         print("nothing to stop")
#
#
# def is_running():
#     s = subprocess.check_output(build_cmd(['container', 'list']), universal_newlines=True)
#     return s.count(docker_tag)
#
#
# def start_one():
#     subprocess.run(build_cmd(["run", "-d", "simc-autobahn"]))
#
#
# def redeploy():
#     stop_all()
#     build()
#     start_one()
#
#
# def status():
#     nr = is_running()
#     if nr:
#         print(f"{docker_tag} is running {nr} times")
#     else:
#         print(f"{docker_tag} is NOT running")
#
#
# def build():
#     print(subprocess.check_output(build_cmd(["build", "-t", docker_tag, "."]), universal_newlines=True))
#
#
# if __name__ == '__main__':
#     args = docopt(__doc__, version='Baumeister 0.1')
#     if args['evo']:
#         print("\nRuning docker on evo")
#     else:
#         print("\nRunning docker on lokal")
#
#     if args['start']:
#         start_one()
#     if args['stop']:
#         stop_all()
#     if args['status']:
#         status()
#     if args['build']:
#         build()
#     if args['redeploy']:
#         redeploy()
#
#
# """EC2
# From: http://www.ybrikman.com/writing/2015/11/11/running-docker-aws-ground-up/
# 1. Lounch Instance
# 2. Choos Free Tier AMS Image, navigate to Tab Security Groups
# 3. Add Ports
# 4. Generate& save SSH Key
# > cd ~/my-aws-key-pairs
# > chmod 400 my-ec2-key-pair.pem
# > ssh -i my-ec2-key-pair.pem ec2-user@<EC2-INSTANCE-PUBLIC-IP-ADDRESS>
# 5. Login and Install DOcker
# [ec2-user]$ sudo yum update -y
# [ec2-user]$ sudo yum install -y docker
# [ec2-user]$ sudo service docker start
# [ec2-user]$ sudo usermod -a -G docker ec2-user
# [ec2-user]$ exit
#
# """


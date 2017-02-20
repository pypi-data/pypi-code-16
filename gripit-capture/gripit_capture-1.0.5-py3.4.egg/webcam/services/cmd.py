import os
import signal
import subprocess

class Cmd:
    def __init__(self):
        self.process = None

    def run(self, cmd):
        self.process = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        shell=True,
                                        preexec_fn=os.setsid)
        return self.process

    def kill(self):
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        self.process = None

import subprocess
import tempfile

from serapeum.backup import config
from serapeum.backup.modules.error import SubProcessError

from serapeum.backup.modules.ds.stack import Stack


class Run:

    def __init__(self):
        self.__cmd_output = ''
        self.c = config

    @property
    def cmd_output(self):
        return self.__cmd_output

    @cmd_output.setter
    def cmd_output(self, command_output):
        if command_output is not None:
            self.__cmd_output += command_output.decode('utf-8')

    def run(self, command):
        try:
            proc_output = subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            self.cmd_output = e.output
            raise SubProcessError('Failed to execute {0}: the subprocess returned an error: {1}'
                            .format(command[0], e.returncode))
        self.cmd_output = proc_output
        return self.cmd_output

    def zip_output(self, command, output_file):
        """
        Zip (using gzip) the output of command "command" to output_file
        :param command:
        :param output_file:
        :return:
        """
        op_fh = open(output_file, 'wb')
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        gzip = subprocess.Popen([self.c.config['SYSTEM']['gzip_path']], stdin=proc.stdout, stdout=op_fh)
        proc.stdout.close()
        op_fh.close()
        self.cmd_output = gzip.communicate()[0]
        return self.cmd_output

    def pipe(self, commands):
        pipes = Stack()
        cmd_output = []
        for command in commands:
            if pipes.peek() is not None:
                previous = pipes.pop()
                f_stdout = tempfile.TemporaryFile()
                proc = subprocess.Popen(command, stdin=previous.stdout, stdout=subprocess.PIPE)
                previous.stdout.close()
                pipes.add(previous)
            else:
                proc = subprocess.Popen(command, stdout=subprocess.PIPE)
            if proc.returncode != 0:
                self.cmd_output = proc.stderr
                raise SubProcessError('Failed to execute {0}: the subprocess returned an error: {1}'
                                .format(command[0], proc.returncode))
            pipes.add(proc)
            cmd_output.append(proc.communicate()[0])
            proc.wait()
        self.cmd_output = '|'.join(cmd_output)
        return self.cmd_output

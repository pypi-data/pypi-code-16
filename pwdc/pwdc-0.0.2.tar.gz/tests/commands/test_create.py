"""Tests for our `pwdc create` subcommand."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase


#This test will only works if you have a valid PWD server in your ~/.pwdc
class TestCreate(TestCase):

    def test_create_ok(self):
        output = popen(['pwdc', 'create'], stdout=PIPE).communicate()[0]
        lines = output.split('\n')
        self.assertTrue(len(lines) != 1)
        self.assertTrue('You can interract with your cluster' in output)

        #info
        output = popen(['pwdc', 'info'], stdout=PIPE).communicate()[0]
        self.assertTrue('You can View your session in a Browser' in output)
        self.assertTrue('eval $(pwdc env)' in output)

        output = popen(['pwdc', 'env'], stdout=PIPE).communicate()[0]
        self.assertTrue('export DOCKER_HOST=' in output)
        self.assertTrue('export DOCKER_MACHINE_NAME=' in output)


        #Clean
        output = popen(['pwdc', 'delete'], stdout=PIPE).communicate()[0]
        self.assertTrue('Session deleted, unset DOCKER_HOST and unset DOCKER_MACHINE_NAME' in output)



    def with_no_session(self):


        output = popen(['pwdc', 'delete'], stdout=PIPE).communicate()[0]
        self.assertTrue('No PWD Session, check --session_file parameter' in output)


        output = popen(['pwdc', 'env'], stdout=PIPE).communicate()[0]
        self.assertTrue('No PWD Session, check --session_file parameter' in output)


        output = popen(['pwdc', 'info'], stdout=PIPE).communicate()[0]
        self.assertTrue('No PWD Session, check --session_file parameter' in output)





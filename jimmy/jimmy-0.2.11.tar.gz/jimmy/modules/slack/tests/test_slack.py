# -*- coding: utf-8 -*-

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import mock
import mockfs
import os
import sys
from jimmy import cli
from click.testing import CliRunner
from jimmy.tests import base

modules_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
jimmy_dir = os.path.dirname(modules_dir)
slack_schema_path = os.path.join(modules_dir, 'slack', 'resources', 'schema.yaml')
jenkins_yaml_path = os.path.join(jimmy_dir, 'sample', 'input', 'jenkins.yaml')


class TestSlackModule(base.TestCase):

    def setup_method(self, method):
        self.runner = CliRunner()

    def teardown_method(self, method):
        mockfs.restore_builtins()

    @mock.patch('jimmy.lib.core.load_py_modules')
    @mock.patch('subprocess.call')
    def test_cli_call(self, mock_subp, mock_modules):
        with open(slack_schema_path, 'r') as f:
            mock_slack_schema = f.read()
        self.mfs = mockfs.replace_builtins()
        self.mfs.add_entries({os.path.join(jimmy_dir, 'lib', 'schema.yaml'): self.jimmy_schema,
                              os.path.join(jimmy_dir, 'jimmy.yaml'): self.mock_jimmy_yaml,
                              slack_schema_path: mock_slack_schema,
                              jenkins_yaml_path: '\n'.join(
                                  [
                                      'jenkins:',
                                      '  slack:',
                                      '    team_subdomain: slackteam',
                                      '    token: access-token',
                                      '    channel: "#build-notifications"',
                                      '    webhook_token: webhook-access-token',
                                      '    webhook_url: http://jenkins.example.com/slack-webhook/'
                                  ])
                              })
        sys.path.insert(0, modules_dir)
        import slack
        import read_source
        sys.path.pop(0)
        mock_modules.return_value = [slack, read_source]
        os.chdir(jimmy_dir)
        self.runner.invoke(cli)
        mock_subp.assert_called_with(
            ['java',
             '-jar', '<< path to jenkins-cli.jar >>',
             '-s', 'http://localhost:8080',
             'groovy',
             modules_dir + '/' + 'slack/resources/jenkins.groovy',
             'setSlackConfig',
             'slackteam', 'access-token', '', '#build-notifications',
             'webhook-access-token', 'http://jenkins.example.com/slack-webhook/'
             ], shell=False)
        assert 1 == mock_subp.call_count, "subprocess call should be equal to 1"

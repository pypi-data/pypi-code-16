#
# Commands to setup and instruct IRATI
#
#    Vincenzo Maffione <v.maffione@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301  USA

import rumba.ssh_support as ssh
from rumba.model import Experiment

# An experiment over the IRATI implementation
class IRATIExperiment(Experiment):
    def __init__(self, testbed, nodes = list()):
        Experiment.__init__(self, testbed, nodes)

    def setup(self):
        cmds = list()

        cmds.append("sudo apt-get update")
        cmds.append("sudo apt-get install g++ gcc "
                          "protobuf-compiler libprotobuf-dev git --yes")
        cmds.append("sudo rm -rf ~/irati")
        cmds.append("cd && git clone https://github.com/IRATI/stack irati")
        cmds.append("cd ~/irati && sudo ./install-from-scratch")
        cmds.append("sudo nohup ipcm &> ipcm.log &")

        for node in self.nodes:
            ssh.execute_commands(self.testbed, node.full_name, cmds, time_out = None)

    def run(self):
        print("[IRATI experiment] start")
        self.swap_in()
        print("Setting up IRATI on the nodes...")
        self.setup()
        print("[IRATI experiment] end")

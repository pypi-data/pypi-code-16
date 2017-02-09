#
# Commands to setup and instruct rlite
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

# An experiment over the RLITE implementation
class RLITEExperiment(Experiment):
    def __init__(self, testbed, nodes = list()):
        Experiment.__init__(self, testbed, nodes)

    def setup(self):
        cmds = list()

        cmds.append("sudo apt-get update")
        cmds.append("sudo apt-get install g++ gcc cmake "
                          "linux-headers-$(uname -r) "
                          "protobuf-compiler libprotobuf-dev git --yes")
        cmds.append("sudo rm -rf ~/rlite")
        cmds.append("cd ~; git clone https://github.com/vmaffione/rlite")
        cmds.append("cd ~/rlite && ./configure && make && sudo make install")
        cmds.append("sudo nohup rlite-uipcps -v DBG -k 0 -U -A &> uipcp.log &")

        for node in self.nodes:
            ssh.execute_commands(self.testbed, node.full_name, cmds, time_out = None)

    def run(self):
        print("[RLITE experiment] start")
        self.swap_in()
        print("Setting up rlite on the nodes...")
        self.setup()
        print("[RLITE experiment] end")

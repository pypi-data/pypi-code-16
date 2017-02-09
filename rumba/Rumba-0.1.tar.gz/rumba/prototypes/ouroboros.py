#
# Commands to instruct Ouroboros
#
#    Sander Vrijders   <sander.vrijders@intec.ugent.be>
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

# An experiment over the Ouroboros implementation
class OuroborosExperiment(Experiment):
    def __init__(self, testbed, nodes = list()):
        Experiment.__init__(self, testbed, nodes)

    def setup_ouroboros(self):
        cmds = list()

        cmds.append("sudo apt-get update")
        cmds.append("sudo apt-get install cmake protobuf-c-compiler git --yes")
        cmds.append("sudo rm -r ~/ouroboros/build")
        cmds.append("cd ~/ouroboros; sudo ./install_release.sh")
        cmds.append("sudo nohup irmd > /dev/null &")

        for node in self.nodes:
            ssh.execute_commands(self.testbed, node.full_name, cmds, time_out = None)
        return

    def bind_names(self):
        for node in self.nodes:
            cmds = list()
            for name, ap in node.bindings.items():
                cmds.append("irm b ap " + ap + " n " + name)

            ssh.execute_commands(self.testbed, node.full_name, cmds, time_out = None)

    def run(self):
        print("[Ouroboros experiment] start")
        print("Creating resources...")
        self.swap_in()
        print("Setting up Ouroboros...")
        self.setup_ouroboros()
        print("Binding names...")
        self.bind_names()
        print("[Ouroboros experiment] end")

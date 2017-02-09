#
# A library to manage ARCFIRE experiments
#
#    Sander Vrijders   <sander.vrijders@intec.ugent.be>
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

import abc

# Represents generic testbed info
#
# @username [string] user name
# @password [string] password
# @proj_name [string] project name
# @exp_name [string] experiment name
#
class Testbed:
    def __init__(self, exp_name, username, password, proj_name):
        self.username = username
        self.password = password
        self.proj_name = proj_name
        self.exp_name = exp_name

    @abc.abstractmethod
    def create_experiment(self, nodes, links):
        raise Exception('create_experiment() not implemented')


# Represents an interface on a node
#
# @name [string] interface name
# @ip [int] IP address of that interface
#
class Interface:
    def __init__(self, name = "", ip = ""):
        self.name = name
        self.ip = ip

# Represents a link in the physical graph
#
# @name [string] Link name
#
class Link:
    def __init__(self, name):
        self.name = name

# Represents a point-to-point link in the physical graph
#
# @name [string] DIF name
#
class P2PLink(Link):
    def __init__(self, name, node_a, node_b,
                 int_a = Interface(),
                 int_b = Interface()):
        Link.__init__(self, name)
        self.node_a = node_a
        self.node_b = node_b
        self.int_a = int_a
        self.int_b = int_b

def get_links(nodes):
    difs = set()
    links = list()
    for node in nodes:
        for dif in node.difs:
            if type(dif) is ShimEthDIF:
                difs.add(dif)

    for dif in difs:
        # Point-to-point link
        if len(dif.members) == 2:
            node_a = dif.members[0]
            node_b = dif.members[1]
            link = P2PLink(node_a.name + "-" + node_b.name,
                           node_a, node_b)
            links.append(link)

    return links

# Base class for DIFs
#
# @name [string] DIF name
#
class DIF:
    def __init__(self, name, members = list()):
        self.name = name
        self.members = members

    def __repr__(self):
        s = "DIF %s" % self.name
        return s

    def add_member(self, node):
        self.members.append(node)

    def del_member(self, node):
        self.members.remove(node)

# Shim over UDP
#
class ShimUDPDIF(DIF):
    def __init__(self, name, members = list()):
        DIF.__init__(self, name, members)

# Shim over Ethernet
#
# @link_speed [int] Speed of the Ethernet network, in Mbps
#
class ShimEthDIF(DIF):
    def __init__(self, name, members = list(), link_speed = 0):
        DIF.__init__(self, name, members)
        self.link_speed = int(link_speed)
        if self.link_speed < 0:
            raise ValueError("link_speed must be a non-negative number")

# Normal DIF
#
# @policies [dict] Policies of the normal DIF
#
class NormalDIF(DIF):
    def __init__(self, name, members = list(), policies = dict()):
        DIF.__init__(self, name, members)
        self.policies = policies

    def add_policy(self, comp, pol):
        self.policies[comp] = pol

    def del_policy(self, comp):
        del self.policies[comp]

    def __repr__(self):
        s = DIF.__repr__(self)
        for comp, pol in self.policies.items():
            s += "\n       Component %s has policy %s" % (comp, pol)
        return s

# A node in the experiment
#
# @difs: DIFs the node will have an IPCP in
# @dif_registrations: Which DIF is registered in which DIF
# @registrations: Registrations of names in DIFs
# @bindings: Binding of names on the processing system
#
class Node:
    def __init__(self, name, difs = list(),
                 dif_registrations = dict(),
                 registrations = dict(),
                 bindings = dict()):
        self.name = name
        self.difs = difs
        for dif in difs:
            dif.add_member(self)
        self.dif_registrations = dif_registrations
        self.registrations = registrations
        self.bindings = bindings
        self.full_name = name

    def __repr__(self):
        s = "Node " + self.name + ":\n"
        s += "  IPCPs in DIFs: ["
        for d in self.difs:
            s += " %s" % d.name
        s += " ]\n"
        s += "  DIF registrations: [ "
        for dif_a, difs in self.dif_registrations.items():
            s += "%s => [" % dif_a.name
            for dif_b in difs:
                s += " %s" % dif_b.name
            s += " ]"
        s += " ]\n"
        s += "  Name registrations: [ "
        for name, difs in self.registrations.items():
            s += "%s => [" % name
            for dif in difs:
                s += " %s" % dif.name
            s += " ]"
        s += " ]\n"
        s += "  Bindings: [ "
        for ap, name in self.bindings.items():
            s += "'%s' => '%s'"  % (ap, name)
        s += " ]\n"
        return s

    def add_dif(self, dif):
        self.difs.append(dif)
        dif.add_member(self)

    def del_dif(self, dif):
        self.difs.remove(dif)
        dif.del_member(self)

    def add_dif_registration(self, dif_a, dif_b):
        self.dif_registrations[dif_a].append(dif_b)

    def del_dif_registration(self, dif_a, dif_b):
        self.dif_registrations[dif_a].remove(dif_b)

    def add_registration(self, name, dif):
        self.dif_registrations[name].append(dif)

    def del_registration(self, name, dif):
        self.dif_registrations[name].remove(dif)

    def add_binding(self, name, ap):
        self.dif_bindings[name] = ap

    def del_binding(self, name):
        del self.dif_bindings[name]

# Base class for ARCFIRE experiments
#
# @name [string] Name of the experiment
# @nodes: Nodes in the experiment
#
class Experiment:
    def __init__(self, testbed, nodes = list()):
        self.nodes = nodes
        self.testbed = testbed

    def __repr__(self):
        s = ""
        for n in self.nodes:
            s += "\n" + str(n)

        return s

    def add_node(self, node):
        self.nodes.append(node)

    def del_node(self, node):
        self.nodes.remove(node)

    # Realize the experiment, using a testbed-specific setup
    def swap_in(self):
        self.links = get_links(self.nodes)
        self.testbed.create_experiment(self.nodes, self.links)

    @abc.abstractmethod
    def run(self):
        raise Exception('run() method not implemented')


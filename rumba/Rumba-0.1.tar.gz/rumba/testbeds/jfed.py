#
# jFed support for Rumba
#
#    Sander Vrijders  <sander.vrijders@intec.ugent.be>
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

import subprocess
import getpass
import xml.dom.minidom as xml

from rumba.model import Testbed

class jFedTestbed(Testbed):
    def __init__(self, exp_name, username, cert_file, jfed_jar, exp_hours = "2",
                 proj_name = "ARCFIRE", authority = "wall2.ilabt.iminds.be"):
        passwd = getpass.getpass(prompt = "Password for certificate file: ")
        Testbed.__init__(self, exp_name, username, passwd, proj_name)
        self.authority = "urn:publicid:IDN+" + authority + "+authority+cm"
        self.auth_name = authority
        self.cert_file = cert_file
        self.jfed_jar = jfed_jar
        self.exp_hours = exp_hours

    def create_rspec(self, nodes, links):
        self.rspec = self.exp_name + ".rspec"

        impl = xml.getDOMImplementation()
        doc = impl.createDocument(None, "rspec", None)

        top_el = doc.documentElement
        top_el.setAttribute("xmlns", "http://www.geni.net/resources/rspec/3")
        top_el.setAttribute("type", "request")
        top_el.setAttribute("xmlns:emulab", "http://www.protogeni.net/" +
                            "resources/rspec/ext/emulab/1")
        top_el.setAttribute("xmlns:jfedBonfire", "http://jfed.iminds.be/" +
                            "rspec/ext/jfed-bonfire/1")
        top_el.setAttribute("xmlns:delay", "http://www.protogeni.net/" +
                            "resources/rspec/ext/delay/1")
        top_el.setAttribute("xmlns:jfed-command", "http://jfed.iminds.be/" +
                            "rspec/ext/jfed-command/1")
        top_el.setAttribute("xmlns:client", "http://www.protogeni.net/" +
                            "resources/rspec/ext/client/1")
        top_el.setAttribute("xmlns:jfed-ssh-keys", "http://jfed.iminds.be/" +
                            "rspec/ext/jfed-ssh-keys/1")
        top_el.setAttribute("xmlns:jfed", "http://jfed.iminds.be/rspec/" +
                            "ext/jfed/1")
        top_el.setAttribute("xmlns:sharedvlan", "http://www.protogeni.net/" +
                            "resources/rspec/ext/shared-vlan/1")
        top_el.setAttribute("xmlns:xsi", "http://www.w3.org/2001/" +
                            "XMLSchema-instance")
        top_el.setAttribute("xsi:schemaLocation", "http://www.geni.net/" +
                            "resources/rspec/3 http://www.geni.net/" +
                            "resources/rspec/3/request.xsd")

        for node in nodes:
            el = doc.createElement("node")
            top_el.appendChild(el)
            el.setAttribute("client_id", node.name)
            el.setAttribute("exclusive", "true")
            el.setAttribute("component_manager_id", self.authority)

            el2 = doc.createElement("sliver_type")
            el.appendChild(el2)
            el2.setAttribute("name", "raw-pc")

            node.ifs = 0
            for link in links:
                if link.node_a == node or link.node_b == node:
                    el3 = doc.createElement("interface")
                    if link.node_a == node:
                        link.int_a.id = node.name + ":if" + str(node.ifs)
                        link_id = link.int_a.id
                    if link.node_b == node:
                        link.int_b.id = node.name + ":if" + str(node.ifs)
                        link_id = link.int_b.id

                    el3.setAttribute("client_id", link_id)
                    node.ifs += 1
                    el.appendChild(el3)

        for link in links:
            el = doc.createElement("link")
            top_el.appendChild(el)
            el.setAttribute("client_id", link.name)

            el2 = doc.createElement("component_manager_id")
            el2.setAttribute("name", self.authority)
            el.appendChild(el2)

            el3 = doc.createElement("interface_ref")
            el3.setAttribute("client_id", link.int_a.id)
            el.appendChild(el3)

            el4 = doc.createElement("interface_ref")
            el4.setAttribute("client_id", link.int_b.id)
            el.appendChild(el4)

        file = open(self.rspec, "w")
        file.write(doc.toprettyxml())
        file.close()

    def create_experiment(self, nodes, links):
        self.create_rspec(nodes, links)
        self.manifest = self.exp_name + ".rrspec"

        for node in nodes:
            auth_name_r = self.auth_name.replace(".", "-")
            node.full_name = node.name + "." + self.exp_name + "." + \
                             self.proj_name + "." + auth_name_r + \
                             "." + self.auth_name

        subprocess.call(["java", "-jar", self.jfed_jar, "create", "-S", \
                         self.proj_name, "--rspec", \
                         self.rspec, "-s", \
                         self.exp_name, "-p", self.cert_file, "-k", \
                         "usercert,userkeys,shareduserallkeys", \
                         "--create-slice",\
                         "--manifest", self.manifest,
                         "-P", self.password, \
                         "-e", self.exp_hours])

        rspec = xml.parse(self.manifest)
        xml_nodes = rspec.getElementsByTagName("node")

        for xml_node in xml_nodes:
            n_name = xml_node.getAttribute("client_id")
            intfs = xml_node.getElementsByTagName("interface")
            for link in links:
                if link.node_a.name == n_name:
                    interface = link.int_a
                if link.node_b.name == n_name:
                    interface = link.int_b
            for intf in intfs:
                comp_id = intf.getAttribute("component_id")
                comp_arr = comp_id.split(":")
                interface.name = comp_arr[-1]
                xml_ip = intf.getElementsByTagName("ip")
                interface.ip = xml_ip[0].getAttribute("address")

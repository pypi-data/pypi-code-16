#
# SSH support for Rumba
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

import paramiko

def get_ssh_client():
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    return ssh_client

def execute_commands(testbed, hostname, commands, time_out = 3):
    '''
    Remote execution of a list of shell command on hostname. By
    default this function will exit (timeout) after 3 seconds.

    @param testbed: testbed info
    @param hostname: host name or ip address of the node
    @param command: *nix shell command
    @param time_out: time_out value in seconds, error will be generated if
    no result received in given number of seconds, the value None can
    be used when no timeout is needed
    '''
    ssh_client = get_ssh_client()

    try:
        ssh_client.connect(hostname, 22,
                           testbed.username, testbed.password,
                           look_for_keys = True, timeout = time_out)
        for command in commands:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            err = str(stderr.read()).strip('b\'\"\\n')
            if err != "":
                err_array = err.split('\\n')
                for erra in err_array:
                    print(erra)
        ssh_client.close()

    except Exception as e:
        print(str(e))
        return

def execute_command(testbed, hostname, command, time_out = 3):
    '''
    Remote execution of a list of shell command on hostname. By
    default this function will exit (timeout) after 3 seconds.

    @param testbed: testbed info
    @param hostname: host name or ip address of the node
    @param command: *nix shell command
    @param time_out: time_out value in seconds, error will be generated if
    no result received in given number of seconds, the value None can
    be used when no timeout is needed

    @return: stdout resulting from the command
    '''
    ssh_client = get_ssh_client()

    try:
        ssh_client.connect(hostname, 22,
                           testbed.username, testbed.password,
                           look_for_keys = True, timeout = time_out)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        err = str(stderr.read()).strip('b\'\"\\n')
        if err != "":
            print(err)
        output = str(stdout.read()).strip('b\'\"\\n')
        ssh_client.close()

        return output

    except Exception as e:
        print(str(e))
        return

def copy_file_to_testbed(testbed, hostname, text, file_name):
    '''
    Write a string to a given remote file.
    Overwrite the complete file if it already exists!

    @param testbed: testbed info
    @param hostname: host name or ip address of the node
    @param text: string to be written in file
    @param file_name: file name (including full path) on the host
    '''
    ssh_client = get_ssh_client()

    try:
        ssh_client.connect(hostname, 22,
                           testbed.username,
                           testbed.password,
                           look_for_keys=True)

        cmd = "touch " + file_name + \
              "; chmod a+rwx " + file_name

        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        err = str(stderr.read()).strip('b\'\"\\n')
        if err != "":
            print(err)

        sftp_client = ssh_client.open_sftp()
        remote_file = sftp_client.open(file_name, 'w')

        remote_file.write(text)
        remote_file.close()

    except Exception as e:
        print(str(e))

def setup_vlan(testbed, node_name, vlan_id, int_name):
    '''
    Gets the interface (ethx) to link mapping

    @param testbed: testbed info
    @param node_name: the node to create the VLAN on
    @param vlan_id: the VLAN id
    @param int_name: the name of the interface
    '''
    print("Setting up VLAN on node " + node_name)

    node_full_name = full_name(node_name, testbed)
    cmd = "sudo ip link add link " + \
          str(int_name) + \
          " name " + str(int_name) + \
          "." + str(vlan_id) + \
          " type vlan id " + str(vlan_id)
    execute_command(testbed, node_full_name, cmd)
    cmd = "sudo ifconfig " + \
          str(int_name) + "." + \
          str(vlan_id) + " up"
    execute_command(node_full_name, cmd, testbed)
    cmd = "sudo ethtool -K " + \
          str(int_name) + " rxvlan off"
    execute_command(node_full_name, cmd, testbed)
    cmd = "sudo ethtool -K " + \
          str(int_name) + " txvlan off"
    execute_command(node_full_name, cmd, testbed)

#!/build/ltesdkroot/Tools/Tools/python/python-2.7.2/bin/python

#######################################################################################################################
#    The tool is used for checking the storage status of LRC knife building slave servers.                            #
#    Date: 07/12/2016                                                                                                 #
#    Author:                                                                                                          #
#    Input:                                                                                                           #
#       1. -n Slave server node label name on jenkins, e.g., knifeSlaveServer                                         #
#       2. -c Jenkins config file name                                                                                #
#       3. -p Jenkins config file path.                                                                               #
#    Output:                                                                                                          #
#       1. result is put in branch_build/Finding_copy_result.txt                                                      #
#       format in Finding_copy_result.txt is as bellow:                                                               #
#       LBR:DNH4.0_ENB_1606_100_01                                                                                    #
#       2. If the scripts execute fail, a file of "Finding_copy_fail.txt" will be generated in folder "branch_build". #
#######################################################################################################################

import getopt
import string
import sys
import re
import os
import subprocess
import traceback
import smtplib
import email
import xml.etree.cElementTree as ElementTree
from email.header import Header
from email.mime import multipart
from email.mime import base
from email.mime import text
from email import encoders


WORK_SPACE_NAME = "workspace"
OUTPUT_FILE = "output.txt"


class GetSlaveServerStorage(object):
    """
    This class is used for searching the branch build that use the same FPGA as trunk.
    """
    WARNING_LINE = "80%"
    USED_TYPE_MORE = "more"
    USED_TYPE_LESS = "less"

    def __init__(self, node_name, configuration_name, configuration_path):
        self.node_label = node_name
        self.conf_name = configuration_name
        self.conf_path = configuration_path
        self.user_name = "microci"
        self.server_used_dict = {}
        self.email_send_type = ""

    def check_config_file(self):
        log("Info: Check config file start. file name: " + self.conf_name + ", path:" + self.conf_path + ".")
        file_dir = os.path.join(self.conf_path, self.conf_name)
        if not os.path.exists(file_dir):
            log("Error: Configuration file does not exit.")
            exit(1)
        log("Info: Configuration file exits.")

    def get_slave_server_list(self):
        result = []
        xml_file = os.path.join(self.conf_path, self.conf_name)
        if not os.path.exists(xml_file):
            log("Warn: can not prase the xml file " + xml_file + ", as it is no exist.")
            sys.exit(1)
        try:
            xml_tree = ElementTree.parse(xml_file)
            root = xml_tree.getroot()
            for content in root.findall("slaves"):
                for element in content.findall("slave"):
                    label_obj = element.find("label")
                    if label_obj is None:
                        log("Warn: There is Null object in label.")
                        continue
                    label_string = label_obj.text
                    if label_string is None:
                        log("Warn: There is Null string in label.")
                        continue
                    label_string_list = label_string.split()
                    for lab_name in label_string_list:
                        if lab_name == self.node_label:
                            host = element.find("launcher/host")
                            server_name = host.text
                            log("Info: Find a host for knife slave server: " + server_name)
                            if server_name not in result:
                                result.append(server_name)
            log("Info: Find slave server success.")
        except ElementTree.ParseError:
            log("ERROR: Parse xml error, the xml file = " + xml_file)
            exit(1)
        else:
            log("Info: knife slave server list: " + repr(result))
            return result

    def copy_jenkins_configuration_file(self):
        log("Info: Copy config file start. file name: " + self.conf_name + ", path:" + self.conf_path + ".")
        file_dir = os.path.join(self.conf_path, self.conf_name)
        if not os.path.exists(self.conf_name):
            open(self.conf_name, "wb").write(open(file_dir, "rb").read())
        log("Info: Copy config file end.")

    def get_server_disk_used(self, server_name):
        p = subprocess.Popen(['ssh', self.user_name + '@' + server_name, 'df -kh /var/fpwork'],
                             stdout=subprocess.PIPE)
        used_percent = "0"
        info = p.stdout.read()
        log(server_name + " disk information : " + info)
        info_lines = info.split('\n')
        if not len(info_lines) == 4 and not len(info_lines) == 3:
            log("Warn: Return information from server error.")
            return
        print_to_out_file(server_name, info)
        for line in info_lines:
            if not line == "" and not line.find("/var/fpwork") == -1:
                str_list = line.split()
                for strr in str_list:
                    if strr.find("%") != -1:
                        log("Info: " + server_name + " : " + strr)
                        if server_name not in self.server_used_dict.keys():
                            self.server_used_dict[server_name] = strr
                            used_percent = strr
                            break
        log("Info: Get server " + server_name + " disk used end. Used : " + used_percent)

    def check_used_information(self):
        log("Info: Start to check disk used information in knife build slave servers.")
        self.email_send_type = GetSlaveServerStorage.USED_TYPE_LESS
        for server_name in self.server_used_dict.keys():
            used_info = self.server_used_dict.get(server_name)
            log("Info: Server: " + server_name + " , disk used " + used_info)
            if used_info > GetSlaveServerStorage.WARNING_LINE:
                log("Info: Disk used more than " + GetSlaveServerStorage.WARNING_LINE + "......")
                self.email_send_type = GetSlaveServerStorage.USED_TYPE_MORE
        log("Info: Check used info end, email_send_type = " + self.email_send_type)

    def send_email(self):
        log("Info: Start to send email, type = " + self.email_send_type)
        mail(self.email_send_type)

    def start(self):
        self.check_config_file()
        self.copy_jenkins_configuration_file()
        slave_server_list = self.get_slave_server_list()
        if len(slave_server_list) == 0:
            log("Warn: There is no slave server list.")
            return
        for server in slave_server_list:
            log("Info: Start to get the server: " + server + " disk used information.")
            self.get_server_disk_used(server)
        self.check_used_information()
        self.send_email()


def template_more():
    template_string = '''
            <html>
                <body>
                <div>Hello SCM,</div>
                <div>
                <p><b>WARN: More than 80% disk space is used in knife slave servers.</b><p>
                <code>$attach_code</code>
                </body>
            </html>
            '''
    return template_string


def template_less():
    template_string = '''
            <html>
                <body>
                <div>Hello SCM,</div>
                <div>
                <p><b>The knife slave server disk space is OK.</b><p>
                <code>$attach_code</code>
                </body>
            </html>
            '''
    return template_string


def mail(template_name):
    sender_ad = 'xuping.xu@nokia.com'
    to = 'xuping.xu@nokia.com; jb.xu@nokia.com; jie.wang@nokia.com; zhong.yu@nokia.com'
    # to = 'xuping.xu@nokia.com'
    server = 'mail.emea.nsn-intra.net'
    log("Info: Send mail type = " + template_name)
    if template_name == GetSlaveServerStorage.USED_TYPE_LESS:
        template = template_less()
        attached_file_list = list()
        attached_file_list.append(OUTPUT_FILE)
        subject = "Info: Disk space in knife build servers is OK."
    elif template_name == GetSlaveServerStorage.USED_TYPE_MORE:
        template = template_more()
        attached_file_list = list()
        attached_file_list.append(OUTPUT_FILE)
        subject = "Alert!!!!: Almost out of disk space 80% in knife slave servers, please take action!!!."
    else:
        log("Info: There is no the mail type: " + template_name + ", and return.")
        return

    mail_data = dict()

    if os.path.exists(OUTPUT_FILE):
        info_list = []
        file_handle = open(OUTPUT_FILE, "rb")
        for line in file_handle:
            line_more = "<p>" + line.strip() + "</p>"
            info_list.append(line_more)
        file_handle.close()
        attach_info = "".join(info_list)
        log("Info: attinfo = " + attach_info)
        mail_data["attach_code"] = attach_info
    else:
        mail_data["attach_code"] = ""

    TEMPLATE = string.Template(template)
    html_data = TEMPLATE.safe_substitute(mail_data)
    send(server, sender_ad, to, subject, html_data, attached_file_list)


def send(server_URL = None, sender='', to='', subject='', content='', attach=None):
    """
    Usage of mail() function:
    mail('somemailserver.com', 'me@example.com', 'someone@example.com', 'test', 'This is a test',file_to_be_attached)
    """
    log("Info: start to send email.")
    message = multipart.MIMEMultipart()
    message['From'] = sender
    message['To'] = to
    message['Subject'] = Header(subject)
    message.attach(text.MIMEText(content, _subtype='html'))
    if attach:
        for i in attach:
            log("Info: file " + i + " should be attached. current folder = " + os.getcwd())
            part = email.mime.base.MIMEBase('application', 'octet-stream')
            part.set_payload(open(i, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(i))
            message.attach(part)
    mailServer = smtplib.SMTP(server_URL)
    mailServer.sendmail(sender, to.split(), message.as_string())
    mailServer.quit()


def usage(file_name):
    usage_text = """
    $text_name have follow parameter for use. "-n" "-p" and "-c" are mandatory.
    -n: Slave server node label name on jenkins, e.g., knifeSlaveServer.
    -c: Jenkins configuration file name.
    -p: Jenkins configuration file path.
    """
    usage_s = string.Template(usage_text)
    param = {"text_name": file_name}
    print(usage_s.safe_substitute(param))


def recreate_workspace():
    os.system("rm -rf " + WORK_SPACE_NAME)
    os.system("mkdir " + WORK_SPACE_NAME)
    os.chdir(WORK_SPACE_NAME)


def print_to_out_file(server, info):
    with open(OUTPUT_FILE, 'a') as out_file:
        out_file.write(server + " disk used information: " + "\n")
        out_file.write(info)
        out_file.write("\n")


def log(msg):
    with open('get_slave_server_disk.log', 'a') as log_file:
        print(msg)
        log_file.write(msg + '\n')


if __name__ == '__main__':
    node_label = ""
    conf_name = ""
    conf_path = ""
    if len(sys.argv) > 1:
        try:
            options, args = getopt.getopt(sys.argv[1:], "n:c:p:", ["node-label", "conf-name", "conf-path"])
        except getopt.GetoptError:
            usage(sys.argv[0])
            sys.exit(1)
    else:
        usage(sys.argv[0])
        sys.exit(1)
    for name, value in options:
        if name in ("-n", "--node-label"):
            node_label = value
        elif name in ("-c", "--conf-name"):
            conf_name = value
        elif name in ("-p", "--conf-path"):
            conf_path = value
        else:
            usage(sys.argv[0])
            sys.exit(1)

    if node_label == '' or conf_name == "" or conf_path == '':
        usage(sys.argv[0])
        sys.exit(1)

    recreate_workspace()
    finding = GetSlaveServerStorage(node_label, conf_name, conf_path)
    finding.start()
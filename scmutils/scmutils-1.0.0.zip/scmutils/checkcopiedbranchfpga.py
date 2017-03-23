#!/build/ltesdkroot/Tools/Tools/python/python-2.7.2/bin/python

#######################################################################################################################
#    The tool is used for                                                                                             #
#         1 Check if the modified FPGA correct according to PROGRAM defined.                                          #
#         2 Finding latest used FPGA version in branch(e.g. 16B). And check if it is the same one as the load         #
#           workspace.                                                                                                #
#    Date:08/02/2017                                                                                                  #
#    Author:                                                                                                          #
#    Input:                                                                                                           #
#       Usage()                                                                                                       #
#    Output:                                                                                                          #
#       1. If there is no exception. The checked file name is the same as based branch.                               #
#       Return success.                                                                                               #
#       2. If there is exception.                                                                                     #
#       Return with failed. And send out the notification email.                                                      #
#######################################################################################################################

import getopt
import string
import sys
import re
import os
import urllib2
import traceback
import smtplib
import email
import xml.etree.cElementTree as cElementTree
import subprocess
from email.header import Header
from email.mime import multipart
from email.mime import base
from email.mime import text
from email import encoders


FEP_TYPE_LIST = ['LCP____SO_E', 'LCP____AO_E', 'LSP____OS_E', 'LSP____OS_B', 'LCP____SF_E', 'LSP____LT_E',
                 'LSP____3G_B', 'LNI____F__E', 'LCA____F__E', 'LBR____F__E']
FPGA_MAPPING_DICT = {"PS_LFS_FW_AGUSTA": "LCA", "PS_LFS_FW_TRIUMPH": "LNI", "PS_LFS_FW_HARLEY": "LBR",
                     "PS_LFS_FW_SIDECAR": "LBR"}
FPGA_LIST = ["LCA", "LNI", "LBR"]
WORK_SPACE_NAME = "CHECK_FPGA"
RESULT_FAIL_FILE_NAME = "Finding_copy_fail.txt"
WFT_ROOT_RELEASE_NOTES = "https://wft.inside.nsn.com/ext/releasenote"
WFT_ROOT_BUILD_CONTENT = "https://wft.int.net.nokia.com/ext/build_content"
BRANCH_LFS_NAME_MAPPING_DICT = {"16A": "FB_LRC_LCP_PS_LFS_OS_2015_12", "16B": "FB_LRC_LCP_PS_LFS_OS_2016_06",
                                "17A": "FB_LRC_LCP_PS_LFS_OS_2016_11", "16Ba": "FB_LRC_LCP_PS_LFS_OS_2017_01"}
BRANCH_ENB_DICT = {"16A": "DNH3.0_ENB", "16B": "DNH4.0_ENB_1606_[12345]", "16Ba": "DNH4.0_ENB_1606_[6789]",
                   "17A": "DNH5.0_ENB"}
EMAIL_TYPE_FAIL = "failed"
EMAIL_TYPE_FAIL_FURTHER = "failed_further"
EMAIL_TYPE_SUCCESS = "success"
EMAIL_TYPE_HALF = "half_success"
CFG_NAME_MAPPING = {"17A": "DNH5.0_PRE_RELEASE_CFG"}
# CFG_NAME_MAPPING = {"17A": "DNH5.0_UNCHANGED_SPECIAL_CFG"}
CFG_REPO = "https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_LTE/builds/branches/lrc/LRCFEP_CFG/"
COPYINFO_REPO = "http://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_LTE/builds/tags/"
COPYINFO_NAME = "copyinfo.txt"
TO = ""


class ExceptNotFind(Exception):
    pass


class ExceptUnknown(Exception):
    pass


class ExceptNotMatch(Exception):
    """
    The exception is used to Mark the found FPGA files in base branch are not the same as it is in current branch.
    """
    pass


class BaseClass(object):

    @staticmethod
    def get_list_from_xml2(xml_file, content, element, regex=''):
        """
        Used for parse LCP LFS OS baseline to get FPGA baselines.
        :param xml_file:
        :param content:
        :param element:
        :param regex:
        :return:
        """
        result = []
        if not os.path.exists(xml_file):
            log("WARN: Can not parse the xml file: " + xml_file + ", as it does no exist.")
            return result
        try:
            xml_tree = cElementTree.parse(xml_file)
            root = xml_tree.getroot()
            for content in root.findall(content):
                for elem in content.findall(element):
                    elem_name = elem.text
                    if not regex == '':
                        if re.search(regex, elem_name):
                            result.append(elem_name)
                    else:
                        result.append(elem_name)
        except cElementTree.ParseError as e:
            raise e
        except:
            raise ExceptUnknown()
        else:
            return result

    @staticmethod
    def parse_xml2(xml_file, content, element, regex=''):
        """
        Used for parse LCP LFS OS baseline in enb content xml file.
        :param xml_file:
        :param content:
        :param element:
        :param regex:
        :return: List
        """
        result = []
        if not os.path.exists(xml_file):
            log("Warn: can not parse the xml file " + xml_file + ", as it does no exist.")
            return result
        try:
            xml_tree = cElementTree.parse(xml_file)
            root = xml_tree.getroot()
            for content_content in root.findall(content):
                for element_content in content_content.findall(element):
                    sc_name = element_content.text
                    sc_type = element_content.get("sc")
                    if not regex == "":
                        if re.search(regex, sc_type):
                            result.append(sc_name)
                    else:
                        result.append(sc_name)
        except cElementTree.ParseError as e:
            log(traceback.format_exc())
            raise e
        except Exception as e:
            log(traceback.format_exc())
            raise e
        else:
            log("INFO: parse_xml2 for " + xml_file + ", the result == " + repr(result))
            return result

    @staticmethod
    def get_enb_build_list_from_lfs_xml(xml_file, content1, content2, content3, content4, regex):
        """
        Used for parse xml for 4 input tag.
        :param xml_file:
        :param content1:
        :param content2:
        :param content3:
        :param content4:
        :param regex:
        :return:
        """
        result = []
        if not os.path.exists(xml_file):
            log("ERROR: can not parse the xml file " + xml_file + ", as it is no exist.")
            raise Exception("ERROR: No " + xml_file + " to parse.")
        try:
            xml_tree = cElementTree.parse(xml_file)
            root = xml_tree.getroot()
            for content in root.findall(content1):
                for element in content.findall(content2):
                    for item in element.findall(content3):
                        for build in item.findall(content4):
                            build_name = build.text
                            if 'state' not in build.attrib.keys():
                                build_status = None
                            else:
                                build_status = build.attrib.get('state')
                            if build_status is None or not build_status == "released":
                                # log("INFO: Find a baseline: " + build_name + " without released status.")
                                continue
                            if re.search(regex, build_name):
                                log("INFO: Find a ENB baseline " + build_name)
                                result.append(build_name)
        except cElementTree.ParseError as e:
            log("ERROR: parse xml error, the xml file = " + xml_file)
            raise e
        except Exception as e:
            raise e
        else:
            log("Info: get_enb_build_list_from_lfs_xml end.")
            log(repr(result))
            return result

    @staticmethod
    def get_fpga_type_from_baseline(fpga_baseline):
        for type in FPGA_MAPPING_DICT.keys():
            if fpga_baseline.find(type) != -1:
                return FPGA_MAPPING_DICT.get(type)

    @staticmethod
    def get_build_content_from_wft(baseline):
        global WFT_ROOT_BUILD_CONTENT
        log("Info: Get baseline information xml from WFT for " + baseline)
        baseline_content_file_name = baseline + ".xml"
        if os.path.exists(baseline_content_file_name):
            log("Info: The baseline content xml file has been downloaded.")
            return baseline_content_file_name
        try:
            req = urllib2.Request(WFT_ROOT_BUILD_CONTENT + "/" + baseline)
            response = urllib2.urlopen(req)
            the_page = response.read()
            file_handle = open(baseline_content_file_name, "w")
            file_handle.write(the_page)
            file_handle.close()
        except urllib2.HTTPError as e:
            log("Error: Could not get LFS xml from WFT. Baseline = " + baseline)
            raise e
        except IOError as e:
            log("Error: Write LFS xml to a file error.")
            raise e
        except:
            raise ExceptUnknown("Unknown exception...")
        log("INFO: Get baseline content end for " + baseline)
        return baseline_content_file_name

    @staticmethod
    def export_svn_file(svn_path, file_name):
        """
        The svn_path should be end with "/", e.g., "https://xxx/ccc/bbb/"
        :param svn_path:
        :param file_name:
        :return:
        """
        log("INFO: Begin to get the cfg file from: " + svn_path + file_name)
        if not os.path.exists(file_name):
            svn_command = "svn export " + svn_path + file_name
            try:
                # subprocess.Popen(svn_command, stdout=subprocess.PIPE)
                os.system(svn_command)
            except Exception as e:
                log("ERROR: svn export cfg file error.")
                raise e
        log("INFO: Succeed to get the cfg file:" + file_name + " from svn.")
        return file_name


class CheckPreConfigFile(BaseClass):
    """
    This class is used for check:
    When pre-release configuration file change, it means that LC tell ENB SCM to modify
    copy FPGA files from based branch release. The class is used to check is the used FPGA files in branch the same
    as in current ENB load building.
    If not the same, means that the modification is earlier than FPGA code commit into current branch. SCM need to
    hands up to LC to confirm.
    If they are the same, it is OK.
    """

    def __init__(self, curr_branch, enb_version, curr_fpga_v):
        self.branch = curr_branch
        self.enb_baseline = enb_version
        self.fpga_v_dict = curr_fpga_v
        self.base_enb_baseline = ""
        self.base_fpga_v_dict = {"PS_LFS_FW_AGUSTA": "", "PS_LFS_FW_TRIUMPH": "", "PS_LFS_FW_HARLEY": "",
                                 "PS_LFS_FW_SIDECAR": ""}
        self.cfg_fpga_enb_mapping = {"LCA": [], "LNI": [], "LBR": []}
        self.cfg_fpga_enb_mapping_base = {"LCA": [], "LNI": [], "LBR": []}
        self.changed_list = []
        self.error_dict = {}

    def get_fpga_enbname_mapping(self, file_name, enb_type="base"):
        log("INFO: Begin to get the mapping of FPGA type and name, branch ENB load.")
        if not os.path.exists(file_name):
            raise Exception("ERROR: CFG file does not exist.")
        type_list = self.cfg_fpga_enb_mapping.keys()
        for line in open(file_name):
            if line == "":
                continue
            line_clean = line.strip()
            fep_enb_list = line_clean.split(':')
            for key_type in type_list:
                if line_clean.find(key_type) != -1:
                    if enb_type == "base":
                        self.cfg_fpga_enb_mapping_base[key_type] = fep_enb_list
                    else:
                        self.cfg_fpga_enb_mapping[key_type] = fep_enb_list
                    break
        if enb_type == "base":
            log("INFO: End to get the mapping: " + repr(self.cfg_fpga_enb_mapping_base))
        else:
            log("INFO: End to get the mapping: " + repr(self.cfg_fpga_enb_mapping))

    def get_pre_cfg_file(self, branch):
        log("INFO: Begin to get the cfg file from svn.")
        global CFG_NAME_MAPPING
        global CFG_REPO
        branch_list = CFG_NAME_MAPPING.keys()
        if branch not in branch_list:
            raise ValueError("ERROR: Input current branch error.")
        file_name = CFG_NAME_MAPPING.get(branch)
        try:
            self.export_svn_file(CFG_REPO, file_name)
        except Exception as e:
            raise e
        return file_name

    def get_based_enb_baseline(self, baseline):
        baseline_xml = baseline + ".xml"
        try:
            if not os.path.exists(baseline_xml):
                self.get_build_content_from_wft(baseline)

            xml_tree = cElementTree.parse(baseline_xml)
            root = xml_tree.getroot()
            base_enb = root.find("diff")
            enb_load = base_enb.get("to")
            self.base_enb_baseline = enb_load
        except Exception as e:
            log(traceback.format_exc())
            raise e
        else:
            log("INFO: End get based enb load, result = " + self.base_enb_baseline)
            return enb_load

    def get_base_enb_copyinfo_file(self):
        global COPYINFO_REPO
        global COPYINFO_NAME
        try:
            base_enb_baseline = self.get_based_enb_baseline(self.enb_baseline)
            if base_enb_baseline is None or base_enb_baseline == "":
                raise ValueError("ERROR: Could not get base ENB load.")
            svn_repo = COPYINFO_REPO + base_enb_baseline + "/"
            self.export_svn_file(svn_repo, COPYINFO_NAME)
        except Exception as e:
            raise e
        else:
            return COPYINFO_NAME

    def calculate_copied_number(self):
        """
        Only current copied FPGA from branch number > "Copy number in base ENB load", return False.
        :return:
        """
        result = True
        curr_number = 0
        base_number = 0
        for key, value_v in self.cfg_fpga_enb_mapping.viewitems():
            if isinstance(value_v, list) and len(value_v) > 0:
                curr_number += 1
        for key, value_v in self.cfg_fpga_enb_mapping_base.viewitems():
            if isinstance(value_v, list) and len(value_v) > 0:
                base_number += 1
        if curr_number > base_number:
            result = False
        log("INFO: Check copied FPGA number, curr_number = " + repr(curr_number) + ", base:" + repr(base_number))
        return result

    def check_if_pre_cfg_change(self):
        """
        Only compare copy FPGA number and FPGA FEP version.
        :return: check_result, False: Continue scripts. True: Do not need to go ahead
        """
        type_list = self.cfg_fpga_enb_mapping.keys()
        check_result = True
        # if not self.calculate_copied_number():
        #    log("ERROR: Copied FPGA files more than based ENB load, raise a exception.")
        #    raise ExceptNotMatch("ERROR: Copied FPGA files more than based ENB load.")

        try:
            for fpga_type in type_list:
                log("INFO: Checking for " + fpga_type)
                current_copy_info_list = self.cfg_fpga_enb_mapping.get(fpga_type)
                base_copy_info_list = self.cfg_fpga_enb_mapping_base.get(fpga_type)
                if len(current_copy_info_list) == 0 and len(base_copy_info_list) == 0:
                    log("INFO: The FPGA do not copy in both current enb load or base enb load, continue.")
                    check_result = False
                    continue
                elif len(current_copy_info_list) == 0 and len(base_copy_info_list) > 0:
                    log("INFO: Remove one FPGA copy in current enb load.")
                    log("INFO: No matter, just do not check it.")
                    # self.changed_list.append(fpga_type)
                    # check_result = False
                    continue
                elif len(current_copy_info_list) > 0 and len(base_copy_info_list) == 0:
                    log("ERROR: Add new FPGA item in pre-release cfg file : " + fpga_type)
                    self.changed_list.append(fpga_type)
                    self.error_dict[fpga_type] = "Add-new-item"
                    raise ExceptNotMatch("ERROR: Add " + fpga_type + " baseline in pre-release cfg file.")
                else:
                    pass
                curr_fep_name = current_copy_info_list[0]
                base_fep_name = base_copy_info_list[0]
                if not curr_fep_name == base_fep_name:
                    log("INFO: The FPGA changes.")
                    if fpga_type not in self.changed_list:
                        self.changed_list.append(fpga_type)
                        check_result = False
        except Exception as e:
            raise e
        else:
            log("INFO: Check if the pre-release cfg file change, result = " + repr(check_result))
            log("INFO: Changed list : " + repr(self.changed_list))
            return check_result

    def lfs_baseline_in_enb(self, enb_baseline):
        try:
            enb_content_file = self.get_build_content_from_wft(enb_baseline)
        except Exception as e:
            raise e

        if not os.path.exists(enb_content_file):
            raise Exception("Error: No enb baseline in workspace.")
        try:
            result_list = self.parse_xml2(enb_content_file, "content", "baseline", "LRC_LCP_PS_LFS_OS")
            lfs_baseline = result_list[0]
            if lfs_baseline == "":
                raise Exception("Error: Can not parse LFS baseline in enb load content xml.")
        except Exception as e:
            raise e
        else:
            log("INFO: Get lfs baseline from enb baseline end, result = " + lfs_baseline)
            return lfs_baseline

    @staticmethod
    def change_type_to_list(fpga_type):
        """
        Return according FPGA baseline name from FPGA type.
        :param fpga_type: LCA LBR LNI
        :return: PS_LFS_FW_AGUSTA and so on.
        """
        global FPGA_MAPPING_DICT
        result_list = []
        for key, value_v in FPGA_MAPPING_DICT.viewitems():
            if value_v == fpga_type:
                result_list.append(key)
        return result_list

    def get_changed_fpga_baseline(self):
        global FPGA_MAPPING_DICT
        log("INFO: Start to get changed FPGA baseline in branch...")
        for fpga_type in self.changed_list:
            log("INFO: Get changed FPGA baseline for " + fpga_type)
            name_enb_info = self.cfg_fpga_enb_mapping.get(fpga_type)
            enb_name = name_enb_info[1]
            log("INFO: Checking " + fpga_type + ", in " + enb_name)
            lfs_os = self.lfs_baseline_in_enb(enb_name)
            try:
                lfs_build_content = self.get_build_content_from_wft(lfs_os)
                baseline_list = self.parse_xml2(lfs_build_content, 'content', 'baseline')
                if len(baseline_list) == 0:
                    raise Exception("ERROR: baseline_list from LFS could not be got.")
                for baseline_name in baseline_list:
                    type_list = self.change_type_to_list(fpga_type)
                    for type_v in type_list:
                        if baseline_name.find(type_v) != -1:
                            self.base_fpga_v_dict[type_v] = baseline_name
            except Exception as e:
                raise e
            else:
                log("INFO: End fpga baselines.")
        log("INFO: Finished to get changed FPGA baseline in branch...")
        log(repr(self.base_fpga_v_dict))
        log(repr(self.fpga_v_dict))

    def check_fpga_baseline(self):
        global FPGA_MAPPING_DICT
        """
        The function is used to check if the FPGA baselines in branch are the same as they are in current
        building
        :return: None
        """
        baseline_type_list = self.base_fpga_v_dict.keys()
        for baseline_type in baseline_type_list:
            curr_baseline = self.fpga_v_dict.get(baseline_type)
            base_baseline = self.base_fpga_v_dict.get(baseline_type)
            log("INFO: Checking for " + baseline_type + "baseline: " + curr_baseline + ", base:" + base_baseline)
            if base_baseline == "":
                log("INFO: The FPGA does not need to check for " + baseline_type)
                continue
            if not base_baseline == curr_baseline:
                fpga_type = FPGA_MAPPING_DICT.get(baseline_type)
                self.error_dict[fpga_type] = "NOT_MATCH_ERROR"
        log("INFO: End checking fpga baseline, result = " + repr(self.error_dict))
        if len(self.error_dict) > 0:
            raise ExceptNotMatch("ERROR: There is not match exception.")

    def start_check_cfg(self):
        """
        The enter function to check PRE_RELEASE_CFG file correctness.
        :return:
        """
        global EMAIL_TYPE_FAIL_FURTHER
        log("INFO: Start to checking if the pre-release cfg file is correct.")
        try:
            cfg_file = self.get_pre_cfg_file(self.branch)
            self.get_fpga_enbname_mapping(cfg_file, "NOT base")
            copy_info_file = self.get_base_enb_copyinfo_file()
            self.get_fpga_enbname_mapping(copy_info_file, "base")
            is_not_changed = self.check_if_pre_cfg_change()
            if is_not_changed:
                log("INFO: Copied FPGA files in PRE_CFG does not change. Return directly.")
                return
            self.get_changed_fpga_baseline()
            self.check_fpga_baseline()
        except ExceptNotMatch:
            log("ERROR: There is not match exception, send the notification email.")
            file_name = generate_error_file()
            write_result("-----------CheckPreConfigFile-------------", file_name)
            for fpga_type in self.changed_list:
                if fpga_type in self.error_dict.keys():
                    write_result(fpga_type + ":" + self.error_dict.get(fpga_type), file_name)
                else:
                    write_result(fpga_type + ":MATCH", file_name)
            mail(EMAIL_TYPE_FAIL_FURTHER, "")
            sys.exit(1)
        except:
            log(traceback.format_exc())
            file_name = generate_error_file()
            write_result("-----------CheckPreConfigFile-------------", file_name)
            write_result("Exception is UNKNOWN", file_name)
            mail(EMAIL_TYPE_FAIL_FURTHER, "")
            sys.exit(1)
        else:
            log("INFO: Checking end. The result is OK.")


class GetBranchBuild(BaseClass):
    """
    This class is used for searching the branch build that use the same FPGA as trunk.
    """
    def __init__(self, base_branch, enb_version, lni_v, lca_v, lbr_v):
        self.base_branch = base_branch
        self.lfs_version = ""
        self.base_lfs_version = ""
        self.enb_baseline = enb_version
        self.base_enb_baseline = ""
        self.CURRENT_FPGA_VER = {"PS_LFS_FW_AGUSTA": "", "PS_LFS_FW_TRIUMPH": "", "PS_LFS_FW_HARLEY": "",
                                 "PS_LFS_FW_SIDECAR": ""}
        self.BASE_FPGA_VER = {"PS_LFS_FW_AGUSTA": "", "PS_LFS_FW_TRIUMPH": "", "PS_LFS_FW_HARLEY": "",
                              "PS_LFS_FW_SIDECAR": ""}
        self.CHANGED_FPGA = []
        self.is_ignore_no_branch = False
        self.checked_lca_name = lca_v
        self.checked_lbr_name = lbr_v
        self.checked_lni_name = lni_v
        self.no_need_handle = False
        # fail_dict is to record the failed FPGA and reason
        self.fail_dict = {}

    def get_lfs_v(self):
        return self.lfs_version

    def get_current_fpga_v(self):
        return self.CURRENT_FPGA_VER

    def find_changed_fpga(self):
        """
        Find the changed FPGA version, if no change, do not need to check.
        If there is change, need to find the used FEP file in based branch.
        :return:
        """
        log("INFO: Start to get changed FPGA.")
        for fpga_type in self.CURRENT_FPGA_VER.keys():
            current_version = self.CURRENT_FPGA_VER.get(fpga_type)
            base_version = self.BASE_FPGA_VER.get(fpga_type)
            if not current_version == base_version:
                log("INFO: current fpga version is not equal to the base one.")
                self.CHANGED_FPGA.append(fpga_type)
        log("INFO: Finish finding changed FPGA: " + repr(self.CHANGED_FPGA))

    def get_fpga_baseline(self):
        """
        Get the FPGA baselines for current ENB load and base ENB load.
        :return: No
        """
        try:
            self.fpga_baseline_from_lfs(self.lfs_version, 'current')
            self.fpga_baseline_from_lfs(self.base_lfs_version, 'base')
        except Exception as e:
            log(traceback.format_exc())
            raise e

    def fpga_baseline_from_lfs(self, lfs_baseline, get_type):
        log("Info: Get fpga baselines start.")
        try:
            lfs_build_content = self.get_build_content_from_wft(lfs_baseline)
            baseline_list = self.parse_xml2(lfs_build_content, 'content', 'baseline')
            if len(baseline_list) == 0:
                raise Exception("ERROR: baseline_list from LFS could not be got.")
            for baseline_name in baseline_list:
                for fpge_type in self.CURRENT_FPGA_VER.keys():
                    if baseline_name.find(fpge_type) != -1 and get_type == "current":
                        self.CURRENT_FPGA_VER[fpge_type] = baseline_name
                    elif baseline_name.find(fpge_type) != -1 and get_type == "base":
                        self.BASE_FPGA_VER[fpge_type] = baseline_name
        except urllib2.HTTPError as e:
            raise e
        except IOError as e:
            raise e
        except Exception as e:
            log(traceback.format_exc())
            raise e
        log("INFO: Finish get FPGA baselines. FPGA_VER = ")
        log(repr(self.CURRENT_FPGA_VER))
        log(repr(self.BASE_FPGA_VER))

    def set_failed_value(self, fpga_type, error_value):
        """
        The function is used to record error value. The error values are used for handle in next step.
        :param fpga_type:
        :param error_value: Exception class instance.
        :return:
        """
        if fpga_type not in self.fail_dict.keys():
            self.fail_dict[fpga_type] = error_value

    def get_branch_build_name(self, fpga_baseline):
        log("Info: Begin to get branch ENB load name for " + fpga_baseline)
        try:
            lfs_os_baseline_list = self.get_assignment_lfs_os(fpga_baseline)
        except Exception as e:
            raise e

        branch_enb_list = []
        try:
            for lfs_os_baseline in lfs_os_baseline_list:
                log("INFO: get use ENB baseline for lfs_os: " + lfs_os_baseline)
                # lfs_rel_baseline = self.transfer_os_to_rel(lfs_os_baseline)
                baseline_xml_file = self.get_build_content_from_wft(lfs_os_baseline)
                regex_enb = BRANCH_ENB_DICT.get(self.base_branch)
                assign_branch_enb_build_list = self.get_enb_build_list_from_lfs_xml(baseline_xml_file,
                                                                                    'assignments', 'used_in',
                                                                                    'branch', 'build', regex_enb)
                if len(assign_branch_enb_build_list) == 0:
                    log("INFO: LFS baseline:" + lfs_os_baseline + " is not used in branch " + self.base_branch)
                    continue
                else:
                    for build_name in assign_branch_enb_build_list:
                        if build_name not in branch_enb_list:
                            branch_enb_list.append(build_name)
            branch_enb_list = sorted(assign_branch_enb_build_list)
            list_number = len(branch_enb_list)
            if list_number == 0:
                raise ExceptNotFind("ERROR: No branch ENB load uses " + fpga_baseline + ".")
            latest_build = branch_enb_list[list_number - 1]
        except Exception as e:
            log(traceback.format_exc())
            raise e
        return latest_build

    def get_branch_build_name_list(self, fpga_baseline):
        log("Info: start to get branch build for " + fpga_baseline)
        try:
            lfs_os_baseline_list = self.get_assignment_lfs_os(fpga_baseline)
        except Exception as e:
            raise e

        branch_enb_list = []
        try:
            for lfs_os_baseline in lfs_os_baseline_list:
                log("INFO: get use ENB baseline for lfs_os: " + lfs_os_baseline)
                baseline_xml_file = self.get_build_content_from_wft(lfs_os_baseline)
                regex_enb = BRANCH_ENB_DICT.get(self.base_branch)
                assign_branch_enb_build_list = self.get_enb_build_list_from_lfs_xml(baseline_xml_file,
                                                                                    'assignments', 'used_in',
                                                                                    'branch', 'build', regex_enb)
                if len(assign_branch_enb_build_list) == 0:
                    log("WARN: LFS baseline:" + lfs_os_baseline + " is not used in branch " + self.base_branch)
                    continue
                else:
                    for build_name in assign_branch_enb_build_list:
                        if build_name not in branch_enb_list:
                            branch_enb_list.append(build_name)
            if len(branch_enb_list) == 0:
                log("Error: The LBR baseline " + fpga_baseline + " is not used in any branch ENB build.")
                raise ExceptNotFind("Error: Could not find branch ENB load via " + fpga_baseline)
            result_branch_enb_list = set(branch_enb_list)
            result_branch_enb_list = sorted(result_branch_enb_list)[::-1]
            log("Info: LBR baseline " + fpga_baseline + " get branch_build_name_list end")
            log("Info: list = " + repr(result_branch_enb_list))
        except Exception as e:
            log(traceback.format_exc())
            raise e
        return result_branch_enb_list

    def get_assignment_lfs_os(self, fpga_baseline):
        """
        Get the fpga baseline assignment that used in branch build.
        :param fpga_baseline:
        :return: The LFS baselines that use the fpga in base branch.
        """
        global BRANCH_LFS_NAME_MAPPING_DICT
        log("INFO: Begin to get assignment used lfs os for " + fpga_baseline)
        try:
            build_content = self.get_build_content_from_wft(fpga_baseline)
            used_baseline_list = self.get_list_from_xml2(build_content, 'used_in', 'baseline')
            branch_used_baseline_list = []
            regex_string = BRANCH_LFS_NAME_MAPPING_DICT.get(self.base_branch)
            if regex_string == "":
                raise ValueError("ERROR: No the regex of LCP LFS for branch " + self.base_branch)
            for baseline in used_baseline_list:
                if baseline.find(regex_string) != -1:
                    branch_used_baseline_list.append(baseline)
            list_number = len(branch_used_baseline_list)
            if list_number == 0:
                raise ExceptNotFind("ERROR: No branch LFS baseline used the FPGA version.")
            else:
                result_list = sorted(branch_used_baseline_list)[::-1]
        except urllib2.HTTPError as e:
            log("ERROR: It seems that there is problem to access WFT.")
            raise e
        except ValueError as e:
            raise e
        except ExceptNotFind as e:
            raise e
        except Exception:
            raise ExceptUnknown()
        else:
            log("INFO: End to get assignment used lfs os, result = " + repr(result_list))
            return result_list

    def lfs_baseline_in_enb(self, enb_baseline, is_the_base):
        """
        Get lfs for base enb load and current enb load.
        :param enb_baseline:
        :param is_the_base:
        :return:
        """
        try:
            enb_content_file = self.get_build_content_from_wft(enb_baseline)
        except Exception as e:
            raise e

        if not os.path.exists(enb_content_file):
            raise Exception("Error: No enb baseline in workspace.")

        try:
            result_list = self.parse_xml2(enb_content_file, "content", "baseline", "LRC_LCP_PS_LFS_OS")
            lfs_baseline = result_list[0]
            if lfs_baseline == "":
                raise Exception("Error: Can not parse LFS baseline in enb load content xml.")
        except Exception as e:
            raise e
        if is_the_base:
            self.base_lfs_version = lfs_baseline
        else:
            self.lfs_version = lfs_baseline
        log("INFO: Get lfs baseline from enb baseline end, result = " + self.lfs_version)

    def check_base_branch_available(self):
        """
        The function is used to check if the branch param is available. Only follow branch are supported.
        16B 17A
        :param branch:
        :return:
        """
        global BRANCH_LFS_NAME_MAPPING_DICT
        if self.base_branch not in BRANCH_LFS_NAME_MAPPING_DICT.keys():
            raise ValueError("ERROR: The branch " + self.base_branch + " does not support to find.")

    def get_based_enb_baseline(self, baseline):
        baseline_xml = baseline + ".xml"
        try:
            if not os.path.exists(baseline_xml):
                self.get_build_content_from_wft(baseline)

            xml_tree = cElementTree.parse(baseline_xml)
            root = xml_tree.getroot()
            base_enb = root.find("diff")
            enb_load = base_enb.get("to")
            self.base_enb_baseline = enb_load
        except Exception as e:
            log(traceback.format_exc())
            raise e
        else:
            log("INFO: End get based enb load, result = " + self.base_enb_baseline)
            return

    def pre_start(self):
        """
        prepare env for finding, such as , lfs baseline, lfs baseline in base enb load, FPGA version in
        current enb baseline and in base enb baseline.
        :return:
        """
        global EMAIL_TYPE_FAIL
        log("Info: prepare start......")
        try:
            self.check_base_branch_available()
            self.get_based_enb_baseline(self.enb_baseline)
            if self.base_enb_baseline == "":
                log("INFO: Base ENB baseline is None. No need to finding.")
                self.no_need_handle = True
                return
            self.lfs_baseline_in_enb(self.enb_baseline, False)
            self.lfs_baseline_in_enb(self.base_enb_baseline, True)
            if self.base_lfs_version == self.lfs_version:
                log("INFO: LFS version does not change. No need to finding.")
                self.no_need_handle = True
                return
            self.get_fpga_baseline()
            self.find_changed_fpga()
            if len(self.CHANGED_FPGA) == 0:
                log("INFO: LFS version change, but no FPGA change. No need to finding.")
                self.no_need_handle = True
                return
        except:
            log("ERROR: prepare start error, " + traceback.format_exc())
            file_n = generate_error_file()
            exception_str = "Prepare env: UNKNOWN EXCEPTION."
            write_result(exception_str, file_n)
            mail(EMAIL_TYPE_FAIL, self.lfs_version)
            sys.exit(1)

    @staticmethod
    def check_file_name_match(branch_enb_load, checked_file_name, file_regex):
        """
        Check if the found FPGA file name in branch matches it is in current load.
        :param branch_enb_load: The found ENB load in base branch.
        :param checked_file_name: Current file name
        :param file_regex: FPGA type
        :return: None
        """
        storage_path = "/lteRel/build/"
        branch_enb_path = storage_path + branch_enb_load
        branch_file_name = get_files(branch_enb_path, file_regex)
        if branch_file_name is None or len(branch_file_name) != 1:
            raise ExceptNotMatch("ERROR: Not match for " + file_regex + ".")
        file_name = branch_file_name[0]
        log("INFO: file name == " + file_name + ": Checked file name == " + checked_file_name)
        if file_name == checked_file_name:
            log("INFO: Check success for " + file_regex + ".")
        else:
            raise ExceptNotMatch("ERROR: Not match for " + file_regex + ".")

    def get_checked_file(self, fep_type):
        global FPGA_LIST
        if fep_type == FPGA_LIST[0]:
            return self.checked_lca_name
        elif fep_type == FPGA_LIST[1]:
            return self.checked_lni_name
        elif fep_type == FPGA_LIST[2]:
            return self.checked_lbr_name
        else:
            raise ValueError("ERROR: Not the checked type: " + fep_type)

    def handle_lni_lca(self, fpga_type):
        """
        Finding LNI and LCA FPGA FEP file in branch. If the input for LNI or LCA is NULL. It means that
        No need to find for it, return directly.
        :param fpga_type: ("PS_LFS_FW_AGUSTA", "PS_LFS_FW_TRIUMPH")
        :return: None
        """
        global FPGA_MAPPING_DICT
        global FPGA_LIST
        fep_type = FPGA_MAPPING_DICT.get(fpga_type)
        log("INFO: Start handle LNI or LCA, type = " + fpga_type)
        if fep_type == FPGA_LIST[0] and self.checked_lca_name == "":
            log("INFO: The checked LCA file is not exist. Return directly.")
            return
        if fep_type == FPGA_LIST[1] and self.checked_lni_name == "":
            log("INFO: The checked LNI file is not exist. Return directly.")
            return
        try:
            branch_enb_build = self.get_branch_build_name(self.CURRENT_FPGA_VER.get(fpga_type))
            checked_file_name = self.get_checked_file(fep_type)
            self.check_file_name_match(branch_enb_build, checked_file_name, fep_type)
            # write_result(fep_type + ":" + enb_build)
        except Exception as e:
            self.set_failed_value(fep_type, e)
            raise e

    def handle_lbr(self):
        global FPGA_MAPPING_DICT
        lbr_enb_load = ""
        if self.checked_lbr_name == "":
            log("INFO: The checked LBR file is not exist. Return directly.")
            return
        harley_ver = self.CURRENT_FPGA_VER.get("PS_LFS_FW_HARLEY")
        sidecar_ver = self.CURRENT_FPGA_VER.get("PS_LFS_FW_SIDECAR")
        try:
            harley_enb_list = self.get_branch_build_name_list(harley_ver)
            sidecar_enb_list = self.get_branch_build_name_list(sidecar_ver)

            for build in harley_enb_list:
                if build in sidecar_enb_list:
                    log("INFO: There is the same ENB load for harley and sidecar. So it is the NEB load.")
                    lbr_enb_load = build
                    break
            if lbr_enb_load == "":
                raise ExceptNotFind("ERROR: No same ENB load for harley and sidecar.")

            fep_type = FPGA_MAPPING_DICT.get("PS_LFS_FW_SIDECAR")
            checked_file_name = self.get_checked_file(fep_type)
            self.check_file_name_match(lbr_enb_load, checked_file_name, fep_type)
            # write_result(fep_type + ":" + lbr_enb_load)
        except Exception as e:
            self.set_failed_value("LBR", e)
            raise e

    def exit_error_with(self, code):
        log("INFO: handle error end.")
        generate_error_file()
        mail(EMAIL_TYPE_FAIL, self.lfs_version)
        sys.exit(code)

    def start_check_branch(self):
        """
        The function is the main function to check:
        When the LCP LFS FPGA baseline change, if the copy information in pre-release CFG file is correct.
        :return:
        """
        is_lbr_handled = False
        if len(self.CHANGED_FPGA) == 0:
            log("INFO: There is no FPGA baseline changes, please check...")
            return

        for fpga_type in self.CHANGED_FPGA:
            # for LNI and LCA
            if fpga_type == "PS_LFS_FW_AGUSTA" or fpga_type == "PS_LFS_FW_TRIUMPH":
                try:
                    self.handle_lni_lca(fpga_type)
                except:
                    log("ERROR: Handle fpga: " + fpga_type + " error.")
                    continue
            # for LBR
            else:
                if is_lbr_handled:
                    log("INFO: LBR has been handled once, so continue.")
                    continue
                try:
                    self.handle_lbr()
                except:
                    log("ERROR: Handle LRC FPGA error: " + fpga_type)
                    pass
                is_lbr_handled = True

        if len(self.fail_dict) > 0:
            self.handle_error()
        else:
            log("INFO: No exception when finding branch ENB load.")
            return

    def handle_error(self):
        """
        Handle the result in finding process.
        Exception will send out email to notify SCM to check.
        No exception will not send out notify email, and scripts go ahead.
        :return:
        """
        log("INFO: Begin to handle error in process.")
        global FPGA_LIST
        global EMAIL_TYPE_FAIL

        if len(self.fail_dict) == 0:
            log("INFO: No error, return directly.")
            return

        file_name = generate_error_file()
        for key, key_value in self.fail_dict.iteritems():
            log("INFO: Handle error for: " + key)
            # write_result(key + ":", file_name)
            if isinstance(key_value, ExceptNotFind):
                exception_str = key + ": NOT FIND EXCEPTION."
            elif isinstance(key_value, ExceptNotMatch):
                exception_str = key + ": NOT MATCH EXCEPTION."
            else:
                exception_str = key + ": UNKNOWN EXCEPTION."
            write_result(exception_str, file_name)
        # mail(EMAIL_TYPE_FAIL, self.lfs_version)
        self.exit_error_with(1)

    def test(self):
        current_lfs_baseline = "LRC_LCP_PS_LFS_OS_2016_09_0038"
        base_lfs_baseline = "LRC_LCP_PS_LFS_OS_2016_09_0037"
        self.get_fpga_baseline_from_lfs(current_lfs_baseline, 'current')
        self.get_fpga_baseline_from_lfs(base_lfs_baseline, 'base')
        self.find_changed_fpga()
        self.start()


def template_failed():
    template_string = '''
        <html>
            <body>
            <div>Hello SCM,</div>
            <div>
            <p><b>There is new LCP LFS: $current_lfs_version. FPGA changes.</b><p>
            <p>But check the FPGA FEP failed with branch FPGA FEP.</p>
            <code>$attach_file</code>
            <p>Please have a look....</p>
            </body>
        </html>
        '''
    return template_string


def template_failed_further():
    template_string = '''
        <html>
            <body>
            <div>Hello SCM,</div>
            <div>
            <p><b>There is FPGA copy information change in pre-cfg file.</b><p>
            <p>But check the FPGA baseline from pre-cfg file to current load use FPGA baseline. Failed.</p>
            <code>$attach_file</code>
            <p>Please have a look....</p>
            </body>
        </html>
        '''
    return template_string


def get_email_dict_data(type_t, param1="", param2=""):
    my_dict = {}
    if type_t == EMAIL_TYPE_FAIL:
        my_dict["current_lfs_version"] = param1
        my_dict["attach_file"] = param2
    elif type_t == EMAIL_TYPE_FAIL_FURTHER:
        my_dict["current_lfs_version"] = param1
        my_dict["attach_file"] = param2
    else:
        log("WARN: email parameter error. Return null dict.")
    return my_dict


def generate_error_file():
    if not os.path.exists(RESULT_FAIL_FILE_NAME):
        ge_command = "touch " + RESULT_FAIL_FILE_NAME
        os.system(ge_command)
    return RESULT_FAIL_FILE_NAME


def mail(template_name, current_lfs_version):
    """
        mail function to send email when LCP LFS OS changes. There are 3 cases:
        1 FPGA changes, and find one branch baseline. Take care to copy the files.
        2 FPGA changes, and there is no the branch baseline. It is an error.
        3 FPGA changes, there are some error when finding
    """
    sender_ad = 'xuping.xu@nokia.com'
    to = 'xuping.xu@nokia.com; jb.xu@nokia.com; jie.wang@nokia.com'

    if not TO == "":
        to = TO
    # to = 'xuping.xu@nokia.com'
    server = 'mail.emea.nsn-intra.net'

    if template_name == EMAIL_TYPE_FAIL:
        template = template_failed()
        attached_file = RESULT_FAIL_FILE_NAME
        attached_file_list = list()
        attached_file_list.append(attached_file)
        subject = "Warning: Finding branch FPGA FEP failed."
    elif template_name == EMAIL_TYPE_FAIL_FURTHER:
        template = template_failed_further()
        attached_file = RESULT_FAIL_FILE_NAME
        attached_file_list = list()
        attached_file_list.append(attached_file)
        subject = "Warning: Checking pre-cfg FPGA baseline failed."
    else:
        log("INFO: Do nothing.")
        return

    mail_data = get_email_dict_data(template_name, current_lfs_version, RESULT_FAIL_FILE_NAME)

    TEMPLATE = string.Template(template)
    html_data = TEMPLATE.safe_substitute(mail_data)
    send(server, sender_ad, to, "[Branch FPGA Exception]" + subject, html_data, attached_file_list)


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
    $text_name have follow parameter for use. "-b" "-p" "-c" and "-v" are mandatory. There must be one of
    -l -a and -r.
    -b: based branch, e.g., 16B, 16Ba. Required.
    -c: current branch, e.g., 17A. Required.
    -v: current using ENB baseline, e.g., DNH5.0_ENB_1611_100_01. Required.
    -l: checked LNI FEP name.
    -a: checked LCA FEP name.
    -r: checked LBR FEP name.
    -m: The send email list.
    """
    usage_s = string.Template(usage_text)
    param = {"text_name": file_name}
    print usage_s.safe_substitute(param)


def get_fpga_type_from_baseline(baseline):
    for fpga_type in FPGA_MAPPING_DICT.keys():
        if baseline.find(fpga_type) != -1:
            return FPGA_MAPPING_DICT.get(fpga_type)


def clean_workspace():
    os.system("rm -rf " + WORK_SPACE_NAME)


def copy_command(file_name, directory):
    cp_command = "cp " + file_name + " " + directory
    os.system(cp_command)


def get_files(root, patterns='*', single_level=False, yield_folders=False):
    patterns = patterns.split(';')
    fileList = []
    for path, subdirs, files in os.walk(root):
        if yield_folders:
            files.extend(subdirs)
        files.sort()
        for f_name in files:
            for pattern in patterns:
                patternGet = re.compile(pattern)
                if patternGet.match(f_name):
                    fileList.append(f_name)
        if single_level:
            break
    return fileList


def log(msg):
    with open('Get_branch_build.log', 'a') as log_file:
        print(msg)
        log_file.write(msg + '\n')


def write_result(msg, file_name):
    with open(file_name, 'a') as result_file:
        result_file.write(msg + '\n')


if __name__ == '__main__':
    current_load_baseline = ""
    BASE_ON_BRANCH = ""
    lni_name = ""
    lca_name = ""
    lbr_name = ""
    current_branch = ""
    if len(sys.argv) > 1:
        try:
            options, args = getopt.getopt(sys.argv[1:], "b:v:l:a:r:m:c:", ["based-branch", "enb-version",
                                                                           "LNI-FEP-name", "LCA-FEP-name",
                                                                           "LBR-FEP-name", "mail-list", "curr-branch"])
        except getopt.GetoptError:
            usage(sys.argv[0])
            sys.exit(1)
    else:
        usage(sys.argv[0])
        sys.exit(1)
    for name, value in options:
        if name in ("-b", "--based-branch"):
            BASE_ON_BRANCH = value
        elif name in ("-v", "--enb-version"):
            current_load_baseline = value
        elif name in ("-l", "--LNI-FEP-name"):
            lni_name = value
        elif name in ("-a", "--LCA-FEP-name"):
            lca_name = value
        elif name in ("-r", "--LBR-FEP-name"):
            lbr_name = value
        elif name in ("-m", "--mail-list"):
            TO = value
            log("INFO: To: " + TO)
        elif name in ("-c", "--curr-branch"):
            current_branch = value
        else:
            usage(sys.argv[0])
            sys.exit(1)

    if BASE_ON_BRANCH == "" or current_load_baseline == "" or (lni_name == "" and lca_name == "" and lbr_name == ""):
        usage(sys.argv[0])
        sys.exit(1)

    clean_workspace()
    os.system("mkdir " + WORK_SPACE_NAME)
    os.chdir(WORK_SPACE_NAME)

    finding = GetBranchBuild(BASE_ON_BRANCH, current_load_baseline, lni_name, lca_name, lbr_name)
    # finding.test()
    finding.pre_start()
    if not finding.no_need_handle:
        finding.start_check_branch()
    else:
        # sys.exit(0)
        pass

    log("-----------------------------------------------------------------------------------")

    dict_list = finding.get_current_fpga_v()
    if dict_list is None or len(dict_list) == 0:
        log("ERROR: dict_list is None")
        sys.exit(1)
    checking = CheckPreConfigFile(current_branch, current_load_baseline, dict_list)
    checking.start_check_cfg()

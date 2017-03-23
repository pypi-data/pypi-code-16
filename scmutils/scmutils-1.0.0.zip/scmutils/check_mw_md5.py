#!/build/ltesdkroot/Tools/Tools/python/python-2.7.2/bin/python

import getopt
import string
import sys
import re
import os
import traceback
import urllib2
import xml.etree.cElementTree as cElementTree


WORK_SPACE_NAME = "check_mw_md5"
BASE_PRE_DIRECTORY = "/lteRel/build/"
SVN_REPO_60 = "https://beisop60.china.nsn-net.net"
SVN_REPO_e1 = "https://svne1.access.nsn.com"
USED_SVN_SERVER = ""


class MWMD5(object):
    """
    This class is used for get base on CD load FEP file name and md5sum
    """
    MW_TYPE_LIST = ['PNS_MW_LTEOAM', 'PNS_MW_3G_CP', 'PNS_MW_3G_SV', 'PNS_MW_LCP', 'PNS_MW_LSP', 'PNS_MW_LTECP', \
                    'PNS_MW_FAP_configuration', 'PNS_MW_OAMCMN_configuration']
    WFT_SERVER_BUILD_CONTENT = "https://wft.inside.nsn.com/ext/build_content"
    WFT_SERVER_RELEASE_NOTES = "https://wft.inside.nsn.com/ext/releasenote"
    ENB_CONTENT_FILE_NAME = "enb_build_content.xml"

    def __init__(self, build_baseline):
        self.mw_baseline_dict = {}
        self.mw_md5_from_rn = {}
        self.mw_md5_workspace = {}
        self.baseline = build_baseline

    @staticmethod
    def download_baseline_content(build_baseline, target_file, dtype="content"):
        if build_baseline == "" or build_baseline is None:
            raise ValueError
        enb_content_path = MWMD5.WFT_SERVER_BUILD_CONTENT + "/" + build_baseline
        if dtype == "rn":
            enb_content_path = MWMD5.WFT_SERVER_RELEASE_NOTES + "/" + build_baseline + ".xml"
        log("INFO: Download file for " + enb_content_path + ".")
        try:
            req = urllib2.Request(enb_content_path)
            response = urllib2.urlopen(req)
            the_page = response.read()
            file_handle = open(target_file, "w")
            file_handle.write(the_page)
        except urllib2.HTTPError as e:
            log("Error: Could not get xml from WFT. Baseline = " + build_baseline)
            raise e
        except IOError as e:
            log("Error: Write xml to a file error.")
            raise e
        except Exception as e:
            log(traceback.format_exc())
            raise e
        else:
            file_handle.close()

    @staticmethod
    def parse_xml2(xml_file, content, element, regex=''):
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
                    if not regex == '':
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
    def parse_xml3(xml_file, content, element, items):
        result = {}
        if not os.path.exists(xml_file):
            log("Warn: can not parse the xml file " + xml_file + ", as it does no exist.")
            return result
        try:
            xml_tree = cElementTree.parse(xml_file)
            root = xml_tree.getroot()
            for content_content in root.findall(content):
                for element_content in content_content.findall(element):
                    map_list = []
                    for item in items:
                        item_content = element_content.find(item)
                        item_content_name = item_content.text
                        map_list.append(item_content_name)
                    if len(map_list) != 2:
                        log("ERROR: Get MW file mad5sum, but the file name and md5sum are not match.")
                        raise ValueError
                    result[map_list[0]] = map_list[1]
        except cElementTree.ParseError as e:
            log(traceback.format_exc())
            raise e
        except Exception as e:
            log(traceback.format_exc())
            raise e
        else:
            log("INFO: parse_xml3 for " + xml_file + ", the result == " + repr(result))
            return result

    def get_mw_baselines_from_content(self, build_baseline):
        log("INFO: Start to get MW baseline from ENB content")

        def add_dict(key, input_value):
            if key not in self.mw_baseline_dict.keys():
                self.mw_baseline_dict[key] = input_value
            else:
                log("ERROR: There is multi MW type. Please check.")
                sys.exit(1)
        if not os.path.exists(self.ENB_CONTENT_FILE_NAME):
            try:
                log("INFO: Try to download ENB content from WFT.")
                self.download_baseline_content(build_baseline, self.ENB_CONTENT_FILE_NAME, "content")
            except urllib2.HTTPError as e:
                raise e
            except Exception as e:
                raise e
        log("INFO: begin to get MW baseline from " + self.ENB_CONTENT_FILE_NAME + ".")
        try:
            for mw_type in self.MW_TYPE_LIST:
                result_list = self.parse_xml2(self.ENB_CONTENT_FILE_NAME, "content", "baseline", mw_type)
                if result_list is None or result_list[0] == "":
                    log("ERROR: Get MW baseline for " + mw_type + " error. Result is None.")
                    raise ValueError
                add_dict(mw_type, result_list[0])
        except cElementTree.ParseError as e:
            log(traceback.format_exc())
            raise e
        except ValueError as e:
            log(traceback.format_exc())
            raise e
        else:
            log("INFO: Get MW baseline end.")
            log(repr(self.mw_baseline_dict))

    def mw_file_md5sum_from_rn(self):
        mw_baseline_list = self.mw_baseline_dict.values()
        if len(mw_baseline_list) == 0:
            log("ERROR: The MW baseline are not correct.")
            raise ValueError
        for mw_baseline in mw_baseline_list:
            log("INFO: Begin to download " + mw_baseline + " release notes.")
            release_notes_file_name = mw_baseline + ".xml"
            if not os.path.exists(release_notes_file_name):
                try:
                    self.download_baseline_content(mw_baseline, release_notes_file_name, "rn")
                except urllib2.HTTPError:
                    log("WARN: There is http error to download " + release_notes_file_name + ", try again.")
                    try:
                        self.download_baseline_content(mw_baseline, release_notes_file_name, "rn")
                    except Exception as e:
                        log("ERROR: Download release notes error. Exit scripts.")
                        raise e
                except Exception as e:
                    log("ERROR: Download release notes error. Exit scripts.")
                    raise e
            try:
                md5_map = self.parse_xml3(release_notes_file_name, "additional", "element", ["file", "md5sum"])
            except Exception as e:
                log(traceback.format_exc())
                raise e
            if len(md5_map) == 0:
                log("ERROR: Get md5 and file name error for " + mw_baseline + ".")
                raise ValueError
            else:
                self.mw_md5_from_rn.update(md5_map)
        log("INFO: get mw file md5 from release notes end, reslt = " + repr(self.mw_md5_from_rn))

    def get_mw_md5sum_from_workspace(self, file_name):
        global BASE_PRE_DIRECTORY
        log("INFO: get md5sum for " + file_name)
        md5sum_regex = "^\w+\s\s/lteRel/build/.+"
        import subprocess
        file_path = BASE_PRE_DIRECTORY + self.baseline + "/" + file_name
        if not os.path.exists(file_path):
            log("ERROR: file for md5 does not exist in workspace, " + file_path)
            raise IOError("File does not exist.")
        try:
            p = subprocess.Popen('md5sum ' + file_path, shell=True, stdout=subprocess.PIPE)
            result_str = p.stdout.read()
            if not re.match(md5sum_regex, result_str):
                log("ERROR: Get md5sum return error: " + result_str)
            md5sum = result_str.split()[0]
        except subprocess.CalledProcessError as e:
            log(traceback.format_exc())
            raise e
        except IOError as e:
            log(traceback.format_exc())
            raise e
        else:
            log("INFO: md5sum for file from workspace: " + file_name + " == " + md5sum)
            return md5sum

    def compare_md5sum(self):
        file_name_list = self.mw_md5_from_rn.keys()
        if len(file_name_list) < 8:
            log("ERROR: MW file number is not correct.")
            raise ValueError
        unmatched_file_name = []
        for file_name in file_name_list:
            file_md5_workspace = self.get_mw_md5sum_from_workspace(file_name)
            file_md5_from_rn = self.mw_md5_from_rn.get(file_name)
            if not file_md5_workspace == file_md5_from_rn:
                unmatched_file_name.append(file_name)
            else:
                log("INFO: MW: " + file_name + " md5sum are the same. It is OK.")
        if len(unmatched_file_name) > 0:
            log("ERROR: md5sum do not match::: " + repr(unmatched_file_name))
            # raise ValueError("ERROR: There are mw files that md5sum not match to release notes.")
            raise ValueError("There is some MW md5sum in workspace is not the same as release notes")

    def compare(self):
        log("INFO: Start to compare.")
        try:
            self.get_mw_baselines_from_content(self.baseline)
            self.mw_file_md5sum_from_rn()
            self.compare_md5sum()
        except Exception:
            log(traceback.format_exc())
            sys.exit(1)


def usage(file_name):
    usage_text = """
    $text_name have follow parameter for use. "-b" are mandatory. The scripts shoud be used after
     copy_mw in ENB building.
    -b: base CD build baseline name, e.g., DNH5.0_ENB_1611_100_01
    -s: SVN server, b60 or e1
    """
    usage_s = string.Template(usage_text)
    param = {"text_name": file_name}
    print usage_s.safe_substitute(param)


def clean_workspace():
    os.system("rm -rf " + WORK_SPACE_NAME)
    os.system("mkdir " + WORK_SPACE_NAME)
    os.chdir(WORK_SPACE_NAME)


def log(msg):
    with open('check_cd_content.log', 'a') as log_file:
        print(msg)
        log_file.write(msg + '\n')


if __name__ == '__main__':
    build_baseline = ''
    if len(sys.argv) > 1:
        try:
            options, args = getopt.getopt(sys.argv[1:], "b:s:", ["baseline=", "server="])
        except getopt.GetoptError:
            usage(sys.argv[0])
            sys.exit(1)
    else:
        usage(sys.argv[0])
        sys.exit(1)
    for name, value in options:
        if name in ("-b", "--baseline"):
            build_baseline = value
        if name in ("-s", "--server"):
            svn_server_name = value
            if svn_server_name == "e1":
                USED_SVN_SERVER = SVN_REPO_e1
            else:
                USED_SVN_SERVER = SVN_REPO_60

    if build_baseline == '':
        usage(sys.argv[0])
        sys.exit(1)

    clean_workspace()

    md5_handle = MWMD5(build_baseline)
    md5_handle.compare()

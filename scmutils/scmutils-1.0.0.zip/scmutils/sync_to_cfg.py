#!/build/ltesdkroot/Tools/Tools/python/python-2.7.2/bin/python

#######################################################################################################################
#    The tool is used for updating CFG files in SVN. The tool should be used after "knife_slave_server_disk.py" that        #
#    generates the file of "Finding_copy_result.txt"                                                                  #
#                                                                                                                     #
#    Date:26/10/2016                                                                                                  #
#    Author:                                                                                                          #
#    Input:                                                                                                           #
#       1. -f The directory of "Finding_copy_result.txt". E.g.,/build/home/xxp/branch_build/Finding_copy_result.txt   #
#       2. -b The branch CFG file name for updating.                                                                  #
#       3  -l: Update branch ENB load name.                                                                           #
#       4  -t: FEP name.                                                                                              #
#    -b is must required. -f or (-l and -t) should be used.                                                           #
#                                                                                                                     #
#    Output:                                                                                                          #
#       1. Update the CFG files according to branch.                                                                  #
#######################################################################################################################

import getopt
import string
import sys
import re
import os
import traceback


BRANCH_CFG_MAPPING_DICT = {"16A": "DNH3.0_CD_CFG", "16B": "DNH4.0_CFG", "17A": "DNH5.0_BASE_CFG"}
WORK_SPACE_NAME = "sync_to_cfg"
INPUT_FILE_NAME = "Finding_copy_result.txt"
FEP_TYPE_LIST = ["LCA", "LBR", "LNI", "LSP____3G_B", "LSP____OS_B", "LSP____F__B", "3GCP__HD", "3GSV__HD"]
SVN_CFG_REPO = "https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_LTE/builds/branches/lrc/LRCFEP_CFG"
BRANCH_ENB_DICT = {"16A": "DNH3.0_ENB", "16B": "DNH4.0_ENB", "17A": "DNH5.0_ENB"}
EMAIL_TYPE_FAIL = "failed"
BRANCH_BASE_DIR = "/lteRel/build/"
EMAIL_TYPE_SUCCESS = "success"
INPUT_MAPPING_DICT = {}
SVN_WORKSPACE = ""
TEMP_CFG_FILE_NAME = "temp_cfg_file"
IS_CFG_CHANGED = False
UPDATE_TYPE_FEP = "FEP"
UPDATE_TYPE_FPGA = "FPGA"


def get_all_files(root, file_type, single_level=False):
    # Expand patterns from semicolon-separated string to list
    log("Info: find required files begin. root = " + root + ",file_type = " + file_type)
    result_name = ""
    for path, subdirs, files in os.walk(root):
        files.sort()
        for file_name in files:
            if file_name.find(file_type) != -1:
                result_name = file_name
                break
        if single_level:
            break
    return result_name


def get_fep_name(fep_type, enb_load):
    enb_dir = BRANCH_BASE_DIR + enb_load
    result_file_name = ""
    if not os.path.exists(enb_dir):
        log("Error: ENB directory does not exist. dir = " + enb_dir)
        raise IOError("Directory does not exist.")
    result_file_name = get_all_files(enb_dir, fep_type, single_level=True)
    if result_file_name == "" or result_file_name is None:
        log("Error: The FEP file does not exist.")
        raise IOError("FEP file does not exist.")
    return result_file_name


def get_branch_baseline(input_file):
    if not os.path.exists(input_file):
        log("Error: Input file does not exist... " + input_file)
        raise IOError("File does not exist.")
    file_name = os.path.basename(input_file)
    regex = re.compile(r'^DNH\d+.0_ENB_\d{4}_\d{3}_\d{2}$')
    try:
        file_handle = open(input_file)
        for line_src in file_handle:
            line = line_src.strip()
            if line == "" or line is None:
                continue
            build = line.split(':')[1]
            fep_type = line.split(':')[0]
            if fep_type not in FEP_TYPE_LIST:
                log("Warn: The FEP type is incorrect in the input file: " + fep_type)
                # raise ValueError("FEP type is incorrect in the input file")
                continue
            match_handle = re.match(regex, build)
            if match_handle is None:
                log("Warn: There is error line in the input file: " + input_file)
                continue
            fep_name = get_fep_name(fep_type, build)
            INPUT_MAPPING_DICT[fep_name] = build
        if len(INPUT_MAPPING_DICT) == 0:
            log("Error: There is no available branch ENB baseline in input file.")
            raise ValueError("No available value from input file: " + input_file)
    except Exception, e:
        raise e
    log("Info: Finish get input, " + repr(INPUT_MAPPING_DICT))


def get_baseline_from_input(key_word):
    result_baseline = None
    result_fep = None
    for key_name in INPUT_MAPPING_DICT.keys():
        if key_name == "" or key_name is None:
            continue
        if key_name.find(key_word) != -1:
            result_baseline = INPUT_MAPPING_DICT.get(key_name)
            result_fep = key_name
    return result_baseline, result_fep


def update_cfg_file(svn_dir_repository, cfg_file_name):
    global IS_CFG_CHANGED
    svn_work_directory = os.path.basename(svn_dir_repository)
    file_name = svn_work_directory + '/' + cfg_file_name
    new_file_name = svn_work_directory + '/' + TEMP_CFG_FILE_NAME
    regex = re.compile(r'DNH\d+.0_ENB_\d{4}_\d{3}_\d{2}')
    regex2 = re.compile(r'.+:')
    try:
        file_handle = open(file_name, 'rb')
        write_handle = open(new_file_name, 'w+')
        for read_line in file_handle:
            clean_line = read_line.strip()
            if clean_line == "" or clean_line is None:
                continue
            for fet_type in FEP_TYPE_LIST:
                if read_line.find(fet_type) != -1:
                    log("Info: Update line, " + clean_line)
                    # update_baseline = INPUT_MAPPING_DICT.get(fet_type)
                    update_baseline, update_fep = get_baseline_from_input(fet_type)
                    src_baseline = clean_line.split(":")[1]
                    log("Info: Update_baseline = " + repr(update_baseline) + ", src_baseline = " + src_baseline)
                    if update_baseline == src_baseline:
                        log("Info: No need to update.")
                    elif src_baseline is None or update_baseline is None:
                        log("Info: There is no the baseline information. Continue.")
                    else:
                        read_line = re.sub(regex, update_baseline, read_line)
                        read_line = re.sub(regex2, update_fep + ":", read_line)
                        log("Info: update the line to: " + read_line)
                        IS_CFG_CHANGED = True
                    break
            write_handle.write(read_line)
        if not IS_CFG_CHANGED:
            log("Info: The CFG file does not need to update.")
    except Exception, e:
        log("Error: Update cfg file error...")
        log(traceback.format_exc())
        raise e
    else:
        file_handle.close()
        write_handle.close()


def add_input_dict(branch_enb_baseline, in_name):
    log("Info: add input dict start... branch load name = " + branch_enb_baseline + ", fep_name = " + in_name)
    if branch_enb_baseline == "" or in_name == "":
        log("Error: When add input dict error, input value is not correct.")
    INPUT_MAPPING_DICT[in_name] = branch_enb_baseline


def usage(file_name):
    usage_text = """
    $text_name have follow parameter for use. "-b" and "-c" are mandatory.
    -b: The branch CFG file name for updating, e.g., 16B:DNH4.0_CFG, DNH5.0_BASE_CFG. Required.
    -f: The directory of "Finding_copy_result.txt". E.g.,/build/home/xxp/branch_build/Finding_copy_result.txt. Required.
    -l: Update branch ENB load name.
    -t: FEP name.
    -b is must required. -f or (-l and -t) should be used. -l and -t should be used at the same time.
    """
    usage_s = string.Template(usage_text)
    param = {"text_name": file_name}
    print usage_s.safe_substitute(param)


def clean_workspace():
    os.system("rm -rf " + WORK_SPACE_NAME)


def copy_command(file_name, directory):
    cp_command = "cp -pf" + file_name + " " + directory
    os.system(cp_command)


def svn_co_command(svn_dir_repository, cfg_file_name):
    co_command = "svn co --depth=empty " + svn_dir_repository
    father_directory = os.path.basename(svn_dir_repository)
    file_name = father_directory + '/' + cfg_file_name
    update_command = "svn update " + file_name
    os.system(co_command)
    os.system(update_command)


def svn_commit_command(svn_dir_repository, cfg_file_name):
    father_directory = os.path.basename(svn_dir_repository)
    file_name = father_directory + '/' + cfg_file_name
    commit_command = "svn --username \"lteman\" --password \"7492d62e\" commit -m \\\"IMSUREWHATIMDOING: Update change." + "\\\" " + file_name
    log("info: commit command = " + commit_command)
    # os.system(commit_command)
    # output = os.popen(commit_command)
    os.system('''expect -c \"
    set timeout 10
    spawn %s
    expect {
        \"*unencrypted*\"
        {
            send \"yes\\\\r\";
            exp_continue;
        }
    }\"''' % commit_command)


def move_temp_file(folder, source, new):
    source_file = folder + '/' + source
    new_file = folder + '/' + new
    mv_command = "mv " + source_file + " " + new_file
    os.system(mv_command)


def log(msg):
    with open('sync_to_cfg.log', 'a') as log_file:
        print(msg)
        log_file.write(msg + '\n')


if __name__ == '__main__':
    update_file_name = ''
    input_file_name = ''
    branch_baseline = ""
    fep_name = ""
    update_type_list = []

    if len(sys.argv) > 1:
        try:
            options, args = getopt.getopt(sys.argv[1:], "b:f:l:t:", ["update_file_name=", "input_file=", \
                                                                     "branch_baseline=", "FEP="])
        except getopt.GetoptError:
            usage(sys.argv[0])
            sys.exit(1)
    else:
        usage(sys.argv[0])
        sys.exit(1)
    for name, value in options:
        if name in ("-b", "--update_file"):
            update_file_name = value
        elif name in ("-f", "--input_file"):
            input_file_name = value
        elif name in ("-l", "--branch_baseline"):
            branch_baseline = value
        elif name in ("-t", "--FEP"):
            fep_name = value
        else:
            usage(sys.argv[0])
            sys.exit(1)

    if update_file_name == '':
        usage(sys.argv[0])
        sys.exit(1)

    if branch_baseline != "" and fep_name != "":
        update_type_list.append(UPDATE_TYPE_FEP)

    if input_file_name != "":
        update_type_list.append(UPDATE_TYPE_FPGA)

    log("Info: Update type = " + repr(update_type_list))

    cfg_repo_folder = os.path.basename(SVN_CFG_REPO)
    clean_workspace()
    os.system("mkdir " + WORK_SPACE_NAME)
    os.chdir(WORK_SPACE_NAME)
    svn_co_command(SVN_CFG_REPO, update_file_name)
    for update_type in update_type_list:
        if update_type == UPDATE_TYPE_FPGA:
            get_branch_baseline(input_file_name)
        elif update_type == UPDATE_TYPE_FEP:
            add_input_dict(branch_baseline, fep_name)
        else:
            log("Error: Incorrect update type.")
            sys.exit(1)
    try:
        update_cfg_file(SVN_CFG_REPO, update_file_name)
    except:
        log(traceback.format_exc())
        sys.exit(1)
    if IS_CFG_CHANGED:
        log("Info: The CFG file start to commit.")
        move_temp_file(cfg_repo_folder, update_file_name, update_file_name + ".bak")
        move_temp_file(cfg_repo_folder, TEMP_CFG_FILE_NAME, update_file_name)
        svn_commit_command(SVN_CFG_REPO, update_file_name)
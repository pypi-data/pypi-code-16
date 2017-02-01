# from HeadLess import HeadLess as extractor
from SocialCrawler import HeadLess as extractor
import json
import re
import os,glob
import unicodedata

# import HackFoursquare

# hack = Hacking("josiel.wirlino@gmail.com","j0sielengenheiro")
# hack.open_browser()

# venue = hack.get_venue_detail("5611c005498eacfce78eceee")
# venue2 = json.loads(venue)

def get_file_output_name(input_file):
    # ifile = remove_accents(input_file)
    # regex = "(?<=from_)\w+_?\d{2}-\d{2}-\d{2}"
    regex = "(?<=from_).+"
    r_compiled = re.compile(regex)
    matched = r_compiled.search(input_file)
    # if matched.group())
    # print(input_file)
    if matched:
        return matched.group(0)
    else:
        return None

path_to = "/home/wirlino/MEGAsync/SocialCrawler_DataSet/Testing"
path_from = "/home/wirlino/MEGAsync/SocialCrawler_DataSet/Testing/"

retrieve_item = 0


os.chdir(path_from)
brasil_file_list = []
for file in glob.glob("*.tsv"):
    brasil_file_list.append(file)


def get_files( thread_api_4square, thread_id):
    global retrieve_item
    global brasil_file_list
    while retrieve_item < len(brasil_file_list):
        retrieve_item += 1
        f_name = get_file_output_name( brasil_file_list[retrieve_item-1])
        
        if f_name is None:
        	f_name = brasil_file_list[retrieve_item-1]
        f_name = f_name[:len(f_name)-4]

        print("Thread "+str(thread_id) +" reading " + brasil_file_list[retrieve_item-1])
        
        thread_api_4square.settings(mode="v1",
			  out_file_name="foursquare_"+f_name,
			  out_path_file=path_to,
			  input_file=path_from+brasil_file_list[retrieve_item-1] 
			  )
        # for line in open(file_name_list[retrieve_item-1],'r'):
        #     a = 1
        thread_api_4square.consult_foursquare()
        print("Thread "+str(thread_id) + " done" )

class_extractor = extractor.HeadLess(developer_email="josiel.wirlino@gmail.com",developer_password="j0sielengenheiro",debug_mode=True)
get_files(class_extractor, "hacking_version")

# c = HackFoursquare.Hacking(developer_email="josiel.wirlino@gmail.com",developer_password="j0sielengenheiro",mode="show")
# c.open_browser()

# r = c.get_info_detail(v="v",key_id="4c6e667465eda0938a3d51d0")

# j = json.loads(r)
# print( j['response']['venue']['location']['lat'])
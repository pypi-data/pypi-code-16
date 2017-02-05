# from SocialCrawler import NewExtractorData

# client_id = "GEQQO0MJPKLUTBIZHERRYQJUCTU5W2MGFAHZKCDB3LYB1GZI"
# client_secret = "QMXESMEH1VKEEKUQ0EBXNCJ4IWCK0EYHA0MUHNVBMGSWXRUZ"

# file_name = "Brasillog_from_Cuiaba__2016-08-28__2016-09-05.tsv"



# test = NewExtractorData.NewExtractor(client_id,client_secret,developer_email="josiel.wirlino@gmail.com",developer_password ="j0sielengenheiro")

# indice = 0
# # while( indice < 4):

# test.settings(mode="v1",
# 			  out_file_name="cuiaba_final_agosto",
# 			  out_path_file="/home/wirlino/Documents/Git/SocialCrawler/SocialCrawler/",
# 			  input_file="/home/wirlino/Documents/Git/SocialCrawler/SocialCrawler/"+file_name			  
# 			  )

# """ We are setting mode to v1 that means the file was created by or Collector or CollectorV2
#     output file created will be log_new_york.tsv and will be saved in ./Log/
#     the input file ( that contains t.co url ) are localed in ./Log/Brasil/ folder
# """

# test.consult_foursquare()

import threading
import re
import os,glob
import unicodedata
from SocialCrawler.NewExtractorData import NewExtractor


def remove_accents(input_str):
    """
    get from http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    """

    enconding = 'utf-8'
    b_string = input_str.decode(enconding)
    nfkd_form = unicodedata.normalize('NFKD', b_string)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

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

client_id_1 = "GEQQO0MJPKLUTBIZHERRYQJUCTU5W2MGFAHZKCDB3LYB1GZI"
client_secret_1 ="QMXESMEH1VKEEKUQ0EBXNCJ4IWCK0EYHA0MUHNVBMGSWXRUZ"

client_id_2 = "JGX5VIAPVC25BZ4Y1LFIPX2JEJDKXAB3XMDAHBOYAXBNDFEV"
client_secret_2 ="VVWNSTM1G2CFTEEL21ENRDOLUYJY5JWKOBYBPO4WYUZIPTWF"


client_id_3 = "AUU4MDBWNNTWSWF00QUVFOIOWLYK1ASZUXGUCOMZQGBB52OX"
client_secret_3 ="R1O1MXOUZ3EHDNXSJFNJI5DTWMZFRDYKJX5SKE3DU5CAXXKI"

client_id_4 = "TOJ5E0V0ECJSXJUJOJOINPHGSLCKK1CGEBVGZXVE3JPNLP0R"
client_secret_4 ="N4ZDB2KOPUOCRSHI3K12UFZ0VOJOVGE0H44WX4NG4Y1L1W0P"

client_id_5 = "NP3N1NYNYNFRE4JHE4G1SK44WGENYYC4HB4YFADDAFB5GM1M"
client_secret_5 = "AXGB42JOEQADTXRU304UAZAJ5DQNIND15KEPVN4ZWMDNMPRN"

path = "/home/wirlino/MEGAsync/SocialCrawler_DataSet/"

file_name_list = [path+"log_from_Aracaju__2016-11-14__2016-11-19.tsv",
                  path+"Brasillog_from_Belem__2016-08-28__2016-09-05.tsv",
                  path+"Brasillog_from_CampoGrande__2016-08-28__2016-09-05.tsv",
                  path+"Brasillog_from_SaoPaulo__2016-08-28__2016-09-05.tsv",
                  path+"log_from_Belem__2016-08-28__2016-09-05.tsv"
                  ]

retrieve_item = 0

os.chdir(path+"Brasil")
brasil_file_list = []
inter_file_list = []

for file in glob.glob("*.tsv"):
    brasil_file_list.append(file)
    # print( get_file_output_name(brasil_file_list[retrieve_item]) )
    # retrieve_item += 1

# os.chdir(path+"Inter")
#
# t= 0
# for file in glob.glob("*.tsv"):
#     inter_file_list.append(file)
#     print(get_file_output_name(inter_file_list[t]))
#     t+=1
#     retrieve_item += 1

# print(retrieve_item)

# def readfile(filename):



r_1 = NewExtractor(client_id_1,
									client_secret_1
									)

r_2 = NewExtractor(client_id_2,
									client_secret_2
									)
r_3 = NewExtractor(client_id_3,
									client_secret_3
									)
r_4 = NewExtractor(client_id_4,
									client_secret_4
									)
r_5 = NewExtractor(client_id_5,
									client_secret_5
									)

# indice = 0
# # while( indice < 4):

# test.settings(mode="v1",
# 			  out_file_name="cuiaba_final_agosto",
# 			  out_path_file="/home/wirlino/Documents/Git/SocialCrawler/SocialCrawler/",
# 			  input_file="/home/wirlino/Documents/Git/SocialCrawler/SocialCrawler/"+file_name			  
# 			  )

# """ We are setting mode to v1 that means the file was created by or Collector or CollectorV2
#     output file created will be log_new_york.tsv and will be saved in ./Log/
#     the input file ( that contains t.co url ) are localed in ./Log/Brasil/ folder
# """

# test.consult_foursquare()

def get_thread( thread_api_4square, thread_id):
    global retrieve_item
    global file_name_list
    while retrieve_item < len(brasil_file_list):
        retrieve_item += 1
        f_name = get_file_output_name( brasil_file_list[retrieve_item-1])
        
        if f_name is None:
        	f_name = brasil_file_list[retrieve_item-1]
        f_name = f_name[:len(f_name)-4]

        print("Thread "+str(thread_id) +" reading " + brasil_file_list[retrieve_item-1])
        
        thread_api_4square.settings(mode="v1",
			  out_file_name="foursquare_"+f_name,
			  out_path_file=path+"Testing",
			  input_file=path+"Brasil/"+brasil_file_list[retrieve_item-1] 
			  )
        # for line in open(file_name_list[retrieve_item-1],'r'):
        #     a = 1
        thread_api_4square.consult_foursquare()
        
        print("Thread "+str(thread_id) + " done" )


t1 = threading.Thread(target=get_thread,args=(r_1,"t1",))
t2 = threading.Thread(target=get_thread,args=(r_2,"t2",))
t3 = threading.Thread(target=get_thread,args=(r_3,"t3",))
t4 = threading.Thread(target=get_thread,args=(r_4,"t4",))
t5 = threading.Thread(target=get_thread,args=(r_5,"t5",))

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

# t2.start()








import pymp4parse

filename = '/Users/alastair.mccormack/Downloads/TomAndHuck_25fps-6ch_ENG_H264_1920x1080_25_AC3_51_5625_DVB_3170.mp4'
myf = open(filename, 'rb')
my_bytes = myf.read(8)

# print( pymp4parse.F4VParser.is_mp4_s(my_bytes) )

# for box in pymp4parse.F4VParser.parse(bytes_input=my_bytes, headers_only=False):
#      print(box)

for box in pymp4parse.F4VParser.parse(filename=filename, headers_only=False):
    print(box)

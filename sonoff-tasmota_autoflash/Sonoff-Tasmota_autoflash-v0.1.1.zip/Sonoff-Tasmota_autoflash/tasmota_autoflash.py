import os
import sys
import serial.tools.list_ports
import json
import tempfile
import urllib

def ports():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print p
    return ports

def download():
    #JSON Document url
    url = "https://api.github.com/repos/arendst/Sonoff-Tasmota/releases"

    #get data and parse it
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    #get tempfolder path
    tempdir=tempfile.gettempdir()

    #get os
    os_name = os.name

    #set file name
    if (os_name=="posix"):
        firmware_name=r"/firmware.bin"
    elif (os_name=="nt"):
        firmware_name=r"\firmware.bin"
    else: print ("OS not supported")
    
    #concat strings to firmeware_path
    firmware_path=tempdir+firmware_name
    print(firmware_path)
    #save values 
    browser_download_url=data[0]['assets'][0]['browser_download_url']
    size_file=data[0]['assets'][0]['size']

    print(browser_download_url)
    #download file 
    urllib.urlretrieve(browser_download_url, firmware_path)

    #get size of the downloaded file

    size_download_file=os.path.getsize(firmware_path)


    print(" The file should be ",  size_file)
    print(" The file is ",  size_download_file)

    #compare filesize to have a basic verification 
    if (size_file == size_download_file):
        print("Download succsseful")
    else:
        print("Error: The size of the downloaded file does not match")

    return firmware_path
    


#user input
print("Please connect your device now")
print("Aviable Ports:")
ports()

port=raw_input("Which port do you want to use?\n")
device= raw_input("Which device are you using? Type 0 for touch or 4CH and 1 for the others\n")
#filepath=raw_input("Enter the filepath of the firmwarefile\n")
filepath=download()

# clear flash
err_erase=os.system("esptool.py --port "+port+" erase_flash")
print(err_erase)

#Process Error
if(err_erase !=0):
    print("Error while erasing. Check your connection.")
    sys.exit()


#Wait to reconnect
raw_input("Reconnect then press enter\n")

#Select device
if(device == "0"):
#Flash with command for 4CH and Touch
    err_write=os.system("esptool.py --port "+port+" write_flash -fm dout -fs detect 0x0 "+filepath)
elif(device == "1"):
#Flash with command for all others
    err_write=os.system("esptool.py --port "+port+" write_flash -fm dio -fs detect 0x0 "+filepath)

#Process Error
if(err_write !=0):
    print("Error while writing. Check your connection.")
    sys.exit()

print("Successful")

os.remove(filepath)
#

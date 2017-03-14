import requests
import subprocess
import os
import sys
import pyperclip
from bs4 import BeautifulSoup as bs
from subprocess import check_output
from youtubeAudio import download
'''What it does-
"Download song of your choice in audio format in two steps by just entering the name."

Usage - 4 ways:-
1. Run the program and enter the song name.
2. From cmd line or run enter "song <song name>". This is will give you top
    n results(n depends on you).
3. From cmd line or run enter "song /<song name>". First result will be automatically downloaded.
   Add '/' ultimately(or penultimately if you are using next option to not run after downloading.)
4. Add 1 at last to download both video and audio.
   and 0 at last to download only video.
   Don't add anything for only audio.
5. You can just copy the song name and run "song" command from cmd or run. No
need to paste just copy. Note:-This will automatically download the first result by default. (You
can change that too.)
6. You can create a keyboard shorcut to shorten the 4th way even more. Just copy the
    the song name and press that Keyboard shortcut. And the download will start.

MIT License-
Tushar Tripathi
tushutripathi@gmail.com
'''

pathA = 'D:\\DC++Share\\Songs\\pyDirect'          # Path for audio
pathV = 'D:\\DC++Share\\Songs\\Video\\pyDirect'   # Path for Video
path = pathA


# Getting pid of the cmd prompt open so that it can be closed in last.
def get_pid():
    ''' Logic:- tasklist gives the tasks in order they are opened. Running the program
    will open a cmd prompt. Now if we immediately just after running the script check
    the processes then the last cmd.exe will be what is opened by this program.
    So we will get the pid which we will close at last.'''
    a = check_output(["tasklist"])
    p = a.replace('\r', '').split('\n')[3:-2]
    for i in range(-1, -len(p), -1):
        if "cmd.exe" in p[i]:
            return int(p[i].split()[1])


def check(tag):         # Custom function to get the channel names through BeautifulSoup
    if tag.has_attr('class') and ('g-hovercard' in tag['class']) and tag.parent.name == 'div':
        return True
    else:
        return False


# If auto is 1 it will not give options, directly send the first result.
# Function return video url and title.
def get(query, auto=0):
    base = "https://www.youtube.com"
    search_url = "https://www.youtube.com/results"
    payload = {'search_query': query, 'page': '', 'utm_source': 'opensearch'}
    r = requests.get(search_url, params=payload)
    soup = bs(r.text, "html.parser")
    # all a tags containing link has this in class name
    videos = soup.find_all("a", class_="yt-ui-ellipsis-2")

    if auto == 1:     # Automatically choses the first one to download.
        print ("File to download ", videos[0].string)
        return (base + videos[0]['href'], videos[0]['title'])

    else:
        # cc=Channel Count-will be used to access the channel name from the channels array.
        count, cc = 1, 0
        channels = soup.find_all(check)  # Scraping channel names
        print('\a')
        print ("Choose what you want. Just enter the corresponding number.")

        for video in videos:
            if 'g-hovercard' in video['class']:  # Skipping over channels
                cc += 1
                continue
            try:
                # In case of playlist the code will tell in the same line
                print "%d. %s" % (count, video.string.strip()),
                if 'list' in video['href']:    # If its a playlist
                    print " - A PLAYLIST",
                print ""

                channel = channels[cc]
                if video.parent.next_sibling.string == "YouTube":
                    print ("-Made by Youtube.")
                else:
                    try:        # Checking if its verified channel
                        print "Channel - ", channel.string.strip(), "-Verified"
                    except:
                        print "Channel - ", channel.string.strip()  # Not verified
                    count += 1

                cc += 1

            except:
                pass

            # Change it to how many options you want(max value-21)
            if count == 6 or cc == len(channels):
                break
            print ""
        choice = int(raw_input("\nNow enter your choice- "))
        print "You chose- ", videos[choice - 1].string.encode('ascii', 'ignore')
        print "Download is starting..."
        return (base + videos[choice - 1]['href'], videos[choice - 1]['title'])


def openFile(title):
    # print "Opening the folder."
    # subprocess.Popen('explorer '+path)
    global path
    print "Let's play the music."
    for ext in ['.webm', '.m4a', '.mp3', '.mp4', '.flv']:
        name = path + "\\" + title + ext
        if os.path.isfile(name):
            subprocess.Popen('"' + name + '"', shell=True)
            break
        # In hindi songs - is replaced by _ for some reasons IDK. Smthing to do with youtube-dl.
        elif os.path.isfile(name.replace('-', '_')):
            name = name.replace('-', '_')
            subprocess.Popen('"' + name + '"', shell=True)
            break
    else:
        print "File can't be opened for some reasons."
        print "Opening the folder."
        path = '"' + path + '"'
        subprocess.Popen('explorer ' + path)


def main(query):
    global path
    whatToDownload = 'audio'                    # Whether to download audio or video.
    if query[-1] == '1':            # Download Video.
        print "Note:- Song video as well as audio will be downloaded."
        query = query[:-1].strip()
        path = pathV
        whatToDownload = 'both'
    elif query[-1] == '0':
        query = query[:-1].strip()
        path = pathV
        whatToDownload = 'video'
        print "Only Song video will be downloaded."
    else:
        print "Only Song Audio will be downloaded."

    file_open = True                # Whether to open the file after download.
    if query[-1] == '/':              # Do not open the file after download.
        query = query[:-1]
        file_open = False

    if query[0] == '/':               # Download the first song without showing any list.
        query = query[1:]
        url, title = get(query, 1)
    else:                           # Show the list to chose what to download.
        url, title = get(query)

    title = title.encode('ascii', 'ignore')
    title = title.replace('"', "'")  # Replacing " by '. Because youtube_dl does so before saving.

    print "Got the url", url
    print "And the name", title
    for ext in ['.webm', '.m4a', '.mp3', '.mp4', '.flv']:
        name = path + "\\" + title + ext
        if os.path.isfile(name) or os.path.isfile(name.replace('_', '-')):
            print "Oh! It's already downloaded."
            break
    else:
        print "Starting download..."
        if whatToDownload in ['audio', 'both']:
            print "Downloading Audio..."
            download(url, title, audio=True)
        if whatToDownload in ['video', 'both']:
            print "\nNow Downloading Video..."
            download(url, title, audio=False)
    if file_open:
        openFile(title)


if __name__ == "__main__":
    pid = get_pid()
    try:
        sys.argv[1]         # Checks if cmd line argument is given
        query = " ".join(sys.argv[1:])
    except:
        if "idlelib" in sys.modules:
            query = raw_input("Enter the song's name. - ")
        else:
            query = "/" + pyperclip.paste()
    try:
        main(query)
        subprocess.Popen("TASKKILL /F /PID {pid}".format(pid=pid))  # Close cmd only if successful.
    except Exception as e:
        print "Error occured-"
        print e

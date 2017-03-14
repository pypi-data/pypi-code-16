from __future__ import unicode_literals
import youtube_dl, os, subprocess

pathA = 'D:/DC++Share/Songs/pyDirect'        # Path for audio
pathV = 'D:/DC++Share/Songs/Video/pyDirect'  # Path for video

def download(url, name, audio=True):
    if audio==True:   # To download audio.
        path = pathA
    else:
        path = pathV
    print "Downloading-", name
    os.chdir(path)                          # Path changed to download folder.
    if audio:
        options = {
            'format': 'bestaudio/best',         # choice of quality
            'extractaudio' : True,             # choosing whether to donwload audio or video.
            'audioformat' : "mp3",              # convert to mp3 for audio format.
            'outtmpl' : '%(title)s.%(ext)s',    # Name of output.
            'noplaylist' : True,                # only download single song, not playlist
        }
    else:
        options = {
            'outtmpl' : '%(title)s.%(ext)s',    # Name of output.
            'noplaylist' : True,                # only download single song, not playlist
        }

    ydl = youtube_dl.YoutubeDL(options)
    with ydl:
        ydl.download([url])
    print ("Download Finished. Keep smiling. :-)")
    return None

if __name__=="__main__":
    url = raw_input("Input song's url - ")
    download(url)

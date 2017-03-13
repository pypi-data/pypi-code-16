from .settings import *
from .extract  import *

def notify():

    if '--help' in sys.argv or '-h' in sys.argv:

        print ""
        print "-------------------------------------------------------------------------"
        print ""
        print "description:"
        print ""
        print "  This operation will check if station are uploading data properly"
        print "  and will notify the relevant station's owner if missing data are"
        print "  being detected."
        print ""
        print "-------------------------------------------------------------------------"
        print ""
        quit()

    os.chdir(setup.home+'/analysis/nuri/activetime/')
    sys.stderr.write('Retrieve information from Google Drive...')
    os.system('skicka ls -r /MagneticFieldData/ > data')
    data = np.loadtxt('data',dtype=str,delimiter='\n')
    print >>sys.stderr,' done!'
    for station in [1,2,3,4]:
        missing = []
        target  = datetime.utcnow()-timedelta(days=1)
        for hr in range(24):
            target = datetime(target.year,target.month,target.day,hr)
            str1   = target.strftime('%Y/%-m/%-d/%-H')
            str2   = target.strftime('%Y-%-m-%-d_%-H')
            if 'MagneticFieldData/%s/NURI-station-%02i/%s-xx.zip'%(str1,station,str2) not in data:
                missing.append(hr)
        if len(missing)>0:
            yesterday   = (date.today()-timedelta(1)).strftime('%A, %B %d, %Y')
            EMAIL_FROM  = 'vincentdumont11@gmail.com'
            EMAIL_TO    = ['bale@ssl.berkeley.edu'] if station==1 else \
                          ['vdumont@berkeley.edu']  if station==2 else \
                          ['wurtele@berkeley.edu']  if station==3 else \
                          ['dbudker@gmail.com']
            EMAIL_SPACE = ', '
            hrs = EMAIL_SPACE.join(['%i'%hr for hr in missing])
            msg ="Dear Station's owner,\n"
            msg+='\n'
            msg+='%i out of 24 data files are found missing from yesterday:\n'%len(missing)
            msg+='%s\n'%yesterday
            msg+='\n'
            msg+='The missing hours are the following:\n'
            msg+='%s\n'%hrs
            msg+='\n'
            msg+='Please check your station and make sure the computer is turned on\n'
            msg+='and all the USB cables are properly connected.\n'
            msg+='\n'
            msg+='Here are the instructions to reset the station:\n'
            msg+='\n'
            msg+='1. Disconnect each USB cable;\n'
            msg+='2. Shut down the computer;\n'
            msg+='3. Reconnect the cables;\n'
            msg+='4. Turn on the computer;\n'
            msg+='5. Open the data grabber application (available from the Desktop)\n'
            msg+='6. Click the "refresh" button for the GPS to make sure it identifies\n'
            msg+='the correct port;\n'
            msg+='7. Hit the "open" button. If the connection works properly, you should\n'
            msg+='see a text highlighted in green mentioning the UTC time. If the text\n'
            msg+='says "No Data", then there is a problem with the USB connection, try\n'
            msg+='re-connecting the cable on a different port and refresh.\n'
            msg+='8. Click the "refresh" button for the sensor to make sure it identifies\n'
            msg+='the correct port;\n'
            msg+='9. Hit "record", you should start seeing the data streaming on the screen;\n'
            msg+='\n'
            msg+="Do not close the application! The laptop's lid can be closed though.\n"
            msg+='As long as the computer is still turned on, data should be streaming\n'
            msg+='and uploading without any problem.\n'
            msg+='\n'
            msg+='Many thanks!\n'
            msg+='Vincent'
            msg = MIMEText(msg)
            msg['Subject'] = 'NURI Automatic Notification - Missing data from station %i...'%station
            msg['From']    = EMAIL_FROM
            msg['To']      = EMAIL_SPACE.join(EMAIL_TO)
            smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpObj.login(EMAIL_FROM, 'newaknlsgkwehexe')
            smtpObj.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            smtpObj.quit()
    os.system('rm data')

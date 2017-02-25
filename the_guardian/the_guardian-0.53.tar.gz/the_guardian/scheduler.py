#! /usr/bin/env python3
from datetime import datetime, timedelta
import time
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
import sys
import webbrowser

def desktop_notification(message):
    """
    """
    Notify.init("mom notifier")
    notification = Notify.Notification.new(message[0],message[1])
    
    notification.show()
    
    return

class mom:
    """
    """
    
    def __init__(self, reminder_time = 50):
        """
        """
        self._messages = []
        self._messages.append(("It's work time!",
                               "Lets give everything to it."))
        self._messages.append(("Time to rejuvenate!",
                               "let's walk or read Wikipedia"))
        
        self._work_interval = timedelta(minutes = reminder_time)
        self._rest_interval = timedelta(minutes = 10)
        #For Testing purposes
        #self._work_interval = timedelta(seconds = 5)
        #self._rest_interval = timedelta(seconds = 5)
        
        Notify.init("mom notifier")
        summary = "Startup Notification!"
        body = "Hi!"
        self._notification = Notify.Notification.new(summary,body)
        self._url = 'https://en.wikipedia.org'
        return
    
    
    def __del__(self):
        """
        """
        
        end_message = tuple(("Closing sessions!", "See you later"))
        self._desktop_notification(end_message)
        Notify.uninit()
        
        return
    
        
    def _run(self, dt = timedelta(minutes = 50)):
        """
        """
        
        begin = datetime.today()
        correction = timedelta(minutes = begin.time().minute,
                               seconds = begin.time().second)

        begin = begin - correction
        end   = begin + dt
                
        while (datetime.today().time() < end.time()):
            
            if datetime.today().minute == 30:
                self._desktop_notification(("Knock! Knock!",
                                            "Hope that you are studying"))
            time.sleep(1)
        
        return
    
    def _desktop_notification(self, message):
        """
        """
        self._notification.update(message[0], message[1])
        self._notification.show()
        
        return
    
    def start(self, sessions = 1):
        """
        """
        
        startup_message = tuple(("Starting timer!",
                                 "Sessions = {}".format(sessions)))
        
        self._desktop_notification(startup_message)
        #time.sleep(5)
        
        for session in range(sessions):
            self._desktop_notification(self._messages[0])
            self._run(self._work_interval)
            self._actions()
            
            self._desktop_notification(self._messages[1])
            self._run(self._rest_interval)
        
        return
    
    def _actions(self):
        """
        """
        
        webbrowser.open_new_tab(self._url)
        return
    

def guardian(sessions = None, reminder = None):
    try:
        if sessions == None or reminder == None:
            raise Exception('Number of sessions or reminder time not provided.')
        
        obj = mom(reminder_time = int(reminder))
        obj.start(sessions = int(sessions))

    except Exception as error:
        message = tuple(('Caught Error: ', repr(error)))
        desktop_notification(message)
    
    return

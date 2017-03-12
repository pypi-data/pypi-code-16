# -*- coding: utf-8 -*-
"""
poll meetup.com for a member_id and automatically rsvp yes to new events
send confirmation email with link and description
"""
import time
import requests
from datetime import datetime
import yaml
import os
from xtools.tools import send

import logging as log
from logging.config import dictConfig
home = os.path.expanduser("~")
dictConfig(yaml.load(open(os.path.join(home, ".logconfig.yaml"))))

creds = yaml.load(open(os.path.join(home, ".meetups", "creds.yaml")))
meetup = creds["meetup"]

def get_events():        
    """ return new events (rsvp=none) """
    r=requests.get("https://api.meetup.com/2/events",
                    params=dict(key=meetup["key"], sign=True,
                                rsvp="none",
                                fields="rsvpable",
                                member_id=meetup["member_id"]))
    try:
        return r.json()["results"]
    except:
        log.info(r.status_code)
        log.info(r.text)
        return []

def rsvp(events):
    """ for each event, rsvp yes and send confirmation email """
    for event in events:
        if not event["rsvpable"]:
            continue
        
        # rsvp yes
        r=requests.post("https://api.meetup.com/2/rsvp",
                        params=dict(key=meetup["key"], sign=True,
                        event_id=event["id"],
                        rsvp="yes"))
        
        # compile email
        subject = "auto_rsvp_yes to %s"%event["name"]       
        content = event["description"]
        if r.status_code != 201:
            subject = "FAILED " + subject
            content = "%s<br><br>%s"%(r.status_code, r.text)
        time = datetime.fromtimestamp(int(event["time"])/1000) 
        time = time.strftime('%Y-%m-%d %H:%M')
        url = ""
        try:
            url = "https://www.meetup.com/{group}/events/{id}/" \
                    .format(group=event["group"]["urlname"], id=event["id"])
        except Exception:
            log.exception(url)
        try:
            message = "{content}".format(content=content)
        except Exception:
            log.exception(content)

        message = "{url}<br><br>{time}<br><br>{content}".format(**locals())

        send(subject, message)
    
def main():
    """ periodic check for new events and automatically rsvp """
    minutes = 10
    log.info("Every %s minutes, check for new meetups and automatically RSVP"%minutes)
    while True:
        try:
            rsvp(get_events())
            time.sleep(minutes * 60)
        except Exception as e:
            log.exception(e)
            
if __name__ == "__main__":
    main()
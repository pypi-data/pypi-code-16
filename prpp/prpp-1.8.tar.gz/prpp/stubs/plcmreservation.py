#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 5 févr. 2016

@author: Adrien
'''
from .plcm import Plcm
import datetime
from .plcmreservedparticipantlist import PlcmReservedParticipantList
from ..entities.utils import STRPTIME_UTC
from dateutil.rrule import rrulestr, rrule
from django.utils.timezone import utc
from dateutil.relativedelta import relativedelta

DAILY_TYPE_ENUM={
    'EVERY_N_DAY':'EVERY_N_DAY',
    'EVERY_WEEKDAY':'EVERY_WEEKDAY',
}

class PlcmRecurDaily(Plcm):
    content_type = "application/vnd.plcm.plcm-recur-daily+xml"
    root_element = "plcm-recur-daily"
    target_namespace = "urn:com:polycom:api:rest:plcm-recur-daily"
    imported_namespaces = []
    
    element_properties={
        'daily-type-enum': { 'prop':'daily_type','tag':'daily-type-enum','type':'enum','values':DAILY_TYPE_ENUM },
        'interval' : { 'prop':'interval','tag':'interval'},
    }
    daily_type=None
    interval=None

    def xml_build_content(self, xml_root, nsmap=None):
        #Build xml attributes from properties
        xml_root = self.xml_build_from_properties(xml_root, xml_root.nsmap)
        return xml_root


class PlcmRecurWeekly(Plcm):
    content_type = "application/vnd.plcm.plcm-recur-weekly+xml"
    root_element = "plcm-recur-weekly"
    target_namespace = "urn:com:polycom:api:rest:plcm-recur-weekly"
    imported_namespaces = []
    
    element_properties={
        'day-of-week-mask': { 'prop':'day_of_week_mask', 'tag':'day-of-week-mask' },
        'interval' : { 'prop':'interval','tag':'interval'},
    }
    day_of_week_mask=None
    interval=None
    
    def xml_build_content(self, xml_root, nsmap=None):
        #Build xml attributes from properties
        xml_root = self.xml_build_from_properties(xml_root, xml_root.nsmap)
        return xml_root



class PlcmRecurMonthly(Plcm):
    '''Used to specify the day with this number evry month'''
    content_type = "application/vnd.plcm.plcm-recur-monthly+xml"
    root_element = "plcm-recur-monthly"
    target_namespace = "urn:com:polycom:api:rest:plcm-recur-monthly"
    imported_namespaces = []
    
    element_properties={
        'day': { 'prop':'day', 'tag':'day' },
        'interval' : { 'prop':'interval','tag':'interval'},
    }
    day=None
    interval=None
    
    def xml_build_content(self, xml_root, nsmap=None):
        #Build xml attributes from properties
        xml_root = self.xml_build_from_properties(xml_root, xml_root.nsmap)
        return xml_root


PREFIX_TYPE_ENUM={
    'FIRST':'FIRST',
    'SECOND':'SECOND',
    'THIRD':'THIRD',
    'FOURTH':'FOURTH',
    'LAST':'LAST',
}

DAY_TYPE_ENUM={
    'DAY':'DAY',
    'WEEKDAY':'WEEKDAY',
    'WEEKEND_DAY':'WEEKEND_DAY',
    'SUNDAY':'SUNDAY',
    'MONDAY':'MONDAY',
    'TUESDAY':'TUESDAY',
    'WEDNESDAY':'WEDNESDAY',
    'THURSDAY':'THURSDAY',
    'FRIDAY':'FRIDAY',
    'SATURDAY':'SATURDAY',
}

class PlcmRecurMonthlyNth(Plcm):
    '''Used to specify a specific day in the month relative to others'''
    content_type = "application/vnd.plcm.plcm-recur-monthly-nth+xml"
    root_element = "plcm-recur-monthly-nth"
    target_namespace = "urn:com:polycom:api:rest:plcm-recur-monthly-nth"
    imported_namespaces = []
    
    element_properties={
        'prefix-type-enum': { 'prop':'prefix_type', 'tag':'prefix-type-enum','type':'enum','values':PREFIX_TYPE_ENUM },
        'day-type-enum' : { 'prop':'day_type','tag':'day-type-enum','type':'enum','values':DAY_TYPE_ENUM }, 
        'interval' : { 'prop':'interval','tag':'interval'},
    }
    prefix_type=None
    day_type=None
    interval=None
    
    def xml_build_content(self, xml_root, nsmap=None):
        #Build xml attributes from properties
        xml_root = self.xml_build_from_properties(xml_root, xml_root.nsmap)
        return xml_root


SCHED_RECURRENCE_TYPE_ENUM = {
    'DAILY':'DAILY',
    'WEEKLY':'WEEKLY',
    'MONTHLY':'MONTHLY',
    'MONTHLY_NTH_DAY':'MONTHLY_NTH_DAY',
}

END_TIME_TYPE_ENUM= {
    'END_AFTER_OCCURENCES':'END_AFTER_OCCURENCES',
    'END_BY_TIME':'END_BY_TIME',
}

class PlcmSchedRecurrence(Plcm):
    content_type = "application/vnd.plcm.plcm-sched-recurrence+xml"
    root_element = "plcm-sched-recurrence"
    target_namespace = "urn:com:polycom:api:rest:plcm-sched-recurrence"
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-recur-daily',
        'urn:com:polycom:api:rest:plcm-recur-weekly',
        'urn:com:polycom:api:rest:plcm-recur-monthly',
        'urn:com:polycom:api:rest:plcm-recur-monthly-nth'
    ]
    element_properties={
        'plcm-recur-monthly-nth': { 'prop':'recur_monthly_nth', 'tag':'plcm-recur-monthly-nth','type':'urn:com:polycom:api:rest:plcm-recur-monthly-nth','class':PlcmRecurMonthlyNth },
        'plcm-recur-monthly' : { 'prop':'recur_monthly','tag':'plcm-recur-monthly','type':'urn:com:polycom:api:rest:plcm-recur-monthly','class':PlcmRecurMonthly }, 
        'plcm-recur-weekly' : { 'prop':'recur_weekly','tag':'plcm-recur-weekly','type':'urn:com:polycom:api:rest:plcm-recur-weekly','class':PlcmRecurWeekly },
        'plcm-recur-daily' : {'prop':'recur_daily','tag':'plcm-recur-daily','type':'urn:com:polycom:api:rest:plcm-recur-daily','class':PlcmRecurDaily },
        'sched-recurrence-type-enum' : {'prop':'sched_recurrence_type','tag':'sched-recurrence-type-enum', 'type':'enum', 'values':SCHED_RECURRENCE_TYPE_ENUM },
        'duration' : {'prop':'duration','tag':'duration'},
        'end-time-type-enum':{'prop':'end_time_type','tag':'end-time-type-enum', 'type':'enum', 'values':END_TIME_TYPE_ENUM},
        'occurrences':{'prop':'occurrences','tag':'occurrences'},
        'recur-start-time':{'prop':'recur_start_time','tag':'recur-start-time', 'type':'datetime'},
        'recur-end-time':{'prop':'recur_end_time','tag':'recur-end-time', 'type':'datetime'},
    }
    recur_monthly_nth=None
    recur_monthly=None
    recur_weekly=None
    recur_daily=None
    sched_recurrence_type=None
    duration=None
    end_time_type=None
    occurrences=None
    recur_start_time=None
    recur_end_time=None
    
    def __init__(self,
                 sched_recurrence_type=None,
                 duration=None,
                 end_time_type=None,
                 occurences=None,
                 recur_start_time=None,
                 recur_end_time=None,
                 ):
        self.sched_recurrence_type=sched_recurrence_type
        self.duration=duration
        self.end_time_type=end_time_type
        self.occurrences=occurences
        self.recur_start_time=recur_start_time
        self.recur_end_time=recur_end_time
        self.recur_daily=PlcmRecurDaily()
        self.recur_monthly=PlcmRecurMonthly()
        self.recur_monthly_nth=PlcmRecurMonthlyNth()
        self.recur_weekly=PlcmRecurWeekly()
        
    def xml_build_content(self, xml_root, nsmap=None):
        #Build xml attributes from properties
        xml_root = self.xml_build_from_properties(xml_root, xml_root.nsmap)
        return xml_root
    

SUPPORTED_LANGUAGE_ENUM = {
    'ENGLISH' : 'ENGLISH',
    'DEUTSCH' : 'DEUTSCH',
    'SPANISH' : 'SPANISH',
    'FRENCH' : 'FRENCH',
    'JAPANESE' : 'JAPANESE',
    'KOREAN' : 'KOREAN',
    'PORTUGESE' : 'PORTUGESE',
    'RUSSIAN' : 'RUSSIAN',
    'CHINESE' : 'CHINESE',
    'TAIWANESE' : 'TAIWANESE'
}
SCHEDULE_CONFERENCE_TYPE_ENUM = {
    'API_DMA_CONF' : 'API_DMA_CONF',
    'API_CMA_CONF' : 'API_CMA_CONF',
    'UI_DMA_CONF' : 'UI_DMA_CONF',
    'UI_CMA_CONF' : 'UI_CMA_CONF',
    'UI_DMA_ANYTIME_CONF' : 'UI_DMA_ANYTIME_CONF'
}
BRIDGE_SELECTION_TYPE_ENUM = {
    'AUTOBRIDGE' : 'AUTOBRIDGE',
    'SINGLEBRIDGE' : 'SINGLEBRIDGE',
    'MULTIBRIDGE' : 'MULTIBRIDGE',
    'SINGLEDMAPOOL' : 'SINGLEDMAPOOL',
    'MULTIDMAPOOL' : 'MULTIDMAPOOL'
}
CONFERENCE_RESERVE_TYPE_ENUM = {
    'SINGLE' : 'SINGLE',
    'RECURRING' : 'RECURRING'
}
(YEARLY,
 MONTHLY,
 WEEKLY,
 DAILY,
 HOURLY,
 MINUTELY,
 SECONDLY) = list(range(7))
_weekday_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

class PlcmReservation(Plcm):
    content_type = "application/vnd.plcm.plcm-reservation+xml"
    root_element = "plcm-reservation"
    target_namespace = "urn:com:polycom:api:rest:plcm-reservation"
    imported_namespaces = [
        'http://www.w3.org/2005/Atom',
        'urn:com:polycom:api:rest:plcm-reserved-participant-list',
        'urn:com:polycom:api:rest:plcm-sched-recurrence',
        'urn:com:polycom:api:rest:plcm-recur-daily',
        'urn:com:polycom:api:rest:plcm-recur-weekly',
        'urn:com:polycom:api:rest:plcm-recur-monthly',
        'urn:com:polycom:api:rest:plcm-recur-monthly-nth',
        'urn:com:polycom:api:rest:plcm-reserved-participant'
    ]
    element_properties={
        'plcm-sched-recurrence' : {'prop':'sched_recurrence','tag':'plcm-sched-recurrence','type':'urn:com:polycom:api:rest:plcm-sched-recurrence','class':PlcmSchedRecurrence},
        'name': { 'prop':'name', 'tag':'name' },
        'template-name' : { 'prop':'template_name','tag':'template-name' }, 
        'send-email' : { 'prop':'is_confirmed_by_email','tag':'send-email', 'type':'boolean' },
        'start-time' : {'prop':'start_time','tag':'start-time', 'type':'datetime' },
        'end-time' : {'prop':'end_time','tag':'end-time', 'type':'datetime' },
        'plcm-reserved-participant-list' : {'prop':'participants_list','tag':'plcm-reserved-participant-list','type':'urn:com:polycom:api:rest:plcm-reserved-participant-list','class':PlcmReservedParticipantList},
        'reservation-identifier':{'prop':'reservation_identifier','tag':'reservation-identifier'},
        'conf-passcode':{'prop':'conf_passcode','tag':'conf-passcode'},
        'chair-passcode':{'prop':'chair_passcode','tag':'chair-passcode'},
        'supported-language-enum':{'prop':'supported_language','tag':'supported-language-enum', 'type':'enum', 'values':SUPPORTED_LANGUAGE_ENUM},
        'dial-in-number':{'prop':'dial_in_number','tag':'dial-in-number'},
        'entity-tag':{'prop':'entity_tag','tag':'entity-tag'},
        'billing-code':{'prop':'billing_code','tag':'billing-code'},
        'schedule-conference-type-enum':{'prop':'schedule_conference_type','tag':'schedule-conference-type-enum', 'type':'enum', 'values':SCHEDULE_CONFERENCE_TYPE_ENUM},
        'bridge-selection-type-enum':{'prop':'bridge_selection_type','tag':'bridge-selection-type-enum', 'type':'enum', 'values':BRIDGE_SELECTION_TYPE_ENUM},
        'scheduled-mcu-ip':{'prop':'scheduled_mcu_ip','tag':'scheduled-mcu-ip'},
        'conference-reserve-type-enum':{'prop':'conference_reserve_type','tag':'conference-reserve-type-enum', 'type':'enum', 'values':CONFERENCE_RESERVE_TYPE_ENUM},
        'conference-id':{'prop':'conference_id','tag':'conference-id'},
        'vmr-room-id':{'prop':'vmr_room_id','tag':'vmr-room-id'},
        'recurrence-id':{'prop':'recurrence_id','tag':'recurrence-id'},
    }
    sched_recurrence=None
    name = None
    template_name = None
    is_confirmed_by_email = None
    start_time = None
    end_time = None
    participants_list = None
    reservation_identifier = None
    conf_passcode = None
    chair_passcode = None
    supported_language = None
    dial_in_number = None
    entity_tag = None
    billing_code = None
    schedule_conference_type = None
    bridge_selection_type = None
    scheduled_mcu_ip = None
    conference_reserve_type = None
    conference_id = None
    vmr_room_id = None
    recurrence_id = None
    
    def __init__(self, 
                 name=None,
                 start_time=None,
                 end_time=None,
                 template_name=None,
                 is_confirmed_by_email=False,
                 participants_list=None):
        self.name = name
        self.start_time = datetime.datetime.strptime(start_time,STRPTIME_UTC) if start_time != None else None
        self.end_time = datetime.datetime.strptime(end_time,STRPTIME_UTC) if end_time != None else None
        self.template_name = template_name
        self.is_confirmed_by_email = is_confirmed_by_email
        self.participants_list = PlcmReservedParticipantList()
        self.conference_reserve_type = CONFERENCE_RESERVE_TYPE_ENUM['SINGLE']
    
    def __str__(self):
        return "Resa> %s[%s->%s/%s]" % (self.name,self.start_time, self.end_time, self.template_name) 
    
    def xml_build_content(self, xml_root, nsmap=None):
        #Build xml attributes from properties
        xml_root = self.xml_build_from_properties(xml_root, xml_root.nsmap)
        #Add participants list
        #xml_root.append(self.plcm_participantslist.xml_build(build_nsmap=True,nsmap=xml_root.nsmap))
        return xml_root

    def add_participant(self,plcm_reservedparticipant):
        self.participants_list.add_participant(plcm_reservedparticipant)
        
    def set_start_end(self,start_time,end_time):
        self.start_time = datetime.datetime.strptime(start_time,STRPTIME_UTC)
        self.end_time = datetime.datetime.strptime(end_time,STRPTIME_UTC)
        
    def import_rrule(self,rrule):
        if self.start_time!=None and self.end_time!=None:
            try:
                sched = PlcmReservation.parse_rrule(rrule, self.start_time, (self.end_time-self.start_time).seconds)
                if sched!=None:
                    self.sched_recurrence = sched
                    self.conference_reserve_type = CONFERENCE_RESERVE_TYPE_ENUM['RECURRING']
                else:
                    raise Exception("Error parsing rrule %s " % rrule)
            except Exception,ex:
                print "[prpp][exception]%s" % ex
                raise ex
        else:
            raise Exception("Start time or end time is missing %s/%s" % (self.start_time,self.end_time))
        
    @staticmethod
    def parse_rrule(rrule,dtstart,duration):
        print("[prpp]parsing rrule %s %s %s " %(rrule,type(dtstart),duration))
        '''Parse a RRULE string FROM IB and returns an according PlcmSchedRecurrence'''
        if rrule!=None:
            parsed = rrulestr(rrule,dtstart=dtstart)
            print "[prpp]%s" % parsed.__dict__
            if parsed!=None:
                #Recurrence type
                if parsed._freq == MONTHLY:
                    sched_recurrence_type=SCHED_RECURRENCE_TYPE_ENUM['MONTHLY']
                elif parsed._freq == WEEKLY:
                    sched_recurrence_type=SCHED_RECURRENCE_TYPE_ENUM['WEEKLY']
                elif parsed._freq == DAILY:
                    sched_recurrence_type=SCHED_RECURRENCE_TYPE_ENUM['DAILY']
                else:
                    raise Exception("Unsupported RRULE type %s for %s" % (parsed._freq,rrule))
                #Number of occurences
                occurences = parsed._count
                
                #End types
                if parsed._until!=None:
                    end_time_type = END_TIME_TYPE_ENUM['END_BY_TIME']
                else:
                    end_time_type = END_TIME_TYPE_ENUM['END_AFTER_OCCURENCES']
                
                #Force timezone to UTC if naive date
                if dtstart.tzinfo==None:
                    dtstart.replace(tzinfo=utc)
                recur_start_time = dtstart
                recur_end_time = dtstart+relativedelta(seconds=duration)
                
                #recur_end_time = None

                sched_xml = PlcmSchedRecurrence(sched_recurrence_type, duration/60, end_time_type, occurences, recur_start_time, recur_end_time)
                if sched_recurrence_type == SCHED_RECURRENCE_TYPE_ENUM['MONTHLY']:
                    if PlcmReservation.check_attr(parsed._bynweekday):
                        sched_xml.sched_recurrence_type=SCHED_RECURRENCE_TYPE_ENUM['MONTHLY_NTH_DAY']
                        #Wich position in month
                        nmonthly = PlcmRecurMonthlyNth()
                        nmonthly.prefix_type = PlcmReservation.prefix_type_key(parsed._bynweekday[0][1])
                        nmonthly.day_type = PlcmReservation.day_type_key(parsed._bynweekday[0][0])
                        nmonthly.interval = parsed._interval
                        sched_xml.recur_monthly_nth = nmonthly
                    elif PlcmReservation.check_attr(parsed._bymonthday):
                        monthly = PlcmRecurMonthly()
                        monthly.day = parsed._bymonthday[0]
                        monthly.interval = parsed._interval
                        sched_xml.recur_monthly = monthly
                    #Old monthly format
                    elif PlcmReservation.check_attr(parsed._bysetpos) and PlcmReservation.check_attr(parsed._byweekday):
                        sched_xml.sched_recurrence_type=SCHED_RECURRENCE_TYPE_ENUM['MONTHLY_NTH_DAY']
                        #Wich position in month
                        nmonthly = PlcmRecurMonthlyNth()
                        nmonthly.prefix_type = PlcmReservation.prefix_type_key(parsed._bysetpos[0])
                        nmonthly.day_type = PlcmReservation.day_type_key(parsed._byweekday[0])
                        nmonthly.interval = parsed._interval
                        sched_xml.recur_monthly_nth = nmonthly
                        
                    '''elif self.check_attr(parsed._byweekday):
                        weekly = PlcmRecurWeekly
                        weekly.day_of_week_mask = PlcmReservation.daylist_to_mask(parsed._byweekday)
                        weekly.interval = parsed._interval
                        sched_xml.recur_monthly = monthly'''
                
                elif sched_recurrence_type == SCHED_RECURRENCE_TYPE_ENUM['WEEKLY']:
                    weekly = PlcmRecurWeekly()
                    weekly.day_of_week_mask = PlcmReservation.daylist_to_mask(parsed._byweekday)
                    weekly.interval = parsed._interval
                    sched_xml.recur_weekly = weekly
                    
                elif sched_recurrence_type == SCHED_RECURRENCE_TYPE_ENUM['DAILY']:
                    daily = PlcmRecurDaily()
                    daily.daily_type = DAILY_TYPE_ENUM['EVERY_N_DAY']
                    daily.interval = parsed._interval
                         
                    if PlcmReservation.check_attr(parsed._bymonthday) or PlcmReservation.check_attr(parsed._byweekno) or PlcmReservation.check_attr(parsed._bysetpos) or PlcmReservation.check_attr(parsed._bymonth) or PlcmReservation.check_attr(parsed._byyearday) or PlcmReservation.check_attr(parsed._bymonthday):
                        raise Exception("rrule format(DAILY) not supported by Polycom. rrule=%s/%s"%(rrule,parsed))
                     
                    sched_xml.recur_daily = daily
                else:
                    raise Exception("RRULE freq %s not implemented %s" %(sched_recurrence_type,rrule))
                
                return sched_xml
        else:
            raise Exception("rrule string is missing")
    
    @staticmethod
    def prefix_type_key(nweekday_pos):
        if nweekday_pos==1:
            return PREFIX_TYPE_ENUM['FIRST']
        elif nweekday_pos==2:
            return PREFIX_TYPE_ENUM['SECOND']
        elif nweekday_pos==3:
            return PREFIX_TYPE_ENUM['THIRD']
        elif nweekday_pos==4:
            return PREFIX_TYPE_ENUM['FOURTH']
        else:
            return PREFIX_TYPE_ENUM['LAST']
    
    @staticmethod
    def day_type_key(nweekday_day):
        if nweekday_day==0:
            return DAY_TYPE_ENUM['MONDAY']
        elif nweekday_day==1:
            return DAY_TYPE_ENUM['TUESDAY']
        elif nweekday_day==2:
            return DAY_TYPE_ENUM['WEDNESDAY']
        elif nweekday_day==3:
            return DAY_TYPE_ENUM['THURSDAY']
        elif nweekday_day==4:
            return DAY_TYPE_ENUM['FRIDAY']
        elif nweekday_day==5:
            return DAY_TYPE_ENUM['SATURDAY']
        elif nweekday_day==6:
            return DAY_TYPE_ENUM['SUNDAY']
        else:
            return DAILY_TYPE_ENUM['DAY']
    
    @staticmethod
    def check_attr(attribute):
        '''Return True if the attribute exists : different from None or empty list'''
        return not (attribute==None or len(attribute)==0)

    @staticmethod
    def daylist_to_mask(days):
        print "[prpp]days %s %s" % (type(days),days)
        mask = ['0'] * 7
        if isinstance(days, (int,long)):
            mask[days] = "1"
        elif isinstance(days, tuple):
            for day in days:
                mask[day] = "1"

        sunday = mask.pop()
        mask.insert(0,sunday)
        print "[prpp]mask:%s" % ''.join(mask)
        return ''.join(mask)
    
    def to_rrule(self,plcm_sched):
        if plcm_sched.sched_recurrence_type == SCHED_RECURRENCE_TYPE_ENUM['DAILY']:
            freq = DAILY
        elif plcm_sched.sched_recurrence_type == SCHED_RECURRENCE_TYPE_ENUM['WEEKLY']:
            freq = WEEKLY
        elif plcm_sched.sched_recurrence_type == SCHED_RECURRENCE_TYPE_ENUM['MONTHLY']:
            freq = MONTHLY
        elif plcm_sched.sched_recurrence_type == SCHED_RECURRENCE_TYPE_ENUM['MONTHLY_NTH_DAY']:
            freq = MONTHLY 
    
        rrule_new = rrule(freq)
        if plcm_sched.recur_daily.daily_type!=None:
            pass
        
        return rrule_new


class PlcmReservationList(Plcm):
    content_type = "application/vnd.plcm.plcm-reservation-list+xml"
    root_element = "plcm-reservation-list"
    target_namespace = "urn:com:polycom:api:rest:plcm-reservation-list"
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-reservation',
    ]
    element_properties={
        'plcm-reservation':{'prop':'plcm_reservations','tag':'plcm-reservation','type':'urn:com:polycom:api:rest:plcm-reservation','class':PlcmReservation,'list':True},
    }


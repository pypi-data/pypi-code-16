#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 5 févr. 2016

@author: Adrien
'''
from datetime import datetime
from dateutil.relativedelta import relativedelta
import traceback
from ..wrapper.request import PRPPRequest
from ..entities.utils import STRPTIME_UTC,STRFTIME, Utils
from ..wrapper.request import PRPPResponse
from ..stubs.plcmreservation import PlcmReservation, PlcmReservationList
from django.utils import timezone
from django.utils.timezone import utc

class Reservations(PRPPRequest):

    def __init__(self, server, path="reservations"):
        super(Reservations,self).__init__(server, path)

    def api_create_reservation(self, plcm_reservation):
        return self.post(plcm_reservation)
    
    def api_update_reservation(self, plcm_reservation):
        return self.put(plcm_reservation,extra_path=plcm_reservation.reservation_identifier)
    
    def api_list(self, start_time, end_time, recurrence_id=None):
        params={}
        params['start-time']=start_time
        params['end-time']=end_time
        if recurrence_id!=None:
            params['recurrence-id'] = recurrence_id
        return self.get(query_params=params)

    def api_get(self, reservation_identifier):
        """Loads one reservation with its identifier"""
        return self.get(extra_path=reservation_identifier)
    
    def api_delete_reservation(self, reservation_identifier):
        """Deletes the reservation associated with the identifier"""
        return self.delete(extra_path=reservation_identifier)

    def get_reservation(self,reservation_identifier):
        '''Retrieve one reservation using its identifier'''
        if reservation_identifier!=None:
            try:
                response = PRPPResponse(self.api_get(reservation_identifier),PlcmReservation,200,'get_reservation')
                if response.plcm_redirect != None:
                    response.load_plcm(self.api_get(response.plcm_redirect.split('/')[-1]), PlcmReservation, 200, 'get_reservation redirect')
                    
                response.is_done()
                return response
            except Exception,ex:
                print "[prpp][exception]%s" % ex
                raise ex
        else:
            raise Exception("reservation_identifier is missing")
    
    def list(self, start_time, end_time, recurrence_id=None):
        """Lists the reservations between start_time and end_time"""
        try:
            if type(start_time) == datetime:
                #Force timezone to UTC if naive date
                if start_time.tzinfo==None:
                    start_time= start_time.replace(tzinfo=utc)
                start_time = start_time.strftime(STRFTIME)
            if type(end_time) == datetime:
                #Force timezone to UTC if naive date
                if end_time.tzinfo==None:
                    end_time=end_time.replace(tzinfo=utc)
                end_time = end_time.strftime(STRFTIME)
            
            start_time = Utils.datetime_to_isoformat(start_time)
            end_time = Utils.datetime_to_isoformat(end_time)
            if start_time is None or end_time is None:
                raise Exception("[prpp] ERROR Time Format is bad %s %s" % (start_time,end_time))
            
            response = PRPPResponse(self.api_list(start_time,end_time,recurrence_id),PlcmReservationList,200,'reservations.list')
            response.is_done()
            return response
        except Exception,ex:
            print "[prpp][exception] reservations list %s" % ex
            raise ex
    
    def create_reservation(self,plcm_reservation, return_first=False):
        """Send a reservation creation request to the Polycom server"""
        #POST reservations
        if plcm_reservation!=None:
            try:
                response = PRPPResponse(self.api_create_reservation(plcm_reservation),
                                        PlcmReservation,
                                        201,
                                        'reservations.create',
                                        plcm_in=plcm_reservation,
                                        allow_empty_response=True)
                if response.plcm_redirect != None:
                    if '/' in response.plcm_redirect:
                        response.load_plcm(self.api_get(response.plcm_redirect.split('/')[-1]), PlcmReservation, 200, 'reservations.create redirect')
                    elif return_first==True:
                        #Recurrence-id is in response headers
                        reservations = self.list(start_time=plcm_reservation.start_time,
                                                      end_time=plcm_reservation.end_time,
                                                      recurrence_id=response.plcm_redirect)
                        reservations.plcm_redirect = response.plcm_redirect
                        response=reservations
                        #Response contains only first occurence
                response.is_done()
                return response
            except Exception,ex:
                traceback.print_exc()
                raise ex
        else:
            raise Exception("A PlcmReservation instance is needed")
    
    def update_reservation(self,plcm_reservation):
        """Send an reservation update request to the Polycom server"""
        #PUT reservations/reservation_identifier
        if plcm_reservation != None:
            if hasattr(plcm_reservation, 'reservation_identifier'):
                try:
                    if plcm_reservation.sched_recurrence!=None:
                        plcm_reservation.sched_recurrence.recur_start_time = plcm_reservation.start_time
                    response = PRPPResponse(self.api_update_reservation(plcm_reservation),
                                            PlcmReservation,
                                            204,
                                            'reservations.update',
                                            allow_empty_response=True,
                                            plcm_in=plcm_reservation)
                    if response.plcm_redirect != None:
                        response.load_plcm(self.api_get(response.plcm_redirect.split('/')[-1]), PlcmReservation, 200, 'reservations.update redirect')
                    response.is_done()
                    return response
                except Exception,ex:
                    print "[prpp][exception]%s" % ex
                    raise ex
            else:
                raise Exception("reservation_identifier of %s is missing" % plcm_reservation)
        else:
            raise Exception("Reservation instance is missing")
        
    def delete_reservation(self,plcm_reservation):
        '''Delete the reservation'''
        #DELETE reservations/reservation_identifier
        if plcm_reservation != None:
            if hasattr(plcm_reservation, 'reservation_identifier'):
                return self.delete_reservation_with_identifier(plcm_reservation.reservation_identifier)
            else:
                raise Exception("reservation_identifier of %s is missing" % plcm_reservation)
        else:
            raise Exception("Reservation is missing")
    
    def delete_reservation_with_identifier(self,reservation_identifier):
        '''Delete the reservation passed onto the RPRM'''
        if reservation_identifier!=None:
            try:
                response = PRPPResponse(self.api_delete_reservation(reservation_identifier),
                                        PlcmReservation,
                                        204,
                                        'reservations.delete',
                                        allow_empty_response=True)
                response.is_done()
                return response
            except Exception,ex:
                print "[prpp][exception]%s" % ex
                raise ex
        else:
            raise Exception("reservations_identifier is missing")
        
    def delete_reccurence_id(self,recurrence_id, date_after=None, reservation_ids = None):
        '''Delete all the reservations associated to the recurrence-id'''
        if recurrence_id!=None:
            if date_after==None:
                date_after=datetime.now()
            end = date_after+relativedelta(years=+2)
            try:
                if reservation_ids is None:
                    #First step:list the reservations for this recurrence_id : CAN BE LONG!
                    reservation_ids = []
                    response = self.list(date_after,end, recurrence_id)
                    if response.plcm_out!=None:
                        if hasattr(response.plcm_out, 'plcm_reservations'):
                            for resa in response.plcm_out.plcm_reservations:
                                reservation_ids.append(resa.reservation_identifier)
                        else:
                            print "[prpp] recurrence_id %s / no occurence to delete" % (recurrence_id)
                
                #Then delete the occurences
                nb_deleted = 0
                if reservation_ids is not None:
                    if len(reservation_ids) > 0:
                        for identifier in reservation_ids:
                            self.delete_reservation_with_identifier(identifier)
                            nb_deleted += 1
                        #Ok all the occurences are deleted
                        print "[prpp] recurrence_id %s / %s occurences deleted" % (recurrence_id,nb_deleted)
                    else:
                        print "[prpp] recurrence_id %s / no occurence to delete" % (recurrence_id)
                return True
            except Exception,ex:
                print "[prpp][exception]%s" % ex
        else:
            raise Exception("[prpp][exception]recurrence_id is missing")
        
    def update_recurrence_id(self,recurrence_id,plcm_reservation, reservation_ids=None):
        '''Updates a reccurent serie of occurences'''
        if recurrence_id!=None:
            if plcm_reservation!=None:
                #First step : we delete the existing serie
                are_deleted = self.delete_reccurence_id(recurrence_id, plcm_reservation.start_time,reservation_ids=reservation_ids)
                #Second step : we build the new serie
                if are_deleted==True:
                    plcm_reservation.reservation_identifier = None
                    plcm_reservation.recurrence_id = None
                    return self.create_reservation(plcm_reservation)
                else:
                    raise Exception("[prpp][exception]Can't delete all the occurences")
            else:
                raise Exception("[prpp][exception]Reservation instance is missing")
        else:
            raise Exception("[prpp][exception]recurrence_id is missing")

    def get_occurence(self,recurrence_id,occurence_number=None,occurence_date=None):
        '''Get an occurence of a recurrent serie, by its number or date : CAN BE LONG'''
        if recurrence_id!=None:
            if occurence_number!=None:
                #First step : we get the occurences
                resas = self.list(datetime.now()+relativedelta(years=-2), datetime.now()+relativedelta(years=+2), recurrence_id)
                #Second step : we find the occurence
                nb = 0
                if hasattr(resas.plcm_out,'plcm_reservations'):
                    for resa in resas.plcm_out.plcm_reservations:
                        nb += 1
                        if nb == occurence_number:
                            return resa
                raise Exception("[prpp][exception]occurence number not found %s > %s ? "%(occurence_number,nb))
            elif occurence_date!=None:
                #First step : we get the occurences
                resas = self.list(occurence_date, occurence_date+relativedelta(days=+2), recurrence_id)
                #Second step : we find the occurence
                for resa in resas.plcm_out.plcm_reservations:
                    diff = resa.start_time - occurence_date
                    print "[prpp] %s %s --> %s" % (resa.start_time, occurence_date, diff)
                    if diff.days == -1:
                        return resa
                raise Exception("[prpp][exception]occurence not found at date %s"%(occurence_date))
            else:
                raise Exception("[prpp][exception]occurence number or date are missing")
        else:
            raise Exception("[prpp][exception]recurrence_id is missing")






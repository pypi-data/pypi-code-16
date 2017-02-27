# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.SAW_QX
#
# Purpose
#    Test SAW.QX
#
# Revision Dates
#    30-Aug-2013 (CT) Creation
#    31-Jan-2014 (CT) Add test for `__{true,floor}div__`  to `_test_expr`
#     2-Apr-2014 (CT) Add/fix tests for `Q.NOT` and `~`
#     9-Sep-2014 (CT) Add tests for query with type restriction
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    31-Jul-2016 (CT) Factor `show_*` to `_SAW_test_functions`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW.__test__.model               import *
from   _GTW.__test__._SAW_test_functions import *

_test_columns = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_columns (apt, "PAP.Subject_has_Phone", Q.subject)
    QX.Kind_EPK PAP.Subject_has_Phone  :  Q.subject
      pap_subject_has_property.left

    >>> show_columns (apt, "PAP.Subject_has_Phone", Q.subject.pid)
    QX.Kind_EPK PAP.Subject_has_Phone  :  Q.subject.pid
      pap_subject_has_property.left

    >>> show_columns (apt, "PAP.Subject_has_Phone", Q.subject.electric)
    QX.Kind PAP.Subject_has_Phone  :  Q.subject.electric
      mom_id_entity__1.electric

    >>> show_columns (apt, "PAP.Subject_has_Phone", Q.subject.lifetime)
    QX.Kind_Partial PAP.Subject_has_Phone  :  Q.subject.lifetime

    >>> show_columns (apt, "PAP.Subject_has_Phone", Q.subject.lifetime.start)
    QX.Kind_Partial PAP.Subject_has_Phone  :  Q.subject.lifetime.start
      pap_company__1.lifetime__start
      pap_person__1.lifetime__start

    >>> show_columns (apt, "PAP.Person_has_Phone", Q.subject)
    QX.Kind_EPK PAP.Person_has_Phone  :  Q.subject
      pap_subject_has_property.left

    >>> show_columns (apt, "PAP.Person_has_Phone", Q.subject.pid)
    QX.Kind_EPK PAP.Person_has_Phone  :  Q.subject.pid
      pap_subject_has_property.left

    >>> show_columns (apt, "PAP.Person_has_Phone", Q.subject.electric)
    QX.Kind PAP.Person_has_Phone  :  Q.subject.electric
      mom_id_entity__4.electric

    >>> show_columns (apt, "PAP.Person_has_Phone", Q.subject.lifetime)
    QX.Kind_Composite PAP.Person_has_Phone  :  Q.subject.lifetime

    >>> show_columns (apt, "PAP.Person_has_Phone", Q.subject.lifetime.start)
    QX.Kind_Structured_Field_Extractor PAP.Person_has_Phone  :  Q.subject.lifetime.start
      pap_person__2.lifetime__start

    >>> show_columns (apt, "PAP.Subject", Q.phone_links)
    QX.Kind_Rev_Query PAP.Subject  :  Q.phone_links
      pap_subject_has_property__1.left

    >>> show_columns (apt, "PAP.Subject", Q.phone_links.phone)
    QX.Kind_EPK PAP.Subject  :  Q.phone_links.phone
      pap_subject_has_property__1.right

    >>> show_columns (apt, "PAP.Subject", Q.phone_links.phone.sn)
    QX.Kind PAP.Subject  :  Q.phone_links.phone.sn
      pap_phone__1.sn

    >>> show_columns (apt, "PAP.Subject", Q.phone_links.phone.sn == 42)
    QX.Bin PAP.Subject  :  Q.phone_links.phone.sn == 42
      pap_phone__1.sn

    >>> show_columns (apt, "PAP.Phone", Q.persons)
    QX.Kind_Rev_Query PAP.Phone  :  Q.persons
      pap_subject_has_property__2.left

    >>> show_columns (apt, "PAP.Phone", Q.persons.pid)
    QX.Kind_Rev_Query PAP.Phone  :  Q.persons.pid
      pap_subject_has_property__2.left

    >>> show_columns (apt, "PAP.Phone", Q.persons.lifetime)
    QX.Kind_Composite PAP.Phone  :  Q.persons.lifetime

    >>> show_columns (apt, "PAP.Phone", Q.persons.lifetime.start)
    QX.Kind_Structured_Field_Extractor PAP.Phone  :  Q.persons.lifetime.start
      pap_person__3.lifetime__start

    >>> show_columns (apt, "PAP.Subject", Q.creation.user == 42)
    QX.Bin PAP.Subject  :  Q.creation.user == 42
      mom_md_change__1.user

"""

_test_getters = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> ET  = apt ["PAP.Person"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxp = QX.Mapper (qrt)

    >>> show_qx (qxp (Q.lifetime))
    <MOM.Date_Interval_lifetime | QX.Kind_Composite for
        <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.lifetime.start))
    <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
        <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
            <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.RAW.lifetime))
    <MOM.Date_Interval_lifetime | QX.Kind_Composite for
        RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.lifetime.RAW))
    <MOM.Date_Interval_lifetime | QX.Kind_Composite for
        RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.RAW.lifetime.start))
    <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
        RAW <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
            RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.lifetime.RAW.start))
    <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
        RAW <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
            RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.lifetime.start.RAW))
    <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
        RAW <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
            RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.lifetime.start.year))
    <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
        <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
            <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>

    >>> show_qx (qxp (Q.accounts))
    <PAP.Person | QX.Kind_Rev_Query for
        <SAW : Role_Ref_Set `accounts`>>

    >>> show_qx (qxp (Q.accounts.name))
    <Auth.Account | QX.Kind for
         <SAW : Email `name` [auth_account__1.name]>>
        <PAP.Person | QX.Kind_Rev_Query for
             <SAW : Role_Ref_Set `accounts`>>

    >>> ET  = apt ["PAP.Person_has_Phone"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxh = QX.Mapper (qrt)

    >>> show_qx (qxh (Q.person))
    <PAP.Person_has_Phone | QX.Kind_EPK for
        <SAW : Person `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxh (Q.person.pid))
    <PAP.Person_has_Phone | QX.Kind_EPK for
        <SAW : Person `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxh (Q.person.last_name))
    <PAP.Person | QX.Kind for
         <SAW : String `last_name` [pap_person__1.last_name, pap_person__1.__raw_last_name]>>
        <PAP.Person_has_Phone | QX.Kind_EPK for
             <SAW : Person `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxh (Q.subject.lifetime))
    <MOM.Date_Interval_lifetime | QX.Kind_Composite for
         <SAW : Date_Interval `lifetime` [pap_person__1.lifetime__finish, pap_person__1.lifetime__start]>>
        <PAP.Person_has_Phone | QX.Kind_EPK for
             <SAW : Person `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxh (Q.subject.lifetime.alive))
    <MOM.Date_Interval_lifetime | QX.Kind_Query for
         <SAW : Boolean `lifetime.alive`>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
             <SAW : Date_Interval `lifetime` [pap_person__1.lifetime__finish, pap_person__1.lifetime__start]>>
            <PAP.Person_has_Phone | QX.Kind_EPK for
                 <SAW : Person `left` [pap_subject_has_property.left]>>
        :AND:
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_person__1.lifetime__start]>>
              None
            Bin:__le__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_person__1.lifetime__start]>>
              <<today>>
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_person__1.lifetime__finish]>>
              None
            Bin:__ge__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_person__1.lifetime__finish]>>
              <<today>>

    >>> ET  = apt ["Auth.Account"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxa = QX.Mapper (qrt)

    >>> show_qx (qxa (Q.person))
    <Auth.Account | QX.Kind_Rev_Query for
        <SAW : Role_Ref `person`>>

    >>> show_qx (qxa (Q.person.last_name))
    <PAP.Person | QX.Kind for
         <SAW : String `last_name` [pap_person__2.last_name, pap_person__2.__raw_last_name]>>
        <Auth.Account | QX.Kind_Rev_Query for
             <SAW : Role_Ref `person`>>

    >>> show_qx (qxa (Q.RAW.person.last_name))
    <PAP.Person | QX.Kind for
        RAW <SAW : String `last_name` [pap_person__2.last_name, pap_person__2.__raw_last_name]>>
        <Auth.Account | QX.Kind_Rev_Query for
            RAW <SAW : Role_Ref `person`>>

    >>> show_qx (qxa (Q.person.lifetime))
    <MOM.Date_Interval_lifetime | QX.Kind_Composite for
         <SAW : Date_Interval `lifetime` [pap_person__2.lifetime__finish, pap_person__2.lifetime__start]>>
        <Auth.Account | QX.Kind_Rev_Query for
             <SAW : Role_Ref `person`>>

    >>> show_qx (qxa (Q.person.lifetime.start))
    <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
         <SAW : Date `lifetime.start` [pap_person__2.lifetime__start]>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
             <SAW : Date_Interval `lifetime` [pap_person__2.lifetime__finish, pap_person__2.lifetime__start]>>
            <Auth.Account | QX.Kind_Rev_Query for
                 <SAW : Role_Ref `person`>>

    >>> show_qx (qxa (Q.person.account_links.account.name))
    <Auth.Account | QX.Kind for
         <SAW : Email `name` [auth_account__2.name]>>
        <PAP.Person_has_Account | QX.Kind_EPK for
             <SAW : Account `right` [pap_person_has_account__3.right]>>
            <PAP.Person | QX.Kind_Rev_Query for
                 <SAW : Link_Ref_List `account_links`>>
                <Auth.Account | QX.Kind_Rev_Query for
                     <SAW : Role_Ref `person`>>

    >>> show_qx (qxa (Q.person_links.person.last_name))
    <PAP.Person | QX.Kind for
         <SAW : String `last_name` [pap_person__3.last_name, pap_person__3.__raw_last_name]>>
        <PAP.Person_has_Account | QX.Kind_EPK for
             <SAW : Person `left` [pap_person_has_account__4.left]>>
            <Auth.Account | QX.Kind_Rev_Query for
                 <SAW : Link_Ref_List `person_links`>>

    >>> show_qx (qxa (Q.person_links.person.account_links.account.name))
    <Auth.Account | QX.Kind for
         <SAW : Email `name` [auth_account__3.name]>>
        <PAP.Person_has_Account | QX.Kind_EPK for
             <SAW : Account `right` [pap_person_has_account__5.right]>>
            <PAP.Person | QX.Kind_Rev_Query for
                 <SAW : Link_Ref_List `account_links`>>
                <PAP.Person_has_Account | QX.Kind_EPK for
                     <SAW : Person `left` [pap_person_has_account__4.left]>>
                    <Auth.Account | QX.Kind_Rev_Query for
                         <SAW : Link_Ref_List `person_links`>>

    >>> ET  = apt ["PAP.Subject_has_Phone"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxs = QX.Mapper (qrt)

    >>> x = qxs (Q.subject)
    >>> show_qx (x)
    <PAP.Subject_has_Phone | QX.Kind_EPK for
        <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxs (Q.creation.user == 42))
    Bin:__eq__:
      <MOM.MD_Change | QX.Kind_EPK for
           <SAW : Entity `user` [mom_md_change__1.user]>>
          <MOM.Id_Entity | QX.Kind_Rev_Query for
               <SAW : Rev_Ref `creation`>>
      42

    >>> x = qxs (Q.subject.lifetime)
    >>> show_qx (x)
    <PAP.Subject | QX.Kind_Partial for
         <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Composite for
           <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
          <PAP.Subject_has_Phone | QX.Kind_EPK for
               <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Composite for
           <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
          <PAP.Subject_has_Phone | QX.Kind_EPK for
               <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> x_start = qxs (Q.subject.lifetime.start)
    >>> show_qx (x_start)
    <PAP.Subject | QX.Kind_Partial for
         <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
           <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
               <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
           <SAW : Date `lifetime.start` [pap_person__4.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
               <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> x_raw_start = qxs (Q.RAW.subject.lifetime.start)
    >>> show_qx (x_raw_start)
    <PAP.Subject | QX.Kind_Partial for
        RAW <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
          RAW <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
              RAW <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
          RAW <SAW : Date `lifetime.start` [pap_person__4.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
              RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> x_start_raw = qxs (Q.subject.RAW.lifetime.start)
    >>> show_qx (x_start_raw)
    <PAP.Subject | QX.Kind_Partial for
        RAW <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
          RAW <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
              RAW <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
          RAW <SAW : Date `lifetime.start` [pap_person__4.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
              RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> x_start__raw = qxs (Q.subject.lifetime.start.RAW)
    >>> show_qx (x_start__raw)
    <PAP.Subject | QX.Kind_Partial for
        RAW <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
          RAW <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
              RAW <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
          RAW <SAW : Date `lifetime.start` [pap_person__4.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
              RAW <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> x_alive = qxs (Q.subject.lifetime.alive)
    >>> show_qx (x_alive)
    <PAP.Subject | QX.Kind_Partial for
         <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <MOM.Date_Interval_lifetime | QX.Kind_Query for
           <SAW : Boolean `lifetime.alive`>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
               <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>
          :AND:
            :OR:
              Bin:__eq__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
                None
              Bin:__le__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
                <<today>>
            :OR:
              Bin:__eq__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.finish` [pap_company__1.lifetime__finish]>>
                None
              Bin:__ge__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.finish` [pap_company__1.lifetime__finish]>>
                <<today>>
      <MOM.Date_Interval_lifetime | QX.Kind_Query for
           <SAW : Boolean `lifetime.alive`>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
               <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
              <PAP.Subject_has_Phone | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>
          :AND:
            :OR:
              Bin:__eq__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.start` [pap_person__4.lifetime__start]>>
                None
              Bin:__le__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.start` [pap_person__4.lifetime__start]>>
                <<today>>
            :OR:
              Bin:__eq__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.finish` [pap_person__4.lifetime__finish]>>
                None
              Bin:__ge__:
                <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                     <SAW : Date `lifetime.finish` [pap_person__4.lifetime__finish]>>
                <<today>>

    >>> x_creation = qxs (Q.subject.creation)
    >>> show_qx (x_creation)
    <MOM.Id_Entity | QX.Kind_Rev_Query for
        <SAW : Rev_Ref `creation`>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
            <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> ET  = apt ["MOM.MD_Change"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxc = QX.Mapper (qrt)

    >>> show_qx (qxc (Q.parent))
    <MOM.MD_Change | QX.Kind_Query for
         <SAW : Int `parent`>>
        <MOM.MD_Change | QX.Kind for
             <SAW : Int `parent_cid` [mom_md_change.parent_cid]>>
            <MOM.MD_Change | QX.Kind_Query for
                 <SAW : Int `parent`>>

    >>> show_qx (qxc (Q.type_name.CONTAINS ("Opti")))
    Call:contains:
      <MOM.MD_Change | QX.Kind for
           <SAW : String `type_name` [mom_md_change.type_name]>>

    >>> show_qx (qxc (Q.type_name.IN (('SRM.Regatta', 'SRM.Regatta_H', 'SRM.Regatta_C'))))
    Call:in_:
      <MOM.MD_Change | QX.Kind for
           <SAW : String `type_name` [mom_md_change.type_name]>>

    >>> ET  = apt ["SRM.Boat_in_Regatta"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxb = QX.Mapper (qrt)

    >>> show_qx (qxb (Q.regatta.boat_class.name))
    <SRM._Boat_Class_ | QX.Kind for
         <SAW : String `name` [srm__boat_class___1.name, srm__boat_class___1.__raw_name]>>
        <SRM.Regatta | QX.Kind_EPK for
             <SAW : Entity `boat_class` [srm_regatta__1.boat_class]>>
            <SRM.Boat_in_Regatta | QX.Kind_EPK for
                 <SAW : Regatta `right` [srm_boat_in_regatta.right]>>

    >>> show_qx (qxb (Q.left == Q.BVAR.this))
    Bin:__eq__:
      <SRM.Boat_in_Regatta | QX.Kind_EPK for
           <SAW : Boat `left` [srm_boat_in_regatta.left]>>
      BVAR:this:

    >>> ET  = apt ["SRM.Regatta"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxr = QX.Mapper (qrt)

    >>> ET.AQ.event.date.start.EQ ("2008")
    Q.left.date.start.between (datetime.date(2008, 1, 1), datetime.date(2008, 12, 31))

    >>> show_qx (qxr (ET.AQ.event.date.start.EQ ("2008")))
    Call:between:
      <MOM.Date_Interval_C | QX.Kind_Structured_Field_Extractor for
           <SAW : Date `date.start` [srm_regatta_event__1.date__start]>>
          <MOM.Date_Interval_C | QX.Kind_Composite for
               <SAW : Date_Interval `date` [srm_regatta_event__1.date__finish, srm_regatta_event__1.date__start]>>
              <SRM.Regatta | QX.Kind_EPK for
                   <SAW : Regatta_Event `left` [srm_regatta.left]>>

"""

_test_expr = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> ET  = apt ["PAP.Subject"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxs = QX.Mapper (qrt)

    >>> show_qx (qxs (Q.phone_links))
    <PAP.Subject | QX.Kind_Rev_Query for
         <SAW : Link_Ref_List `phone_links`>>

    >>> show_qx (qxs (Q.phone_links.phone))
    <PAP.Subject_has_Phone | QX.Kind_EPK for
         <SAW : Phone `right` [pap_subject_has_property__1.right]>>
        <PAP.Subject | QX.Kind_Rev_Query for
             <SAW : Link_Ref_List `phone_links`>>

    >>> show_qx (qxs (Q.phone_links.phone.sn == 42))
    Bin:__eq__:
      <PAP.Phone | QX.Kind for
           <SAW : Numeric_String `sn` [pap_phone__1.sn]>>
          <PAP.Subject_has_Phone | QX.Kind_EPK for
               <SAW : Phone `right` [pap_subject_has_property__1.right]>>
              <PAP.Subject | QX.Kind_Rev_Query for
                   <SAW : Link_Ref_List `phone_links`>>
      42

    >>> ET  = apt ["PAP.Person"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxp = QX.Mapper (qrt)

    >>> show_qx (qxp (Q.phone_links.phone.sn == 42))
    Bin:__eq__:
      <PAP.Phone | QX.Kind for
           <SAW : Numeric_String `sn` [pap_phone__2.sn]>>
          <PAP.Person_has_Phone | QX.Kind_EPK for
               <SAW : Phone `right` [pap_subject_has_property__2.right]>>
              <PAP.Person | QX.Kind_Rev_Query for
                   <SAW : Link_Ref_List `phone_links`>>
      42

    >>> show_qx (qxp (Q.lifetime.start.century))
    Traceback (most recent call last):
      ...
    AttributeError: century

    >>> show_qx (qxp (Q.lifetime.start.century + 3))
    Traceback (most recent call last):
      ...
    AttributeError: century

    >>> show_qx (qxp (Q.lifetime.start.year + 3))
    Bin:__add__:
      <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
           <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
          <MOM.Date_Interval_lifetime | QX.Kind_Composite for
               <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
      3

    >>> show_qx (qxp (- (Q.lifetime.start.year + 3)))
    Una:__neg__:
      Bin:__add__:
        <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
             <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
             <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                 <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
        3

    >>> show_qx (qxp (~ (Q.lifetime.alive)))
    Una:__not__:
      :AND:
        :OR:
          Bin:__eq__:
            <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                 <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
            None
          Bin:__le__:
            <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                 <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
            <<today>>
        :OR:
          Bin:__eq__:
            <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                 <SAW : Date `lifetime.finish` [pap_person.lifetime__finish]>>
            None
          Bin:__ge__:
            <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                 <SAW : Date `lifetime.finish` [pap_person.lifetime__finish]>>
            <<today>>

    >>> show_qx (qxp (Q.lifetime.start.year + 25 > Q.lifetime.finish.year - 2))
    Bin:__gt__:
      Bin:__add__:
        <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
             <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
             <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                 <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
        25
      Bin:__sub__:
        <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
             <SAW : Date `lifetime.finish` [pap_person.lifetime__finish]>>
             <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                 <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
        2

    >>> show_qx (qxp (Q.SUM (1)))
    _Aggr_:SUM:
      1

    >>> ET  = apt ["PAP.Phone"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxh = QX.Mapper (qrt)

    >>> show_qx (qxh (Q.persons))
    <PAP.Phone | QX.Kind_Rev_Query for
         <SAW : Role_Ref_Set `persons`>>

    >>> show_qx (qxh (Q.persons.pid))
    <PAP.Phone | QX.Kind_Rev_Query for
         <SAW : Role_Ref_Set `persons`>>

    >>> show_qx (qxh (Q.persons.lifetime))
    <MOM.Date_Interval_lifetime | QX.Kind_Composite for
         <SAW : Date_Interval `lifetime` [pap_person__1.lifetime__finish, pap_person__1.lifetime__start]>>
        <PAP.Phone | QX.Kind_Rev_Query for
             <SAW : Role_Ref_Set `persons`>>

    >>> show_qx (qxh (Q.persons.lifetime.start))
    <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
         <SAW : Date `lifetime.start` [pap_person__1.lifetime__start]>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
             <SAW : Date_Interval `lifetime` [pap_person__1.lifetime__finish, pap_person__1.lifetime__start]>>
            <PAP.Phone | QX.Kind_Rev_Query for
                 <SAW : Role_Ref_Set `persons`>>

    >>> ET  = apt ["PAP.Subject_has_Phone"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxs = QX.Mapper (qrt)

    >>> show_qx (qxs (~ (Q.subject.lifetime.alive)))
    <PAP.Subject | QX.Kind_Partial for
         <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      Una:__not__:
        :AND:
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
              None
            Bin:__le__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
              <<today>>
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_company__1.lifetime__finish]>>
              None
            Bin:__ge__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_company__1.lifetime__finish]>>
              <<today>>
      Una:__not__:
        :AND:
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_person__2.lifetime__start]>>
              None
            Bin:__le__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_person__2.lifetime__start]>>
              <<today>>
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_person__2.lifetime__finish]>>
              None
            Bin:__ge__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_person__2.lifetime__finish]>>
              <<today>>

    >>> show_qx (qxs (- (Q.subject.lifetime.start * 2)))
    <PAP.Subject | QX.Kind_Partial for
         <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      Una:__neg__:
        Bin:__mul__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2
      Una:__neg__:
        Bin:__mul__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.start` [pap_person__2.lifetime__start]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2

    >>> show_qx (qxs ((Q.subject.phones.sn * 2) - (Q.subject.lifetime.start )))
    <PAP.Subject | QX.Kind_Partial for
         <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      Bin:__sub__/r:
        <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
             <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
            <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                 <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
                <PAP.Subject_has_Phone | QX.Kind_EPK for
                     <SAW : Subject `left` [pap_subject_has_property.left]>>
        Bin:__mul__:
          <PAP.Phone | QX.Kind for
               <SAW : Numeric_String `sn` [pap_phone__3.sn]>>
              <PAP.Subject | QX.Kind_Rev_Query for
                   <SAW : Role_Ref_Set `phones`>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2
      Bin:__sub__/r:
        <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
             <SAW : Date `lifetime.start` [pap_person__2.lifetime__start]>>
            <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                 <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
                <PAP.Subject_has_Phone | QX.Kind_EPK for
                     <SAW : Subject `left` [pap_subject_has_property.left]>>
        Bin:__mul__:
          <PAP.Phone | QX.Kind for
               <SAW : Numeric_String `sn` [pap_phone__3.sn]>>
              <PAP.Subject | QX.Kind_Rev_Query for
                   <SAW : Role_Ref_Set `phones`>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2

    >>> show_qx (qxs ((Q.subject.lifetime.finish * 2) - (Q.subject.lifetime.start + 5)))
    <PAP.Subject | QX.Kind_Partial for
         <SAW : Date_Interval `lifetime` (PAP.Company | PAP.Person)>>
        <PAP.Subject_has_Phone | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      Bin:__sub__:
        Bin:__mul__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.finish` [pap_company__1.lifetime__finish]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2
        Bin:__add__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          5
      Bin:__sub__:
        Bin:__mul__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.finish` [pap_company__1.lifetime__finish]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2
        Bin:__add__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.start` [pap_person__2.lifetime__start]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          5
      Bin:__sub__:
        Bin:__mul__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.finish` [pap_person__2.lifetime__finish]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2
        Bin:__add__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.start` [pap_company__1.lifetime__start]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_company.lifetime__finish, pap_company.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          5
      Bin:__sub__:
        Bin:__mul__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.finish` [pap_person__2.lifetime__finish]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          2
        Bin:__add__:
          <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
               <SAW : Date `lifetime.start` [pap_person__2.lifetime__start]>>
              <MOM.Date_Interval_lifetime | QX.Kind_Composite for
                   <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
                  <PAP.Subject_has_Phone | QX.Kind_EPK for
                       <SAW : Subject `left` [pap_subject_has_property.left]>>
          5

    >>> ET  = apt ["SRM.Boat_in_Regatta"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxb = QX.Mapper (qrt)

    >>> show_qx (qxb (Q.regatta.boat_class.name.STARTSWITH ("O")))
    Call:startswith:
      <SRM._Boat_Class_ | QX.Kind for
           <SAW : String `name` [srm__boat_class___1.name, srm__boat_class___1.__raw_name]>>
          <SRM.Regatta | QX.Kind_EPK for
               <SAW : Entity `boat_class` [srm_regatta__1.boat_class]>>
              <SRM.Boat_in_Regatta | QX.Kind_EPK for
                   <SAW : Regatta `right` [srm_boat_in_regatta.right]>>

    >>> show_qx (qxb (Q.AND (Q.points > Q.place * Q.right.races, Q.RAW.boat.nation == "AUT")))
    :AND:
      Bin:__gt__:
        <SRM.Boat_in_Regatta | QX.Kind for
             <SAW : Int `points` [srm_boat_in_regatta.points]>>
        Bin:__mul__:
          <SRM.Boat_in_Regatta | QX.Kind for
               <SAW : Int `place` [srm_boat_in_regatta.place]>>
          <SRM.Regatta | QX.Kind for
               <SAW : Int `races` [srm_regatta__1.races]>>
              <SRM.Boat_in_Regatta | QX.Kind_EPK for
                   <SAW : Regatta `right` [srm_boat_in_regatta.right]>>
      Bin:__eq__:
        <SRM.Boat | QX.Kind for
            RAW <SAW : Nation `nation` [srm_boat__1.nation]>>
            <SRM.Boat_in_Regatta | QX.Kind_EPK for
                RAW <SAW : Boat `left` [srm_boat_in_regatta.left]>>
        AUT

    >>> show_qx (qxb (~ Q.AND (Q.points > Q.place * Q.right.races, Q.RAW.boat.nation == "AUT")))
    :OR:
      :NOT:
        Bin:__gt__:
          <SRM.Boat_in_Regatta | QX.Kind for
               <SAW : Int `points` [srm_boat_in_regatta.points]>>
          Bin:__mul__:
            <SRM.Boat_in_Regatta | QX.Kind for
                 <SAW : Int `place` [srm_boat_in_regatta.place]>>
            <SRM.Regatta | QX.Kind for
                 <SAW : Int `races` [srm_regatta__1.races]>>
                <SRM.Boat_in_Regatta | QX.Kind_EPK for
                     <SAW : Regatta `right` [srm_boat_in_regatta.right]>>
      :NOT:
        Bin:__eq__:
          <SRM.Boat | QX.Kind for
              RAW <SAW : Nation `nation` [srm_boat__1.nation]>>
              <SRM.Boat_in_Regatta | QX.Kind_EPK for
                  RAW <SAW : Boat `left` [srm_boat_in_regatta.left]>>
          AUT

    >>> show_qx (qxb (Q.points / Q.left.left.max_crew))
    Bin:__truediv__:
      <SRM.Boat_in_Regatta | QX.Kind for
           <SAW : Int `points` [srm_boat_in_regatta.points]>>
      <SRM.Boat_Class | QX.Kind for
           <SAW : Int `max_crew` [srm_boat_class__1.max_crew]>>
          <SRM.Boat | QX.Kind_EPK for
               <SAW : Boat_Class `left` [srm_boat__1.left]>>
              <SRM.Boat_in_Regatta | QX.Kind_EPK for
                   <SAW : Boat `left` [srm_boat_in_regatta.left]>>

    >>> show_qx (qxb (Q.points // Q.left.left.max_crew))
    Bin:__floordiv__:
      <SRM.Boat_in_Regatta | QX.Kind for
           <SAW : Int `points` [srm_boat_in_regatta.points]>>
      <SRM.Boat_Class | QX.Kind for
           <SAW : Int `max_crew` [srm_boat_class__1.max_crew]>>
          <SRM.Boat | QX.Kind_EPK for
               <SAW : Boat_Class `left` [srm_boat__1.left]>>
              <SRM.Boat_in_Regatta | QX.Kind_EPK for
                   <SAW : Boat `left` [srm_boat_in_regatta.left]>>

    >>> ET  = apt ["SRM.Regatta_C"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxc = QX.Mapper (qrt)

    >>> show_qx (qxc (Q.left.date.start.year == 2013))
    Bin:__eq__:
      <MOM.Date_Interval_C | QX.Kind_Structured_Field_Extractor for
           <SAW : Date `date.start` [srm_regatta_event__1.date__start]>>
          <MOM.Date_Interval_C | QX.Kind_Composite for
               <SAW : Date_Interval `date` [srm_regatta_event__1.date__finish, srm_regatta_event__1.date__start]>>
              <SRM.Regatta | QX.Kind_EPK for
                   <SAW : Regatta_Event `left` [srm_regatta.left]>>
      2013

    >>> ET  = apt ["PAP.Subject_has_Property"]
    >>> qrs = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxs = QX.Mapper (qrs)

    >>> show_qx (qxs (Q.left)) ### PAP.Subject_has_Property
    <PAP.Subject_has_Property | QX.Kind_EPK for
         <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxs (Q.left["PAP.Person"])) ### PAP.Subject_has_Property
    <PAP.Person | QX._Kind_EPK_Restricted_ for
         <SAW : Subject `left` [pap_subject_has_property.left]>>
        <PAP.Subject_has_Property | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxs (Q.left["PAP.Person"].last_name)) ### PAP.Subject_has_Property
    <PAP.Person | QX.Kind for
         <SAW : String `last_name` [pap_person.last_name, pap_person.__raw_last_name]>>
        <PAP.Person | QX._Kind_EPK_Restricted_ for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
            <PAP.Subject_has_Property | QX.Kind_EPK for
                 <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxs (Q.subject["PAP.Person"].lifetime)) ### PAP.Subject_has_Property
    <MOM.Date_Interval_lifetime | QX.Kind_Composite for
         <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
        <PAP.Person | QX._Kind_EPK_Restricted_ for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
            <PAP.Subject_has_Property | QX.Kind_EPK for
                 <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxs (Q.subject["PAP.Person"].lifetime.alive)) ### PAP.Subject_has_Property
    <MOM.Date_Interval_lifetime | QX.Kind_Query for
         <SAW : Boolean `lifetime.alive`>>
        <MOM.Date_Interval_lifetime | QX.Kind_Composite for
             <SAW : Date_Interval `lifetime` [pap_person.lifetime__finish, pap_person.lifetime__start]>>
            <PAP.Person | QX._Kind_EPK_Restricted_ for
                 <SAW : Subject `left` [pap_subject_has_property.left]>>
                <PAP.Subject_has_Property | QX.Kind_EPK for
                     <SAW : Subject `left` [pap_subject_has_property.left]>>
        :AND:
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
              None
            Bin:__le__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.start` [pap_person.lifetime__start]>>
              <<today>>
          :OR:
            Bin:__eq__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_person.lifetime__finish]>>
              None
            Bin:__ge__:
              <MOM.Date_Interval_lifetime | QX.Kind_Structured_Field_Extractor for
                   <SAW : Date `lifetime.finish` [pap_person.lifetime__finish]>>
              <<today>>

    >>> show_qx (qxs (Q.left["PAP.Legal_Entity"])) ### PAP.Subject_has_Property
    <PAP.Subject_has_Property | QX._Kind_Partial_Restricted_ for
         <SAW : Subject `left` [pap_subject_has_property.left]>>
        <PAP.Subject_has_Property | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <PAP.Company | QX._Kind_EPK_Restricted_ for
           <SAW : Subject `left` [pap_subject_has_property.left]>>
          <PAP.Subject_has_Property | QX.Kind_EPK for
               <SAW : Subject `left` [pap_subject_has_property.left]>>

    >>> show_qx (qxs (Q.left["PAP.Legal_Entity"].name)) ### PAP.Subject_has_Property
    <PAP.Subject_has_Property | QX._Kind_Partial_Restricted_ for
         <SAW : Subject `left` [pap_subject_has_property.left]>>
        <PAP.Subject_has_Property | QX.Kind_EPK for
             <SAW : Subject `left` [pap_subject_has_property.left]>>
      <PAP.Company | QX.Kind for
           <SAW : String `name` [pap_company__2.name, pap_company__2.__raw_name]>>
          <PAP.Company | QX._Kind_EPK_Restricted_ for
               <SAW : Subject `left` [pap_subject_has_property.left]>>
              <PAP.Subject_has_Property | QX.Kind_EPK for
                   <SAW : Subject `left` [pap_subject_has_property.left]>>

"""

_test_joins = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_joins (apt, "PAP.Subject", Q.creation.user == 42)
    PAP.Subject  :  Q.creation.user == 42
      OUTER mom_md_change__1.pid = mom_id_entity.pid

    >>> show_joins (apt, "PAP.Subject_has_Phone", Q.subject)
    PAP.Subject_has_Phone  :  Q.subject

    >>> show_joins (apt, "PAP.Subject_has_Phone", Q.subject.pid)
    PAP.Subject_has_Phone  :  Q.subject.pid

    >>> show_joins (apt, "PAP.Subject_has_Phone", Q.subject.electric)
    PAP.Subject_has_Phone  :  Q.subject.electric
      OUTER pap_subject_has_property.pid = pap_subject_has_phone.pid
      OUTER mom_id_entity__1.pid = pap_subject_has_property.left

    >>> show_joins (apt, "PAP.Subject_has_Phone", Q.subject.lifetime)
    PAP.Subject_has_Phone  :  Q.subject.lifetime
      OUTER pap_subject_has_property.pid = pap_subject_has_phone.pid
      OUTER mom_id_entity__1.pid = pap_subject_has_property.left

    >>> show_joins (apt, "PAP.Subject_has_Phone", Q.subject.lifetime.start)
    PAP.Subject_has_Phone  :  Q.subject.lifetime.start
      OUTER pap_subject_has_property.pid = pap_subject_has_phone.pid
      OUTER mom_id_entity__1.pid = pap_subject_has_property.left
      OUTER pap_company__1.pid = pap_subject_has_property.left
      OUTER pap_person__1.pid = pap_subject_has_property.left

    >>> show_joins (apt, "PAP.Person_has_Phone", Q.subject)
    PAP.Person_has_Phone  :  Q.subject

    >>> show_joins (apt, "PAP.Person_has_Phone", Q.subject.pid)
    PAP.Person_has_Phone  :  Q.subject.pid

    >>> show_joins (apt, "PAP.Person_has_Phone", Q.subject.electric)
    PAP.Person_has_Phone  :  Q.subject.electric
      JOIN  pap_subject_has_property.pid = pap_subject_has_phone.pid
      JOIN  pap_person__2.pid = pap_subject_has_property.left
      JOIN  mom_id_entity__4.pid = pap_subject_has_property.left

    >>> show_joins (apt, "PAP.Person_has_Phone", Q.subject.lifetime)
    PAP.Person_has_Phone  :  Q.subject.lifetime
      JOIN  pap_subject_has_property.pid = pap_subject_has_phone.pid
      JOIN  pap_person__2.pid = pap_subject_has_property.left

    >>> show_joins (apt, "PAP.Person_has_Phone", Q.subject.lifetime.start)
    PAP.Person_has_Phone  :  Q.subject.lifetime.start
      JOIN  pap_subject_has_property.pid = pap_subject_has_phone.pid
      JOIN  pap_person__2.pid = pap_subject_has_property.left

    >>> show_joins (apt, "Auth.Account", Q.person)
    Auth.Account  :  Q.person
      OUTER pap_person_has_account__1.right = auth_account.pid
      OUTER pap_person__3.pid = pap_person_has_account__1.left

    >>> show_joins (apt, "Auth.Account", Q.person.lifetime == ("2013-07-15", ))
    Auth.Account  :  Q.person.lifetime == ('2013-07-15',)
      OUTER pap_person_has_account__1.right = auth_account.pid
      OUTER pap_person__3.pid = pap_person_has_account__1.left

    >>> show_joins (apt, "Auth.Account", Q.person.lifetime.start == "2013-07-15")
    Auth.Account  :  Q.person.lifetime.start == '2013-07-15'
      OUTER pap_person_has_account__1.right = auth_account.pid
      OUTER pap_person__3.pid = pap_person_has_account__1.left

    >>> show_joins (apt, "Auth.Account", Q.person.account_links.account.name)
    Auth.Account  :  Q.person.account_links.account.name
      OUTER pap_person_has_account__1.right = auth_account.pid
      OUTER pap_person__3.pid = pap_person_has_account__1.left
      OUTER pap_person_has_account__2.left = pap_person__3.pid
      JOIN  auth_account__1.pid = pap_person_has_account__2.right

    >>> show_joins (apt, "Auth.Account", Q.person_links.person.account_links.account.name)
    Auth.Account  :  Q.person_links.person.account_links.account.name
      OUTER pap_person_has_account__3.right = auth_account.pid
      JOIN  pap_person__4.pid = pap_person_has_account__3.left
      OUTER pap_person_has_account__4.left = pap_person__4.pid
      JOIN  auth_account__2.pid = pap_person_has_account__4.right

    >>> show_joins (apt, "SRM.Regatta_C", Q.left.date.start.year == 2013)
    SRM.Regatta_C  :  Q.left.date.start.year == 2013
      JOIN  srm_regatta_event__1.pid = srm_regatta.left

"""

_test_xs_filter = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_xs_filter (apt, "Auth.Account", Q.person_links.person.account_links.account.name == "foo")
    Auth.Account  :  Q.person_links.person.account_links.account.name == 'foo'
        auth_account__1.name = :name_1

    >>> show_xs_filter (apt, "Auth.Account", Q.person_links.person.account_links.account.name)
    Auth.Account  :  Q.person_links.person.account_links.account.name
        auth_account__1.name != :name_1

    >>> show_xs_filter (apt, "Auth.Account", ~ Q.person_links.person.account_links.account.name)
    Auth.Account  :  ~ Q.person_links.person.account_links.account.name
        auth_account__1.name = :name_1

    >>> show_xs_filter (apt, "Auth.Account", Q.RAW.person.last_name == "Tanzer")
    Auth.Account  :  Q.RAW.person.last_name == 'Tanzer'
        pap_person__2.__raw_last_name = :__raw_last_name_1

    >>> show_xs_filter (apt, "PAP.Subject_has_Phone", Q.subject.pid == 42)
    PAP.Subject_has_Phone  :  Q.subject.pid == 42
        pap_subject_has_property."left" = :left_1

    >>> show_xs_filter (apt, "PAP.Subject_has_Phone", Q.subject.lifetime == ("2000-01-02", "2000-07-23"))
    PAP.Subject_has_Phone  :  Q.subject.lifetime == ('2000-01-02', '2000-07-23')
        pap_company__1.lifetime__start = :lifetime__start_1 AND pap_company__1.lifetime__finish = :lifetime__finish_1 OR pap_person__3.lifetime__start = :lifetime__start_2 AND pap_person__3.lifetime__finish = :lifetime__finish_2

    >>> show_xs_filter (apt, "PAP.Subject_has_Phone", Q.subject.lifetime == Q.creation.time)
    PAP.Subject_has_Phone  :  Q.subject.lifetime == Q.creation.time
        mom_md_change__1.kind = :kind_1 AND pap_company__1.lifetime__start = mom_md_change__1.time OR mom_md_change__1.kind = :kind_1 AND pap_person__3.lifetime__start = mom_md_change__1.time

    >>> show_xs_filter (apt, "PAP.Subject_has_Phone", Q.subject.lifetime.start == "2000-01-02")
    PAP.Subject_has_Phone  :  Q.subject.lifetime.start == '2000-01-02'
        pap_company__1.lifetime__start = :lifetime__start_1 OR pap_person__3.lifetime__start = :lifetime__start_2

    >>> show_xs_filter (apt, "PAP.Subject_has_Phone", Q.creation.time == "2013-09-11")
    PAP.Subject_has_Phone  :  Q.creation.time == '2013-09-11'
        mom_md_change__1.kind = :kind_1 AND mom_md_change__1.time = :time_1

    >>> show_xs_filter (apt, "PAP.Subject_has_Phone", Q.subject.phone_links.phone.creation.time == "2013-09-11")
    PAP.Subject_has_Phone  :  Q.subject.phone_links.phone.creation.time == '2013-09-11'
        mom_md_change__2.kind = :kind_1 AND mom_md_change__2.time = :time_1

    >>> show_xs_filter (apt, "PAP.Subject", Q.creation.user == 42)
    PAP.Subject  :  Q.creation.user == 42
        mom_md_change__1.kind = :kind_1 AND mom_md_change__1."user" = :user_1

    >>> show_xs_filter (apt, "PAP.Subject", Q.phone_links.phone.creation.time == "2013-09-11")
    PAP.Subject  :  Q.phone_links.phone.creation.time == '2013-09-11'
        mom_md_change__3.kind = :kind_1 AND mom_md_change__3.time = :time_1

    >>> show_xs_filter (apt, "PAP.Person", Q.phone_links.phone.creation.time == "2013-09-11")
    PAP.Person  :  Q.phone_links.phone.creation.time == '2013-09-11'
        mom_md_change__4.kind = :kind_1 AND mom_md_change__4.time = :time_1

    >>> show_xs_filter (apt, "PAP.Person", Q.RAW.lifetime.start == "2010-01-01")
    PAP.Person  :  Q.RAW.lifetime.start == '2010-01-01'
        pap_person.lifetime__start = :lifetime__start_1

    >>> ET  = apt ["SRM.Regatta"]
    >>> show_xs_filter (apt, "SRM.Regatta", ET.AQ.event.date.start.EQ ("2008"))
    SRM.Regatta  :  Q.left.date.start.between (datetime.date(2008, 1, 1), datetime.date(2008, 12, 31))
        srm_regatta_event__1.date__start IS NOT NULL AND srm_regatta_event__1.date__start >= :date__start_1 AND srm_regatta_event__1.date__start <= :date__start_2

    >>> show_xs_filter (apt, "SRM.Regatta_C", Q.left.date.alive)
    SRM.Regatta_C  :  Q.left.date.alive
        (srm_regatta_event__1.date__start IS NULL OR srm_regatta_event__1.date__start <= :date__start_1) AND (srm_regatta_event__1.date__finish IS NULL OR srm_regatta_event__1.date__finish >= :date__finish_1)

    >>> show_xs_filter (apt, "SRM.Regatta_C", Q.event.date.start.D.YEAR (2010))
    SRM.Regatta_C  :  Q.event.date.start.between (datetime.date(2010, 1, 1), datetime.date(2010, 12, 31))
        srm_regatta_event__1.date__start IS NOT NULL AND srm_regatta_event__1.date__start >= :date__start_1 AND srm_regatta_event__1.date__start <= :date__start_2

"""

_test_xs_filter_pg = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_xs_filter (apt, "SRM.Regatta_C", Q.event.date.start.year == 2010)
    SRM.Regatta_C  :  Q.event.date.start.year == 2010
        EXTRACT(year FROM srm_regatta_event__1.date__start) = :param_1

"""

_test_xs_filter_sq = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> show_xs_filter (apt, "SRM.Regatta_C", Q.event.date.start.year == 2010)
    SRM.Regatta_C  :  Q.event.date.start.year == 2010
        CAST(strftime(:strftime_1, srm_regatta_event__1.date__start) AS INTEGER) = :param_1

"""

_test_debug = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> ET = apt ["SRM.Boat"]
    >>> qrt = apt.DBW.PNS.Q_Result.E_Type (ET, _strict = False)
    >>> qxp = QX.Mapper (qrt)

    >>> qf = ET.sail_number.Q_Raw.AC ("11") ### SRM.Boat

    >>> print (qf)
    Q.__raw_sail_number.startswith ('11',)

    >>> show_qx (qxp (qf))

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_columns   = _test_columns
        , test_expr      = _test_expr
        , test_getters   = _test_getters
        , test_joins     = _test_joins
        , test_xs_filter = _test_xs_filter
        )
    , ignore = ("HPS", )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( test_xs_filter_pg = _test_xs_filter_pg
            )
        , ignore = ("HPS", "MYS", "SQL", "sq")
        )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( test_xs_filter_sq = _test_xs_filter_sq
            )
        , ignore = ("HPS", "MYS", "POS", "pg")
        )
    )

X__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_debug     = _test_debug
        )
    )

### __END__ GTW.__test__.SAW_QX

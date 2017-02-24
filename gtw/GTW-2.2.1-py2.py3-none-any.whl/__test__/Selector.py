# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Selector
#
# Purpose
#    Test MOM.Selector
#
# Revision Dates
#     1-Jun-2016 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW.__test__.model               import *
from   _GTW.__test__._SAW_test_functions import show_esf_query, show_query
from   _GTW.__test__.Test_Command        import esf_completer

from   _MOM.import_MOM                   import Q

from   _TFL.pyk                          import pyk

import _GTW._OMP._PAP.Adhoc_Group
import _GTW._OMP._PAP.Company_1P
import _GTW._OMP._PAP.Subject_has_VAT_IDN
import _GTW._OMP._PAP.Company_has_VAT_IDN
import _GTW._OMP._PAP.Person_has_VAT_IDN
import _GTW._OMP._PAP.Person_in_Group

import _GTW.Request_Data

_test_main = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> EVT = scope.EVT
    >>> PAP = scope.PAP
    >>> SWP = scope.SWP

    >>> print (PAP.Person.ES.recursive_repr ())
    <Selector.Entity_N for <PAP.Person.AQ> for PAP.Person>
      <Selector.Atom for last_name>
      <Selector.Atom for first_name>
      <Selector.Atom for middle_name>
      <Selector.Atom for title>

    >>> PAP.Person.ES ["middle_name"]
    <Selector.Atom for middle_name>

    >>> print (PAP.Company.ES.recursive_repr ())
    <Selector.Entity_PS for <PAP.Company.AQ> for PAP.Company>
      <Selector.Atom for name>
      <Selector.Atom for registered_in>

    >>> print (PAP.Company_1P.ES.recursive_repr ())
    <Selector.Entity_N for <PAP.Company_1P.AQ> for PAP.Company_1P>
      <Selector.Atom for person.last_name>
      <Selector.Atom for person.first_name>
      <Selector.Atom for person.middle_name>
      <Selector.Atom for person.title>
      <Selector.Atom for name>
      <Selector.Atom for registered_in>

    >>> with expect_except (KeyError) : # doctest:+ELLIPSIS
    ...     PAP.Company_1P.ES ["person"]
    KeyError: ...

    >>> PAP.Company_1P.ES ["person.last_name"]
    <Selector.Atom for person.last_name>

    >>> print (PAP.Subject.ES.recursive_repr ())
    <Selector.Entity_P for <PAP.Subject.AQ> for PAP.Subject>
      <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Adhoc_Group>
        <Selector.Atom for name>
      <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company>
        <Selector.Atom for name>
        <Selector.Atom for registered_in>
      <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
        <Selector.Atom for person.last_name>
        <Selector.Atom for person.first_name>
        <Selector.Atom for person.middle_name>
        <Selector.Atom for person.title>
        <Selector.Atom for name>
        <Selector.Atom for registered_in>
      <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person>
        <Selector.Atom for last_name>
        <Selector.Atom for first_name>
        <Selector.Atom for middle_name>
        <Selector.Atom for title>

    >>> for l, e in PAP.Subject.ES.level_elements () :
    ...      print ("  " * l, repr (e), repr (e.root))
     <Selector.Entity_P for <PAP.Subject.AQ> for PAP.Subject> <Selector.Entity_P for <PAP.Subject.AQ> for PAP.Subject>
       <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Adhoc_Group> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Adhoc_Group>
         <Selector.Atom for name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Adhoc_Group>
       <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company>
         <Selector.Atom for name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company>
         <Selector.Atom for registered_in> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company>
       <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
         <Selector.Atom for person.last_name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
         <Selector.Atom for person.first_name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
         <Selector.Atom for person.middle_name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
         <Selector.Atom for person.title> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
         <Selector.Atom for name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
         <Selector.Atom for registered_in> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Company_1P>
       <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person>
         <Selector.Atom for last_name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person>
         <Selector.Atom for first_name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person>
         <Selector.Atom for middle_name> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person>
         <Selector.Atom for title> <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person>

    >>> PAP.Subject.ES ["[PAP.Person]"]
    <Selector.Entity_P_CNP for <PAP.Subject.AQ> for PAP.Person>

    >>> PAP.Subject.ES ["[PAP.Person].first_name"]
    <Selector.Atom for first_name>

    >>> print (PAP.Person_in_Group.ES.recursive_repr ())
    <Selector.Entity_PS for <PAP.Person_in_Group.AQ> for PAP.Person_in_Group>
      <Selector.Entity_N for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Person>
        <Selector.Atom for left.last_name>
        <Selector.Atom for left.first_name>
        <Selector.Atom for left.middle_name>
        <Selector.Atom for left.title>
      <Selector.Entity_P for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Group>
        <Selector.Entity_P_CNP for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Adhoc_Group>
          <Selector.Atom for right[PAP.Adhoc_Group].name>
        <Selector.Entity_P_CNP for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
          <Selector.Atom for right[PAP.Company].name>
          <Selector.Atom for right[PAP.Company].registered_in>
        <Selector.Entity_P_CNP for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P>
          <Selector.Atom for right[PAP.Company_1P].person.last_name>
          <Selector.Atom for right[PAP.Company_1P].person.first_name>
          <Selector.Atom for right[PAP.Company_1P].person.middle_name>
          <Selector.Atom for right[PAP.Company_1P].person.title>
          <Selector.Atom for right[PAP.Company_1P].name>
          <Selector.Atom for right[PAP.Company_1P].registered_in>

    >>> PAP.Person_in_Group.ES ["left"]
    <Selector.Entity_N for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Person>

    >>> PAP.Person_in_Group.ES ["right"]
    <Selector.Entity_P for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Group>

    >>> PAP.Person_in_Group.ES ["right[PAP.Adhoc_Group].name"]
    <Selector.Atom for right[PAP.Adhoc_Group].name>

    >>> PAP.Person_in_Group.ES ["right['PAP.Adhoc_Group']name"]
    <Selector.Atom for right[PAP.Adhoc_Group].name>

    >>> print (PAP.Person_has_VAT_IDN.ES.recursive_repr ())
    <Selector.Entity_N for <PAP.Person_has_VAT_IDN.AQ> for PAP.Person_has_VAT_IDN>
      <Selector.Atom for left.last_name>
      <Selector.Atom for left.first_name>
      <Selector.Atom for left.middle_name>
      <Selector.Atom for left.title>
      <Selector.Atom for vin>

    >>> PAP.Person_has_VAT_IDN.ES ["left.last_name"]
    <Selector.Atom for left.last_name>

    >>> print (PAP.Company_has_VAT_IDN.ES.recursive_repr ())
    <Selector.Entity_PS for <PAP.Company_has_VAT_IDN.AQ> for PAP.Company_has_VAT_IDN>
      <Selector.Entity_PS for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
        <Selector.Atom for left.name>
        <Selector.Atom for left.registered_in>
      <Selector.Atom for vin>

    >>> PAP.Company_has_VAT_IDN.ES ["left.name"]
    <Selector.Atom for left.name>

    >>> print (PAP.Subject_has_VAT_IDN.ES.recursive_repr ())
    <Selector.Entity_PS for <PAP.Subject_has_VAT_IDN.AQ> for PAP.Subject_has_VAT_IDN>
      <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Subject>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
          <Selector.Atom for left[PAP.Company].name>
          <Selector.Atom for left[PAP.Company].registered_in>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Person>
          <Selector.Atom for left[PAP.Person].last_name>
          <Selector.Atom for left[PAP.Person].first_name>
          <Selector.Atom for left[PAP.Person].middle_name>
          <Selector.Atom for left[PAP.Person].title>
      <Selector.Atom for vin>

    >>> PAP.Subject_has_VAT_IDN.ES ["left[PAP.Company].name"]
    <Selector.Atom for left[PAP.Company].name>

    >>> PAP.Subject_has_VAT_IDN.ES ["left[PAP.Person].title"]
    <Selector.Atom for left[PAP.Person].title>

    >>> PAP.Subject_has_VAT_IDN.ES ["vin"]
    <Selector.Atom for vin>

    >>> print (PAP.Subject_has_Property.ES.recursive_repr ())
    <Selector.Entity_P for <PAP.Subject_has_Property.AQ> for PAP.Subject_has_Property>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Address>
        <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
            <Selector.Atom for left[PAP.Company].name>
            <Selector.Atom for left[PAP.Company].registered_in>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P>
            <Selector.Atom for left[PAP.Company_1P].person.last_name>
            <Selector.Atom for left[PAP.Company_1P].person.first_name>
            <Selector.Atom for left[PAP.Company_1P].person.middle_name>
            <Selector.Atom for left[PAP.Company_1P].person.title>
            <Selector.Atom for left[PAP.Company_1P].name>
            <Selector.Atom for left[PAP.Company_1P].registered_in>
        <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Address>
          <Selector.Atom for right.street>
          <Selector.Atom for right.zip>
          <Selector.Atom for right.city>
          <Selector.Atom for right.country>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Email>
        <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
            <Selector.Atom for left[PAP.Company].name>
            <Selector.Atom for left[PAP.Company].registered_in>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P>
            <Selector.Atom for left[PAP.Company_1P].person.last_name>
            <Selector.Atom for left[PAP.Company_1P].person.first_name>
            <Selector.Atom for left[PAP.Company_1P].person.middle_name>
            <Selector.Atom for left[PAP.Company_1P].person.title>
            <Selector.Atom for left[PAP.Company_1P].name>
            <Selector.Atom for left[PAP.Company_1P].registered_in>
        <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Email>
          <Selector.Atom for right.address>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Phone>
        <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
            <Selector.Atom for left[PAP.Company].name>
            <Selector.Atom for left[PAP.Company].registered_in>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P>
            <Selector.Atom for left[PAP.Company_1P].person.last_name>
            <Selector.Atom for left[PAP.Company_1P].person.first_name>
            <Selector.Atom for left[PAP.Company_1P].person.middle_name>
            <Selector.Atom for left[PAP.Company_1P].person.title>
            <Selector.Atom for left[PAP.Company_1P].name>
            <Selector.Atom for left[PAP.Company_1P].registered_in>
        <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Phone>
          <Selector.Atom for right.sn>
          <Selector.Atom for right.ndc>
          <Selector.Atom for right.cc>
        <Selector.Atom for extension>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Url>
        <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company>
            <Selector.Atom for left[PAP.Company].name>
            <Selector.Atom for left[PAP.Company].registered_in>
          <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P>
            <Selector.Atom for left[PAP.Company_1P].person.last_name>
            <Selector.Atom for left[PAP.Company_1P].person.first_name>
            <Selector.Atom for left[PAP.Company_1P].person.middle_name>
            <Selector.Atom for left[PAP.Company_1P].person.title>
            <Selector.Atom for left[PAP.Company_1P].name>
            <Selector.Atom for left[PAP.Company_1P].registered_in>
        <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Url>
          <Selector.Atom for right.value>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Address>
        <Selector.Atom for left.last_name>
        <Selector.Atom for left.first_name>
        <Selector.Atom for left.middle_name>
        <Selector.Atom for left.title>
        <Selector.Atom for right.street>
        <Selector.Atom for right.zip>
        <Selector.Atom for right.city>
        <Selector.Atom for right.country>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Email>
        <Selector.Atom for left.last_name>
        <Selector.Atom for left.first_name>
        <Selector.Atom for left.middle_name>
        <Selector.Atom for left.title>
        <Selector.Atom for right.address>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Phone>
        <Selector.Atom for left.last_name>
        <Selector.Atom for left.first_name>
        <Selector.Atom for left.middle_name>
        <Selector.Atom for left.title>
        <Selector.Atom for right.sn>
        <Selector.Atom for right.ndc>
        <Selector.Atom for right.cc>
        <Selector.Atom for extension>
      <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Url>
        <Selector.Atom for left.last_name>
        <Selector.Atom for left.first_name>
        <Selector.Atom for left.middle_name>
        <Selector.Atom for left.title>
        <Selector.Atom for right.value>

    >>> PAP.Subject_has_Property.ES ["[PAP.Company_has_Url]"]
    <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Url>

    >>> PAP.Subject_has_Property.ES ["[PAP.Company_has_Url]"] ["left[PAP.Company_1P].person.title"]
    <Selector.Atom for left[PAP.Company_1P].person.title>

    >>> PAP.Subject_has_Property.ES ["[PAP.Company_has_Url]left[PAP.Company_1P].person.title"]
    <Selector.Atom for left[PAP.Company_1P].person.title>

    >>> PAP.Subject_has_Property.ES ["[PAP.Company_has_Url].left[PAP.Company_1P].person.title"]
    <Selector.Atom for left[PAP.Company_1P].person.title>

    >>> PAP.Subject_has_Property.ES ["[PAP.Company_has_Url].right"]
    <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Url>

    >>> PAP.Subject_has_Property.ES ["[PAP.Company_has_Url].right.value"]
    <Selector.Atom for right.value>

    >>> for l, e in PAP.Subject_has_VAT_IDN.ES.level_elements () :
    ...      print ("  " * l, repr (e), e.macro_name)
     <Selector.Entity_PS for <PAP.Subject_has_VAT_IDN.AQ> for PAP.Subject_has_VAT_IDN> do_entity_ps
       <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Subject> do_entity_p
         <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p_cnp
           <Selector.Atom for left[PAP.Company].name> do_atom
           <Selector.Atom for left[PAP.Company].registered_in> do_atom
         <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Person> do_entity_p_cnp
           <Selector.Atom for left[PAP.Person].last_name> do_atom
           <Selector.Atom for left[PAP.Person].first_name> do_atom
           <Selector.Atom for left[PAP.Person].middle_name> do_atom
           <Selector.Atom for left[PAP.Person].title> do_atom
       <Selector.Atom for vin> do_atom

    >>> for l, e in PAP.Subject_has_Property.ES.level_elements () :
    ...      print ("  " * l, repr (e), e.macro_name)
     <Selector.Entity_P for <PAP.Subject_has_Property.AQ> for PAP.Subject_has_Property> do_entity_p
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Address> do_entity_p_cnp
         <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company].name> do_atom
             <Selector.Atom for left[PAP.Company].registered_in> do_atom
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company_1P].person.last_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.first_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.middle_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.title> do_atom
             <Selector.Atom for left[PAP.Company_1P].name> do_atom
             <Selector.Atom for left[PAP.Company_1P].registered_in> do_atom
         <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Address> do_entity_n
           <Selector.Atom for right.street> do_atom
           <Selector.Atom for right.zip> do_atom
           <Selector.Atom for right.city> do_atom
           <Selector.Atom for right.country> do_atom
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Email> do_entity_p_cnp
         <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company].name> do_atom
             <Selector.Atom for left[PAP.Company].registered_in> do_atom
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company_1P].person.last_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.first_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.middle_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.title> do_atom
             <Selector.Atom for left[PAP.Company_1P].name> do_atom
             <Selector.Atom for left[PAP.Company_1P].registered_in> do_atom
         <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Email> do_entity_n
           <Selector.Atom for right.address> do_atom
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Phone> do_entity_p_cnp
         <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company].name> do_atom
             <Selector.Atom for left[PAP.Company].registered_in> do_atom
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company_1P].person.last_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.first_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.middle_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.title> do_atom
             <Selector.Atom for left[PAP.Company_1P].name> do_atom
             <Selector.Atom for left[PAP.Company_1P].registered_in> do_atom
         <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Phone> do_entity_n
           <Selector.Atom for right.sn> do_atom
           <Selector.Atom for right.ndc> do_atom
           <Selector.Atom for right.cc> do_atom
         <Selector.Atom for extension> do_atom
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Company_has_Url> do_entity_p_cnp
         <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company].name> do_atom
             <Selector.Atom for left[PAP.Company].registered_in> do_atom
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for PAP.Company_1P> do_entity_p_cnp
             <Selector.Atom for left[PAP.Company_1P].person.last_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.first_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.middle_name> do_atom
             <Selector.Atom for left[PAP.Company_1P].person.title> do_atom
             <Selector.Atom for left[PAP.Company_1P].name> do_atom
             <Selector.Atom for left[PAP.Company_1P].registered_in> do_atom
         <Selector.Entity_N for <right.AQ [Attr.Type.Querier Id_Entity]> for PAP.Url> do_entity_n
           <Selector.Atom for right.value> do_atom
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Address> do_entity_p_cnp
         <Selector.Atom for left.last_name> do_atom
         <Selector.Atom for left.first_name> do_atom
         <Selector.Atom for left.middle_name> do_atom
         <Selector.Atom for left.title> do_atom
         <Selector.Atom for right.street> do_atom
         <Selector.Atom for right.zip> do_atom
         <Selector.Atom for right.city> do_atom
         <Selector.Atom for right.country> do_atom
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Email> do_entity_p_cnp
         <Selector.Atom for left.last_name> do_atom
         <Selector.Atom for left.first_name> do_atom
         <Selector.Atom for left.middle_name> do_atom
         <Selector.Atom for left.title> do_atom
         <Selector.Atom for right.address> do_atom
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Phone> do_entity_p_cnp
         <Selector.Atom for left.last_name> do_atom
         <Selector.Atom for left.first_name> do_atom
         <Selector.Atom for left.middle_name> do_atom
         <Selector.Atom for left.title> do_atom
         <Selector.Atom for right.sn> do_atom
         <Selector.Atom for right.ndc> do_atom
         <Selector.Atom for right.cc> do_atom
         <Selector.Atom for extension> do_atom
       <Selector.Entity_P_CNP for <PAP.Subject_has_Property.AQ> for PAP.Person_has_Url> do_entity_p_cnp
         <Selector.Atom for left.last_name> do_atom
         <Selector.Atom for left.first_name> do_atom
         <Selector.Atom for left.middle_name> do_atom
         <Selector.Atom for left.title> do_atom
         <Selector.Atom for right.value> do_atom

    >>> for l, e in EVT.Event.AQ.left.ESW.level_elements () :
    ...      print ("  " * l, repr (e), "id =", e.id, ", ui_name =", e.ui_name)
     <Selector.Entity_P for <MOM.Id_Entity.AQ> for MOM.Id_Entity> id =  , ui_name = Id_Entity
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for PAP.Adhoc_Group> id = [PAP.Adhoc_Group] , ui_name = Id_Entity[Adhoc_Group]
         <Selector.Atom for name> id = [PAP.Adhoc_Group]name , ui_name = Name
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for PAP.Company> id = [PAP.Company] , ui_name = Id_Entity[Company]
         <Selector.Atom for name> id = [PAP.Company]name , ui_name = Name
         <Selector.Atom for registered_in> id = [PAP.Company]registered_in , ui_name = Registered in
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for PAP.Company_1P> id = [PAP.Company_1P] , ui_name = Id_Entity[Company_1P]
         <Selector.Atom for person.last_name> id = [PAP.Company_1P]person.last_name , ui_name = Person/Last name
         <Selector.Atom for person.first_name> id = [PAP.Company_1P]person.first_name , ui_name = Person/First name
         <Selector.Atom for person.middle_name> id = [PAP.Company_1P]person.middle_name , ui_name = Person/Middle name
         <Selector.Atom for person.title> id = [PAP.Company_1P]person.title , ui_name = Person/Academic title
         <Selector.Atom for name> id = [PAP.Company_1P]name , ui_name = Name
         <Selector.Atom for registered_in> id = [PAP.Company_1P]registered_in , ui_name = Registered in
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for PAP.Person> id = [PAP.Person] , ui_name = Id_Entity[Person]
         <Selector.Atom for last_name> id = [PAP.Person]last_name , ui_name = Last name
         <Selector.Atom for first_name> id = [PAP.Person]first_name , ui_name = First name
         <Selector.Atom for middle_name> id = [PAP.Person]middle_name , ui_name = Middle name
         <Selector.Atom for title> id = [PAP.Person]title , ui_name = Academic title
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SRM.Page> id = [SRM.Page] , ui_name = Id_Entity[Regatta_Page]
         <Selector.Atom for perma_name> id = [SRM.Page]perma_name , ui_name = Name
         <Selector.Atom for event.name> id = [SRM.Page]event.name , ui_name = Event/Name
         <Selector.Atom for event.date.start> id = [SRM.Page]event.date.start , ui_name = Event/Date/Start
         <Selector.Atom for event.date.finish> id = [SRM.Page]event.date.finish , ui_name = Event/Date/Finish
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SRM.Regatta_C> id = [SRM.Regatta_C] , ui_name = Id_Entity[Regatta_C]
         <Selector.Atom for left.name> id = [SRM.Regatta_C]left.name , ui_name = Event/Name
         <Selector.Atom for left.date.start> id = [SRM.Regatta_C]left.date.start , ui_name = Event/Date/Start
         <Selector.Atom for left.date.finish> id = [SRM.Regatta_C]left.date.finish , ui_name = Event/Date/Finish
         <Selector.Atom for boat_class.name> id = [SRM.Regatta_C]boat_class.name , ui_name = Boat class/Name
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SRM.Regatta_Event> id = [SRM.Regatta_Event] , ui_name = Id_Entity[Regatta_Event]
         <Selector.Atom for name> id = [SRM.Regatta_Event]name , ui_name = Name
         <Selector.Atom for date.start> id = [SRM.Regatta_Event]date.start , ui_name = Date/Start
         <Selector.Atom for date.finish> id = [SRM.Regatta_Event]date.finish , ui_name = Date/Finish
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SRM.Regatta_H> id = [SRM.Regatta_H] , ui_name = Id_Entity[Regatta_H]
         <Selector.Atom for left.name> id = [SRM.Regatta_H]left.name , ui_name = Event/Name
         <Selector.Atom for left.date.start> id = [SRM.Regatta_H]left.date.start , ui_name = Event/Date/Start
         <Selector.Atom for left.date.finish> id = [SRM.Regatta_H]left.date.finish , ui_name = Event/Date/Finish
         <Selector.Atom for boat_class.name> id = [SRM.Regatta_H]boat_class.name , ui_name = Handicap/Name
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SWP.Clip_O> id = [SWP.Clip_O] , ui_name = Id_Entity[Clip_O]
         <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Object_PN> id = [SWP.Clip_O]left , ui_name = Object_PN
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SRM.Page> id = [SWP.Clip_O]left , ui_name = Object_PN[Regatta_Page]
             <Selector.Atom for left[SRM.Page].perma_name> id = [SWP.Clip_O]left[SRM.Page].perma_name , ui_name = Object[Regatta_Page]/Name
             <Selector.Atom for left[SRM.Page].event.name> id = [SWP.Clip_O]left[SRM.Page].event.name , ui_name = Object[Regatta_Page]/Event/Name
             <Selector.Atom for left[SRM.Page].event.date.start> id = [SWP.Clip_O]left[SRM.Page].event.date.start , ui_name = Object[Regatta_Page]/Event/Date/Start
             <Selector.Atom for left[SRM.Page].event.date.finish> id = [SWP.Clip_O]left[SRM.Page].event.date.finish , ui_name = Object[Regatta_Page]/Event/Date/Finish
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Clip_X> id = [SWP.Clip_O]left , ui_name = Object_PN[Clip_X]
             <Selector.Atom for left[SWP.Clip_X].perma_name> id = [SWP.Clip_O]left[SWP.Clip_X].perma_name , ui_name = Object[Clip_X]/Name
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Gallery> id = [SWP.Clip_O]left , ui_name = Object_PN[Gallery]
             <Selector.Atom for left[SWP.Gallery].perma_name> id = [SWP.Clip_O]left[SWP.Gallery].perma_name , ui_name = Object[Gallery]/Name
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Page> id = [SWP.Clip_O]left , ui_name = Object_PN[Page]
             <Selector.Atom for left[SWP.Page].perma_name> id = [SWP.Clip_O]left[SWP.Page].perma_name , ui_name = Object[Page]/Name
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Page_Y> id = [SWP.Clip_O]left , ui_name = Object_PN[Page_Y]
             <Selector.Atom for left[SWP.Page_Y].perma_name> id = [SWP.Clip_O]left[SWP.Page_Y].perma_name , ui_name = Object[Page_Y]/Name
             <Selector.Atom for left[SWP.Page_Y].year> id = [SWP.Clip_O]left[SWP.Page_Y].year , ui_name = Object[Page_Y]/Year
           <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Referral> id = [SWP.Clip_O]left , ui_name = Object_PN[Referral]
             <Selector.Atom for left[SWP.Referral].parent_url> id = [SWP.Clip_O]left[SWP.Referral].parent_url , ui_name = Object[Referral]/Parent url
             <Selector.Atom for left[SWP.Referral].perma_name> id = [SWP.Clip_O]left[SWP.Referral].perma_name , ui_name = Object[Referral]/Name
         <Selector.Atom for date_x.start> id = [SWP.Clip_O]date_x.start , ui_name = date/Start
         <Selector.Atom for date_x.finish> id = [SWP.Clip_O]date_x.finish , ui_name = date/Finish
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SWP.Clip_X> id = [SWP.Clip_X] , ui_name = Id_Entity[Clip_X]
         <Selector.Atom for perma_name> id = [SWP.Clip_X]perma_name , ui_name = Name
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SWP.Gallery> id = [SWP.Gallery] , ui_name = Id_Entity[Gallery]
         <Selector.Atom for perma_name> id = [SWP.Gallery]perma_name , ui_name = Name
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SWP.Page> id = [SWP.Page] , ui_name = Id_Entity[Page]
         <Selector.Atom for perma_name> id = [SWP.Page]perma_name , ui_name = Name
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SWP.Page_Y> id = [SWP.Page_Y] , ui_name = Id_Entity[Page_Y]
         <Selector.Atom for perma_name> id = [SWP.Page_Y]perma_name , ui_name = Name
         <Selector.Atom for year> id = [SWP.Page_Y]year , ui_name = Year
       <Selector.Entity_P_CNP for <MOM.Id_Entity.AQ> for SWP.Referral> id = [SWP.Referral] , ui_name = Id_Entity[Referral]
         <Selector.Atom for parent_url> id = [SWP.Referral]parent_url , ui_name = Parent url
         <Selector.Atom for perma_name> id = [SWP.Referral]perma_name , ui_name = Name

    >>> print (SWP.Clip_O.ES.recursive_repr ())
    <Selector.Entity_PS for <SWP.Clip_O.AQ> for SWP.Clip_O>
      <Selector.Entity_P for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Object_PN>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SRM.Page>
          <Selector.Atom for left[SRM.Page].perma_name>
          <Selector.Atom for left[SRM.Page].event.name>
          <Selector.Atom for left[SRM.Page].event.date.start>
          <Selector.Atom for left[SRM.Page].event.date.finish>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Clip_X>
          <Selector.Atom for left[SWP.Clip_X].perma_name>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Gallery>
          <Selector.Atom for left[SWP.Gallery].perma_name>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Page>
          <Selector.Atom for left[SWP.Page].perma_name>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Page_Y>
          <Selector.Atom for left[SWP.Page_Y].perma_name>
          <Selector.Atom for left[SWP.Page_Y].year>
        <Selector.Entity_P_CNP for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Referral>
          <Selector.Atom for left[SWP.Referral].parent_url>
          <Selector.Atom for left[SWP.Referral].perma_name>
      <Selector.Atom for date_x.start>
      <Selector.Atom for date_x.finish>


"""

_test_query = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> EVT = scope.EVT
    >>> PAP = scope.PAP
    >>> SWP = scope.SWP
    >>> ct  = PAP.Person     ("Tanzer", "Christian", "", "Mag.", raw = True)
    >>> ctc = PAP.Company_1P (person = ct)
    >>> evt = EVT.Event      (ctc, ("1988-01-15", ), raw = True)
    >>> p1  = SWP.Page       ("event-1-text", text = "Text for the 1. event", raw = True)
    >>> cl1 = SWP.Clip_O     (p1, abstract = "Test clip", raw = True)
    >>> ctp = PAP.Person_has_Phone   (ct, PAP.Phone ("43", "1", "234567", raw = True))
    >>> _   = PAP.Person_has_VAT_IDN (ct, vin = "ATU38931901", raw = True)

    >>> c_PhA_t = esf_completer (scope, PAP.Person_has_Account.AQ.left, "title", "Mag" )
    >>> prepr (c_PhA_t.attr_selectors)
    {'title' : 'Mag'}
    >>> prepr (c_PhA_t.e_type_selectors)
    {}
    >>> prepr (c_PhA_t.filters_q)
    [Q.title.startswith ('mag',)]
    >>> prepr (c_PhA_t.names)
    ('title', 'last_name', 'first_name', 'middle_name')

    >>> c_PhA_l = esf_completer (scope, PAP.Person_has_Account.AQ.left, "last_name", "Tan" )
    >>> prepr (c_PhA_l.attr_selectors)
    {'last_name' : 'Tan'}
    >>> prepr (c_PhA_l.e_type_selectors)
    {}
    >>> prepr (c_PhA_l.filters_q)
    [<Filter_Or [Q.last_name.startswith ('tan',), Q.last_name.contains ('-tan',)]>]
    >>> prepr (c_PhA_l.names)
    ('last_name', 'first_name', 'middle_name', 'title')

    >>> show_query (c_PhA_l.query ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_person.__raw_first_name AS pap_person___raw_first_name,
           pap_person.__raw_last_name AS pap_person___raw_last_name,
           pap_person.__raw_middle_name AS pap_person___raw_middle_name,
           pap_person.__raw_title AS pap_person___raw_title,
           pap_person.first_name AS pap_person_first_name,
           pap_person.last_name AS pap_person_last_name,
           pap_person.lifetime__finish AS pap_person_lifetime__finish,
           pap_person.lifetime__start AS pap_person_lifetime__start,
           pap_person.middle_name AS pap_person_middle_name,
           pap_person.pid AS pap_person_pid,
           pap_person.sex AS pap_person_sex,
           pap_person.title AS pap_person_title
         FROM mom_id_entity
           JOIN pap_person ON mom_id_entity.pid = pap_person.pid
         WHERE (pap_person.last_name LIKE :last_name_1 || '%%%%')
            OR (pap_person.last_name LIKE '%%%%' || :last_name_2 || '%%%%')
    Parameters:
         last_name_1          : 'tan'
         last_name_2          : '-tan'

    >>> c_ShP_l_p_l = esf_completer \
    ...     ( scope, PAP.Subject_has_Phone.AQ.left
    ...     , "[PAP.Company_1P].person.last_name", "Tan"
    ...     , dict (E_Type_NP = "PAP.Company_1P")
    ...     )
    >>> prepr (c_ShP_l_p_l.attr_selectors)
    {'[PAP.Company_1P]person.last_name' : 'Tan'}
    >>> prepr (c_ShP_l_p_l.e_type_selectors)
    {'E_Type_NP' : 'PAP.Company_1P'}
    >>> prepr (c_ShP_l_p_l.filters_q)
    [<Filter_Or [Q.person.last_name.startswith ('tan',), Q.person.last_name.contains ('-tan',)]>]
    >>> print (formatted (c_ShP_l_p_l.names))
    ( '[PAP.Company_1P]person.last_name'
    , '[PAP.Company_1P]person.first_name'
    , '[PAP.Company_1P]person.middle_name'
    , '[PAP.Company_1P]person.title'
    , '[PAP.Company_1P]name'
    , '[PAP.Company_1P]registered_in'
    )

    >>> print (formatted (c_ShP_l_p_l.query ().all ()))
    [PAP.Company_1P (('tanzer', 'christian', '', 'mag.'), 'tanzer christian, mag.', '')]

    >>> print (formatted (c_ShP_l_p_l.instance (ctc).values))
    { '[PAP.Company_1P]' : 'Tanzer Christian, Mag.'
    , '[PAP.Company_1P]name' : 'Tanzer Christian, Mag.'
    , '[PAP.Company_1P]person.first_name' : 'Christian'
    , '[PAP.Company_1P]person.last_name' : 'Tanzer'
    , '[PAP.Company_1P]person.title' : 'Mag.'
    }

    >>> c_ShP_p_l = esf_completer \
    ...     ( scope, PAP.Subject_has_Phone.AQ.left
    ...     , "[PAP.Person].last_name", "Tan"
    ...     , dict (E_Type_NP = "PAP.Person")
    ...     )
    >>> prepr (c_ShP_p_l.attr_selectors)
    {'[PAP.Person]last_name' : 'Tan'}
    >>> prepr (c_ShP_p_l.e_type_selectors)
    {'E_Type_NP' : 'PAP.Person'}
    >>> prepr (c_ShP_p_l.filters_q)
    [<Filter_Or [Q.last_name.startswith ('tan',), Q.last_name.contains ('-tan',)]>]
    >>> print (formatted (c_ShP_p_l.names))
    ( '[PAP.Person]last_name'
    , '[PAP.Person]first_name'
    , '[PAP.Person]middle_name'
    , '[PAP.Person]title'
    )

    >>> print (formatted (c_ShP_p_l.query ().all ()))
    [PAP.Person ('tanzer', 'christian', '', 'mag.')]

    >>> print (formatted (c_ShP_p_l.instance (ct).values))
    { '[PAP.Person]' : 'Tanzer Christian, Mag.'
    , '[PAP.Person]first_name' : 'Christian'
    , '[PAP.Person]last_name' : 'Tanzer'
    , '[PAP.Person]title' : 'Mag.'
    }

    >>> c_ShP_l_p_t = esf_completer \
    ...     ( scope, PAP.Subject_has_Phone.AQ.left
    ...     , "[PAP.Company_1P].person.title", "Ing"
    ...     , dict (E_Type_NP = "PAP.Company_1P")
    ...     )
    >>> prepr (c_ShP_l_p_t.attr_selectors)
    {'[PAP.Company_1P]person.title' : 'Ing'}
    >>> prepr (c_ShP_l_p_t.e_type_selectors)
    {'E_Type_NP' : 'PAP.Company_1P'}
    >>> prepr (c_ShP_l_p_t.filters_q)
    [Q.person.title.startswith ('ing',)]
    >>> print (formatted (c_ShP_l_p_t.names))
    ( '[PAP.Company_1P]person.title'
    , '[PAP.Company_1P]person.last_name'
    , '[PAP.Company_1P]person.first_name'
    , '[PAP.Company_1P]person.middle_name'
    , '[PAP.Company_1P]name'
    , '[PAP.Company_1P]registered_in'
    )

    >>> print (formatted (c_ShP_l_p_t.query ().all ()))
    []

    >>> show_query (c_ShP_l_p_l.query ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_company.__raw_name AS pap_company___raw_name,
           pap_company.__raw_registered_in AS pap_company___raw_registered_in,
           pap_company.__raw_short_name AS pap_company___raw_short_name,
           pap_company.lifetime__finish AS pap_company_lifetime__finish,
           pap_company.lifetime__start AS pap_company_lifetime__start,
           pap_company.name AS pap_company_name,
           pap_company.pid AS pap_company_pid,
           pap_company.registered_in AS pap_company_registered_in,
           pap_company.short_name AS pap_company_short_name,
           pap_company_1p.person AS pap_company_1p_person,
           pap_company_1p.pid AS pap_company_1p_pid
         FROM mom_id_entity
           JOIN pap_company ON mom_id_entity.pid = pap_company.pid
           JOIN pap_company_1p ON pap_company.pid = pap_company_1p.pid
           LEFT OUTER JOIN pap_person AS pap_person__1 ON pap_person__1.pid = pap_company_1p.person
         WHERE (pap_person__1.last_name LIKE :last_name_1 || '%%%%')
            OR (pap_person__1.last_name LIKE '%%%%' || :last_name_2 || '%%%%')
    Parameters:
         last_name_1          : 'tan'
         last_name_2          : '-tan'

    >>> c_ShP_r_sn = esf_completer \
    ...     ( scope, PAP.Subject_has_Phone.AQ.right
    ...     , "sn", "234"
    ...     )
    >>> prepr (c_ShP_r_sn.attr_selectors)
    {'sn' : '234'}
    >>> prepr (c_ShP_r_sn.e_type_selectors)
    {}
    >>> prepr (c_ShP_r_sn.filters_q)
    [Q.sn.startswith ('234',)]
    >>> prepr (c_ShP_r_sn.names)
    ('sn', 'ndc', 'cc')

    >>> print (formatted (c_ShP_r_sn.query ().all ()))
    [PAP.Phone ('43', '1', '234567')]

    >>> print (c_ShP_r_sn.instance (ctc).recursive_repr ())
    <Selector.Instance for <PAP.Phone.AQ> for PAP.Phone = (('tanzer', 'christian', '', 'mag.'), 'tanzer christian, mag.', '')>
      <Selector.Instance for sn = <Undef/value>>
      <Selector.Instance for ndc = <Undef/value>>
      <Selector.Instance for cc = <Undef/value>>

    >>> c_PiG_r_p_m = esf_completer \
    ...     ( scope, PAP.Person_in_Group.AQ.right
    ...     , "[PAP.Company_1P].person.title", "Ma"
    ...     , { "E_Type_NP" : "PAP.Company_1P" }
    ...     )
    >>> print (c_PiG_r_p_m.E_Type.type_name, c_PiG_r_p_m.E_Type_NP.type_name)
    PAP.Group PAP.Company_1P
    >>> prepr (c_PiG_r_p_m.attr_selectors)
    {'[PAP.Company_1P]person.title' : 'Ma'}
    >>> prepr (c_PiG_r_p_m.e_type_selectors)
    {'E_Type_NP' : 'PAP.Company_1P'}
    >>> prepr (c_PiG_r_p_m.filters_q)
    [Q.person.title.startswith ('ma',)]
    >>> print (formatted (c_PiG_r_p_m.names))
    ( '[PAP.Company_1P]person.title'
    , '[PAP.Company_1P]person.last_name'
    , '[PAP.Company_1P]person.first_name'
    , '[PAP.Company_1P]person.middle_name'
    , '[PAP.Company_1P]name'
    , '[PAP.Company_1P]registered_in'
    )

    >>> print (formatted (c_PiG_r_p_m.query ().all ()))
    [PAP.Company_1P (('tanzer', 'christian', '', 'mag.'), 'tanzer christian, mag.', '')]

    >>> c_PiG_r_p_m_instance = c_PiG_r_p_m.instance (ctc)
    >>> print (c_PiG_r_p_m_instance.recursive_repr ())
    <Selector.Instance for <PAP.Group.AQ> for PAP.Group = (('tanzer', 'christian', '', 'mag.'), 'tanzer christian, mag.', '')>
      <Selector.Instance for <PAP.Group.AQ> for PAP.Adhoc_Group = <Undef/value>>
      <Selector.Instance for <PAP.Group.AQ> for PAP.Company = <Undef/value>>
      <Selector.Instance for <PAP.Group.AQ> for PAP.Company_1P = Tanzer Christian, Mag.>
        <Selector.Instance for person.last_name = Tanzer>
        <Selector.Instance for person.first_name = Christian>
        <Selector.Instance for person.middle_name = >
        <Selector.Instance for person.title = Mag.>
        <Selector.Instance for name = Tanzer Christian, Mag.>
        <Selector.Instance for registered_in = >

    >>> for l, e in c_PiG_r_p_m_instance.level_elements () :
    ...      print ("  " * l, repr (e), "selected type =", e.selected_type)
     <Selector.Instance for <PAP.Group.AQ> for PAP.Group = (('tanzer', 'christian', '', 'mag.'), 'tanzer christian, mag.', '')> selected type = PAP.Company_1P
       <Selector.Instance for <PAP.Group.AQ> for PAP.Adhoc_Group = <Undef/value>> selected type = PAP.Company_1P
       <Selector.Instance for <PAP.Group.AQ> for PAP.Company = <Undef/value>> selected type = PAP.Company_1P
       <Selector.Instance for <PAP.Group.AQ> for PAP.Company_1P = Tanzer Christian, Mag.> selected type = PAP.Company_1P
         <Selector.Instance for person.last_name = Tanzer> selected type = PAP.Company_1P
         <Selector.Instance for person.first_name = Christian> selected type = PAP.Company_1P
         <Selector.Instance for person.middle_name = > selected type = PAP.Company_1P
         <Selector.Instance for person.title = Mag.> selected type = PAP.Company_1P
         <Selector.Instance for name = Tanzer Christian, Mag.> selected type = PAP.Company_1P
         <Selector.Instance for registered_in = > selected type = PAP.Company_1P

    >>> show_query (c_PiG_r_p_m.query ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_company.__raw_name AS pap_company___raw_name,
           pap_company.__raw_registered_in AS pap_company___raw_registered_in,
           pap_company.__raw_short_name AS pap_company___raw_short_name,
           pap_company.lifetime__finish AS pap_company_lifetime__finish,
           pap_company.lifetime__start AS pap_company_lifetime__start,
           pap_company.name AS pap_company_name,
           pap_company.pid AS pap_company_pid,
           pap_company.registered_in AS pap_company_registered_in,
           pap_company.short_name AS pap_company_short_name,
           pap_company_1p.person AS pap_company_1p_person,
           pap_company_1p.pid AS pap_company_1p_pid
         FROM mom_id_entity
           JOIN pap_company ON mom_id_entity.pid = pap_company.pid
           JOIN pap_company_1p ON pap_company.pid = pap_company_1p.pid
           JOIN pap_person AS pap_person__1 ON pap_person__1.pid = pap_company_1p.person
         WHERE (pap_person__1.title LIKE :title_1 || '%%%%')
    Parameters:
         title_1        : 'ma'

    >>> c_ShV_l_P_t = esf_completer \
    ...     ( scope, PAP.Subject_has_VAT_IDN.AQ.left
    ...     , "[PAP.Person].title", "Dr."
    ...     , { "E_Type_NP" : "PAP.Person" }
    ...     )
    >>> prepr (c_ShV_l_P_t.attr_selectors)
    {'[PAP.Person]title' : 'Dr.'}
    >>> prepr (c_ShV_l_P_t.e_type_selectors)
    {'E_Type_NP' : 'PAP.Person'}
    >>> prepr (c_ShV_l_P_t.filters_q)
    [Q.title.startswith ('dr.',)]
    >>> print (formatted (c_ShV_l_P_t.names))
    ( '[PAP.Person]title'
    , '[PAP.Person]last_name'
    , '[PAP.Person]first_name'
    , '[PAP.Person]middle_name'
    )
    >>> show_query (c_ShV_l_P_t.query ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_person.__raw_first_name AS pap_person___raw_first_name,
           pap_person.__raw_last_name AS pap_person___raw_last_name,
           pap_person.__raw_middle_name AS pap_person___raw_middle_name,
           pap_person.__raw_title AS pap_person___raw_title,
           pap_person.first_name AS pap_person_first_name,
           pap_person.last_name AS pap_person_last_name,
           pap_person.lifetime__finish AS pap_person_lifetime__finish,
           pap_person.lifetime__start AS pap_person_lifetime__start,
           pap_person.middle_name AS pap_person_middle_name,
           pap_person.pid AS pap_person_pid,
           pap_person.sex AS pap_person_sex,
           pap_person.title AS pap_person_title
         FROM mom_id_entity
           JOIN pap_person ON mom_id_entity.pid = pap_person.pid
         WHERE (pap_person.title LIKE :title_1 || '%%%%')
    Parameters:
         title_1              : 'dr.'

    >>> c_ShP_l_C_n = esf_completer \
    ...     ( scope, PAP.Subject_has_Property.AQ.left
    ...     , "[PAP.Company].name", "Goo", dict (E_Type_NP = "PAP.Company")
    ...     )
    >>> print (formatted (c_ShP_l_C_n.names))
    ( '[PAP.Company]name'
    , '[PAP.Company]registered_in'
    )

    >>> show_query (c_ShP_l_C_n.query ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_company.__raw_name AS pap_company___raw_name,
           pap_company.__raw_registered_in AS pap_company___raw_registered_in,
           pap_company.__raw_short_name AS pap_company___raw_short_name,
           pap_company.lifetime__finish AS pap_company_lifetime__finish,
           pap_company.lifetime__start AS pap_company_lifetime__start,
           pap_company.name AS pap_company_name,
           pap_company.pid AS pap_company_pid,
           pap_company.registered_in AS pap_company_registered_in,
           pap_company.short_name AS pap_company_short_name,
           pap_company_1p.person AS pap_company_1p_person,
           pap_company_1p.pid AS pap_company_1p_pid
         FROM mom_id_entity
           JOIN pap_company ON mom_id_entity.pid = pap_company.pid
           LEFT OUTER JOIN pap_company_1p ON pap_company.pid = pap_company_1p.pid
         WHERE (pap_company.name LIKE :name_1 || '%%%%')
    Parameters:
         name_1               : 'goo'

    >>> show_esf_query (scope, PAP.Subject_has_Property.AQ.right, "[PAP.Address].zip", "1130", { "E_Type_NP" : "PAP.Address"})
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_address."desc" AS pap_address_desc,
           pap_address.__raw_city AS pap_address___raw_city,
           pap_address.__raw_country AS pap_address___raw_country,
           pap_address.__raw_region AS pap_address___raw_region,
           pap_address.__raw_street AS pap_address___raw_street,
           pap_address.__raw_zip AS pap_address___raw_zip,
           pap_address.city AS pap_address_city,
           pap_address.country AS pap_address_country,
           pap_address.pid AS pap_address_pid,
           pap_address.region AS pap_address_region,
           pap_address.street AS pap_address_street,
           pap_address.zip AS pap_address_zip
         FROM mom_id_entity
           JOIN pap_address ON mom_id_entity.pid = pap_address.pid
         WHERE (pap_address.zip LIKE :zip_1 || '%%%%')
    Parameters:
         zip_1                : '1130'

    >>> c_E_l_C_l_P_p = esf_completer \
    ...     ( scope, EVT.Event.AQ.left
    ...     , "[SWP.Clip_O].left[SWP.Page].perma_name", "event-1"
    ...     , { "E_Type_NP" : "SWP.Clip_O", "[SWP.Clip_O]left/E_Type_NP" : "SWP.Page" }
    ...     )
    >>> prepr (c_E_l_C_l_P_p.attr_selectors)
    {'[SWP.Clip_O]left[SWP.Page].perma_name' : 'event-1'}
    >>> prepr (c_E_l_C_l_P_p.e_type_selectors)
    {'E_Type_NP' : 'SWP.Clip_O', '[SWP.Clip_O]left/E_Type_NP' : 'SWP.Page'}
    >>> prepr (c_E_l_C_l_P_p.filters_q)
    [Q.left ["SWP.Page"].perma_name.startswith ('event-1',)]
    >>> print (formatted (c_E_l_C_l_P_p.names))
    ( '[SWP.Clip_O]left[SWP.Page].perma_name'
    , '[SWP.Clip_O]date_x.start'
    , '[SWP.Clip_O]date_x.finish'
    )
    >>> print (formatted (c_E_l_C_l_P_p.query ().all ()))
    [SWP.Clip_O (('event-1-text', ), ())]

    >>> c_E_l_C_l_P_p_instance = c_E_l_C_l_P_p.instance (cl1)
    >>> for l, e in c_E_l_C_l_P_p_instance.level_elements () :
    ...      print ("  " * l, repr (e), "selected type =", e.selected_type)
     <Selector.Instance for <MOM.Id_Entity.AQ> for MOM.Id_Entity = (('event-1-text', ), ())> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for PAP.Adhoc_Group = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for PAP.Company = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for PAP.Company_1P = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for PAP.Person = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SRM.Page = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SRM.Regatta_C = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SRM.Regatta_Event = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SRM.Regatta_H = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SWP.Clip_O = event-1-text> selected type = SWP.Clip_O
         <Selector.Instance for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Object_PN = ('event-1-text')> selected type = SWP.Page
           <Selector.Instance for <left.AQ [Attr.Type.Querier Id_Entity]> for SRM.Page = <Undef/value>> selected type = SWP.Page
           <Selector.Instance for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Clip_X = <Undef/value>> selected type = SWP.Page
           <Selector.Instance for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Gallery = <Undef/value>> selected type = SWP.Page
           <Selector.Instance for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Page = ('event-1-text')> selected type = SWP.Page
             <Selector.Instance for left[SWP.Page].perma_name = event-1-text> selected type = SWP.Page
           <Selector.Instance for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Page_Y = <Undef/value>> selected type = SWP.Page
           <Selector.Instance for <left.AQ [Attr.Type.Querier Id_Entity]> for SWP.Referral = <Undef/value>> selected type = SWP.Page
         <Selector.Instance for date_x.start = None> selected type = SWP.Clip_O
         <Selector.Instance for date_x.finish = None> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SWP.Clip_X = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SWP.Gallery = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SWP.Page = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SWP.Page_Y = <Undef/value>> selected type = SWP.Clip_O
       <Selector.Instance for <MOM.Id_Entity.AQ> for SWP.Referral = <Undef/value>> selected type = SWP.Clip_O

    >>> print (formatted (c_E_l_C_l_P_p_instance.values))
    { '[SWP.Clip_O]' : 'event-1-text'
    , '[SWP.Clip_O]left' : SWP.Page ('event-1-text')
    , '[SWP.Clip_O]left[SWP.Page].perma_name' : 'event-1-text'
    }

"""

_test_templates = r"""
    >>> nav_root = create_app () # doctest:+ELLIPSIS
    Cache ...

    >>> scope = nav_root.scope

    >>> show_esf_form (nav_root, "PAP.Person_has_Phone", "left")
    <form class = "pure-form pure-form-stacked" title="Select Person">
        <div class="pure-controls">
                      <button class="pure-button pure-button-primary" name="APPLY" title="Use the currently selected Person" type="submit">
          <i class="fa"></i><b>Apply</b>
        </button>
                    <button class="pure-button" name="CLEAR" title="Reset fields" type="button">
          <i class="fa"></i><b>Clear</b>
        </button>
                    <button class="pure-button" name="CANCEL" title="Leave form without selecting Person" type="button">
          <i class="fa"></i><b>Cancel</b>
        </button>
        </div>
        <input type="hidden" name="__esf_for_attr__" value="left">
        <input type="hidden" name="__esf_for_type__" value="PAP.Person">
              <div class="pure-control-group attr-filter" title="Last name">
        <label for="last_name">Last name</label>
          <span class="value">
                      <input type="text" class="value" id="last_name" name="last_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="First name">
        <label for="first_name">First name</label>
          <span class="value">
                      <input type="text" class="value" id="first_name" name="first_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Middle name">
        <label for="middle_name">Middle name</label>
          <span class="value">
                      <input type="text" class="value" id="middle_name" name="middle_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Academic title">
        <label for="title">Academic title</label>
          <span class="value">
                      <input type="text" class="value" id="title" name="title"/>
       </span>
        </div>
    <BLANKLINE>
      </form>

    >>> show_esf_form (nav_root, "EVT.Event", "left")
      <form class = "pure-form pure-form-stacked" title="Select Id_Entity for attribute Object">
        <div class="pure-controls">
                      <button class="pure-button pure-button-primary" name="APPLY" title="Use the currently selected Id_Entity" type="submit">
          <i class="fa"></i><b>Apply</b>
        </button>
                    <button class="pure-button" name="CLEAR" title="Reset fields" type="button">
          <i class="fa"></i><b>Clear</b>
        </button>
                    <button class="pure-button" name="CANCEL" title="Leave form without selecting Id_Entity" type="button">
          <i class="fa"></i><b>Cancel</b>
        </button>
        </div>
        <input type="hidden" name="__esf_for_attr__" value="left">
        <input type="hidden" name="__esf_for_type__" value="MOM.Id_Entity">
              <div class="pure-control-group attr-filter polymorphic" title="Id_Entity">
        <div class=" pure-control-group">
        <label for="E_Type_NP">Select type of Id_Entity</label>
          <select class="E_Type" id="E_Type_NP" name="E_Type_NP" title="Select type of Id_Entity">
              <option value="">---</option>
                      <option value="PAP.Adhoc_Group">Adhoc_Group</option>
            <option value="PAP.Company">Company</option>
            <option value="PAP.Company_1P">Company_1P</option>
            <option value="PAP.Person">Person</option>
            <option value="SRM.Page">SRM.Page [Regatta_Page]</option>
            <option value="SRM.Regatta_C">Regatta_C</option>
            <option value="SRM.Regatta_Event">Regatta_Event</option>
            <option value="SRM.Regatta_H">Regatta_H</option>
            <option value="SWP.Clip_O">Clip_O</option>
            <option value="SWP.Clip_X">Clip_X</option>
            <option value="SWP.Gallery">Gallery</option>
            <option value="SWP.Page">Page</option>
            <option value="SWP.Page_Y">Page_Y</option>
            <option value="SWP.Referral">Referral</option>
            </select>
      </div>           <fieldset class="E_Type PAP.Adhoc_Group" disabled="True" title="Id_Entity[Adhoc_Group]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[PAP.Adhoc_Group]name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Adhoc_Group]name" name="[PAP.Adhoc_Group]name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type PAP.Company" disabled="True" title="Id_Entity[Company]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[PAP.Company]name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company]name" name="[PAP.Company]name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Registered in">
        <label for="[PAP.Company]registered_in">Registered in</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company]registered_in" name="[PAP.Company]registered_in"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type PAP.Company_1P" disabled="True" title="Id_Entity[Company_1P]">
              <div class="pure-control-group attr-filter" title="Person/Last name">
        <label for="[PAP.Company_1P]person.last_name">Person/Last name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company_1P]person.last_name" name="[PAP.Company_1P]person.last_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Person/First name">
        <label for="[PAP.Company_1P]person.first_name">Person/First name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company_1P]person.first_name" name="[PAP.Company_1P]person.first_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Person/Middle name">
        <label for="[PAP.Company_1P]person.middle_name">Person/Middle name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company_1P]person.middle_name" name="[PAP.Company_1P]person.middle_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Person/Academic title">
        <label for="[PAP.Company_1P]person.title">Person/Academic title</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company_1P]person.title" name="[PAP.Company_1P]person.title"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Name">
        <label for="[PAP.Company_1P]name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company_1P]name" name="[PAP.Company_1P]name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Registered in">
        <label for="[PAP.Company_1P]registered_in">Registered in</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Company_1P]registered_in" name="[PAP.Company_1P]registered_in"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type PAP.Person" disabled="True" title="Id_Entity[Person]">
              <div class="pure-control-group attr-filter" title="Last name">
        <label for="[PAP.Person]last_name">Last name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Person]last_name" name="[PAP.Person]last_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="First name">
        <label for="[PAP.Person]first_name">First name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Person]first_name" name="[PAP.Person]first_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Middle name">
        <label for="[PAP.Person]middle_name">Middle name</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Person]middle_name" name="[PAP.Person]middle_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Academic title">
        <label for="[PAP.Person]title">Academic title</label>
          <span class="value">
                      <input type="text" class="value" id="[PAP.Person]title" name="[PAP.Person]title"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SRM.Page" disabled="True" title="Id_Entity[Regatta_Page]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[SRM.Page]perma_name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SRM.Page]perma_name" name="[SRM.Page]perma_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Event/Name">
        <label for="[SRM.Page]event.name">Event/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SRM.Page]event.name" name="[SRM.Page]event.name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Event/Date/Start">
        <label for="[SRM.Page]event.date.start">Event/Date/Start</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Page]event.date.start" name="[SRM.Page]event.date.start"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Event/Date/Finish">
        <label for="[SRM.Page]event.date.finish">Event/Date/Finish</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Page]event.date.finish" name="[SRM.Page]event.date.finish"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SRM.Regatta_C" disabled="True" title="Id_Entity[Regatta_C]">
              <div class="pure-control-group attr-filter" title="Event/Name">
        <label for="[SRM.Regatta_C]left.name">Event/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SRM.Regatta_C]left.name" name="[SRM.Regatta_C]left.name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Event/Date/Start">
        <label for="[SRM.Regatta_C]left.date.start">Event/Date/Start</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Regatta_C]left.date.start" name="[SRM.Regatta_C]left.date.start"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Event/Date/Finish">
        <label for="[SRM.Regatta_C]left.date.finish">Event/Date/Finish</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Regatta_C]left.date.finish" name="[SRM.Regatta_C]left.date.finish"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Boat class/Name">
        <label for="[SRM.Regatta_C]boat_class.name">Boat class/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SRM.Regatta_C]boat_class.name" name="[SRM.Regatta_C]boat_class.name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SRM.Regatta_Event" disabled="True" title="Id_Entity[Regatta_Event]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[SRM.Regatta_Event]name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SRM.Regatta_Event]name" name="[SRM.Regatta_Event]name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Date/Start">
        <label for="[SRM.Regatta_Event]date.start">Date/Start</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Regatta_Event]date.start" name="[SRM.Regatta_Event]date.start"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Date/Finish">
        <label for="[SRM.Regatta_Event]date.finish">Date/Finish</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Regatta_Event]date.finish" name="[SRM.Regatta_Event]date.finish"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SRM.Regatta_H" disabled="True" title="Id_Entity[Regatta_H]">
              <div class="pure-control-group attr-filter" title="Event/Name">
        <label for="[SRM.Regatta_H]left.name">Event/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SRM.Regatta_H]left.name" name="[SRM.Regatta_H]left.name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Event/Date/Start">
        <label for="[SRM.Regatta_H]left.date.start">Event/Date/Start</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Regatta_H]left.date.start" name="[SRM.Regatta_H]left.date.start"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Event/Date/Finish">
        <label for="[SRM.Regatta_H]left.date.finish">Event/Date/Finish</label>
          <span class="value">
                    <input type="text" class="date value" id="[SRM.Regatta_H]left.date.finish" name="[SRM.Regatta_H]left.date.finish"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Handicap/Name">
        <label for="[SRM.Regatta_H]boat_class.name">Handicap/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SRM.Regatta_H]boat_class.name" name="[SRM.Regatta_H]boat_class.name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Clip_O" disabled="True" title="Id_Entity[Clip_O]">
                  <div class="pure-control-group attr-filter polymorphic" title="Object_PN">
        <div class=" pure-control-group">
        <label for="[SWP.Clip_O]left/E_Type_NP">Select type of Object_PN</label>
          <select class="E_Type" id="[SWP.Clip_O]left/E_Type_NP" name="[SWP.Clip_O]left/E_Type_NP" title="Select type of Object_PN">
                      <option value="SRM.Page">SRM.Page [Regatta_Page]</option>
            <option value="SWP.Clip_X">Clip_X</option>
            <option value="SWP.Gallery">Gallery</option>
            <option value="SWP.Page" selected="selected">Page</option>
            <option value="SWP.Page_Y">Page_Y</option>
            <option value="SWP.Referral">Referral</option>
                <option value="">---</option>
        </select>
      </div>           <fieldset class="E_Type SRM.Page" disabled="True" title="Object_PN[Regatta_Page]">
              <div class="pure-control-group attr-filter" title="Object[Regatta_Page]/Name">
        <label for="[SWP.Clip_O]left[SRM.Page].perma_name">Object[Regatta_Page]/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_O]left[SRM.Page].perma_name" name="[SWP.Clip_O]left[SRM.Page].perma_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Object[Regatta_Page]/Event/Name">
        <label for="[SWP.Clip_O]left[SRM.Page].event.name">Object[Regatta_Page]/Event/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_O]left[SRM.Page].event.name" name="[SWP.Clip_O]left[SRM.Page].event.name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Object[Regatta_Page]/Event/Date/Start">
        <label for="[SWP.Clip_O]left[SRM.Page].event.date.start">Object[Regatta_Page]/Event/Date/Start</label>
          <span class="value">
                    <input type="text" class="date value" id="[SWP.Clip_O]left[SRM.Page].event.date.start" name="[SWP.Clip_O]left[SRM.Page].event.date.start"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Object[Regatta_Page]/Event/Date/Finish">
        <label for="[SWP.Clip_O]left[SRM.Page].event.date.finish">Object[Regatta_Page]/Event/Date/Finish</label>
          <span class="value">
                    <input type="text" class="date value" id="[SWP.Clip_O]left[SRM.Page].event.date.finish" name="[SWP.Clip_O]left[SRM.Page].event.date.finish"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Clip_X" disabled="True" title="Object_PN[Clip_X]">
              <div class="pure-control-group attr-filter" title="Object[Clip_X]/Name">
        <label for="[SWP.Clip_O]left[SWP.Clip_X].perma_name">Object[Clip_X]/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_O]left[SWP.Clip_X].perma_name" name="[SWP.Clip_O]left[SWP.Clip_X].perma_name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Gallery" disabled="True" title="Object_PN[Gallery]">
              <div class="pure-control-group attr-filter" title="Object[Gallery]/Name">
        <label for="[SWP.Clip_O]left[SWP.Gallery].perma_name">Object[Gallery]/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_O]left[SWP.Gallery].perma_name" name="[SWP.Clip_O]left[SWP.Gallery].perma_name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Page" title="Object_PN[Page]">
              <div class="pure-control-group attr-filter" title="Object[Page]/Name">
        <label for="[SWP.Clip_O]left[SWP.Page].perma_name">Object[Page]/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_O]left[SWP.Page].perma_name" name="[SWP.Clip_O]left[SWP.Page].perma_name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Page_Y" disabled="True" title="Object_PN[Page_Y]">
              <div class="pure-control-group attr-filter" title="Object[Page_Y]/Name">
        <label for="[SWP.Clip_O]left[SWP.Page_Y].perma_name">Object[Page_Y]/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_O]left[SWP.Page_Y].perma_name" name="[SWP.Clip_O]left[SWP.Page_Y].perma_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Object[Page_Y]/Year">
        <label for="[SWP.Clip_O]left[SWP.Page_Y].year">Object[Page_Y]/Year</label>
          <span class="value">
                        <input type="text" class="value" id="[SWP.Clip_O]left[SWP.Page_Y].year" input-mode="number" name="[SWP.Clip_O]left[SWP.Page_Y].year" pattern="[-+]?[0-9]*"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Referral" disabled="True" title="Object_PN[Referral]">
              <div class="pure-control-group attr-filter" title="Object[Referral]/Parent url">
        <label for="[SWP.Clip_O]left[SWP.Referral].parent_url">Object[Referral]/Parent url</label>
          <span class="value">
                    <input type="url" class="value" id="[SWP.Clip_O]left[SWP.Referral].parent_url" name="[SWP.Clip_O]left[SWP.Referral].parent_url"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Object[Referral]/Name">
        <label for="[SWP.Clip_O]left[SWP.Referral].perma_name">Object[Referral]/Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_O]left[SWP.Referral].perma_name" name="[SWP.Clip_O]left[SWP.Referral].perma_name"/>
       </span>
        </div>
      </fieldset>
      </div>
            <div class="pure-control-group attr-filter" title="date/Start">
        <label for="[SWP.Clip_O]date_x.start">date/Start</label>
          <span class="value">
                    <input type="text" class="date value" id="[SWP.Clip_O]date_x.start" name="[SWP.Clip_O]date_x.start"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="date/Finish">
        <label for="[SWP.Clip_O]date_x.finish">date/Finish</label>
          <span class="value">
                    <input type="text" class="date value" id="[SWP.Clip_O]date_x.finish" name="[SWP.Clip_O]date_x.finish"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Clip_X" disabled="True" title="Id_Entity[Clip_X]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[SWP.Clip_X]perma_name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Clip_X]perma_name" name="[SWP.Clip_X]perma_name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Gallery" disabled="True" title="Id_Entity[Gallery]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[SWP.Gallery]perma_name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Gallery]perma_name" name="[SWP.Gallery]perma_name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Page" disabled="True" title="Id_Entity[Page]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[SWP.Page]perma_name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Page]perma_name" name="[SWP.Page]perma_name"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Page_Y" disabled="True" title="Id_Entity[Page_Y]">
              <div class="pure-control-group attr-filter" title="Name">
        <label for="[SWP.Page_Y]perma_name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Page_Y]perma_name" name="[SWP.Page_Y]perma_name"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Year">
        <label for="[SWP.Page_Y]year">Year</label>
          <span class="value">
                        <input type="text" class="value" id="[SWP.Page_Y]year" input-mode="number" name="[SWP.Page_Y]year" pattern="[-+]?[0-9]*"/>
       </span>
        </div>
      </fieldset>
            <fieldset class="E_Type SWP.Referral" disabled="True" title="Id_Entity[Referral]">
              <div class="pure-control-group attr-filter" title="Parent url">
        <label for="[SWP.Referral]parent_url">Parent url</label>
          <span class="value">
                    <input type="url" class="value" id="[SWP.Referral]parent_url" name="[SWP.Referral]parent_url"/>
       </span>
        </div>
            <div class="pure-control-group attr-filter" title="Name">
        <label for="[SWP.Referral]perma_name">Name</label>
          <span class="value">
                      <input type="text" class="value" id="[SWP.Referral]perma_name" name="[SWP.Referral]perma_name"/>
       </span>
        </div>
      </fieldset>
      </div>
      </form>


"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_main        = _test_main
        , test_templates   = _test_templates
        )
    )

__test__.update \
    ( Scaffold.create_test_dict \
        ( dict
            ( test_query     = _test_query
            )
        , ignore           = ("HPS", "MYS")
        )
    )

### __END__ GTW.__test__.Selector

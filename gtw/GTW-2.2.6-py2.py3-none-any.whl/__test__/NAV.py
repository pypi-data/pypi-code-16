# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.NAV
#
# Purpose
#    Test GTW.NAV functionality
#
# Revision Dates
#    27-Jan-2012 (CT) Creation
#     2-Jun-2012 (CT) Rename `suppress_translation_loading` to `load_I18N`
#    26-Jul-2012 (CT) Adapt to use of `GTW.RST.TOP` instead of `GTW.NAV`
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    11-Dec-2012 (CT) Add error `410`
#    12-Dec-2012 (CT) Add `Person_has_Account`
#    20-Jan-2013 (CT) Change `401`
#    21-Mar-2013 (CT) Add `Company_R` and tests for `Query_Restriction_Spec`
#     2-Apr-2013 (CT) Factor `test_qr`, add `test_esf`
#    11-Apr-2013 (CT) Adapt to changes in `MOM.Attr.Querier`
#     9-Dec-2013 (CT) Adapt to style changes of Auth forms
#    15-Sep-2014 (CT) Adapt to change of macro `entity_selector_form`
#     2-Jan-2015 (CT) Adapt to another change of macro `entity_selector_form`
#    27-Jan-2015 (CT) Add template `e_type_admin|ETR_table`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    18-May-2016 (CT) Factor `create_app` to `_GTW.__test__.model`
#    ««revision-date»»···
#--

from   __future__               import print_function, unicode_literals

_test_nav = """
    >>> nav_root = create_app () # doctest:+ELLIPSIS
    Cache ...

    >>> TTT = nav_root.Templateer.Template_Type

    >>> print (nav_root.abs_href)
    /

    >>> sk = Sorted_By ()
    >>> for t in sorted (nav_root.template_iter (), key = sk) :
    ...    print (t.name)
    400
    401
    403
    404
    405
    408
    410
    500
    503
    account_change_email
    account_change_password
    account_make_cert
    account_register
    account_reset_password
    calendar
    calendar_day
    console
    e_type_admin
    e_type_admin|ETR_table
    e_type_aggregator
    e_type_display
    e_type_mf3
    e_type_mf3|mf3
    e_type_mf3|mf3|mf3_h_cols
    gallery
    html/static.jnj
    login
    photo
    regatta_calendar
    regatta_page
    regatta_page_r
    site_admin
    video

    >>> for k in sorted (TTT.css_href_map, key = sk) :
    ...    print (k)
    400
    401
    403
    404
    405
    408
    410
    500
    503
    account_change_email
    account_change_password
    account_make_cert
    account_register
    account_reset_password
    calendar
    calendar_day
    console
    e_type_admin
    e_type_admin|ETR_table
    e_type_display
    e_type_mf3
    e_type_mf3|mf3
    e_type_mf3|mf3|mf3_h_cols
    gallery
    html/static.jnj
    login
    photo
    site_admin
    video

    >>> for owl in nav_root.own_links_transitive :
    ...   if not owl.hidden:
    ...     print (owl.href, owl.template.name)
    Admin site_admin
    Admin/Benutzerverwaltung site_admin
    Admin/Benutzerverwaltung/Account e_type_admin
    Admin/Benutzerverwaltung/Account_in_Group e_type_admin
    Admin/Benutzerverwaltung/Certificate e_type_admin
    Admin/Benutzerverwaltung/Group e_type_admin
    Admin/Personenverwaltung site_admin
    Admin/Personenverwaltung/Address e_type_admin
    Admin/Personenverwaltung/Address_Position e_type_admin
    Admin/Personenverwaltung/Company e_type_admin
    Admin/Personenverwaltung/Company_has_Address e_type_admin
    Admin/Personenverwaltung/Company_has_Email e_type_admin
    Admin/Personenverwaltung/Company_has_Phone e_type_admin
    Admin/Personenverwaltung/Company_has_Url e_type_admin
    Admin/Personenverwaltung/Company_R e_type_admin
    Admin/Personenverwaltung/Email e_type_admin
    Admin/Personenverwaltung/Person e_type_admin
    Admin/Personenverwaltung/Person_has_Account e_type_admin
    Admin/Personenverwaltung/Person_has_Address e_type_admin
    Admin/Personenverwaltung/Person_has_Email e_type_admin
    Admin/Personenverwaltung/Person_has_Phone e_type_admin
    Admin/Personenverwaltung/Person_has_Url e_type_admin
    Admin/Personenverwaltung/Phone e_type_admin
    Admin/Personenverwaltung/Subject_has_Property e_type_admin
    Admin/Personenverwaltung/Url e_type_admin
    Admin/Regattaverwaltung site_admin
    Admin/Regattaverwaltung/Boat e_type_admin
    Admin/Regattaverwaltung/Boat_in_Regatta e_type_admin
    Admin/Regattaverwaltung/Boat_Class e_type_admin
    Admin/Regattaverwaltung/Club e_type_admin
    Admin/Regattaverwaltung/Regatta_C e_type_admin
    Admin/Regattaverwaltung/Regatta_Event e_type_admin
    Admin/Regattaverwaltung/Regatta_H e_type_admin
    Admin/Regattaverwaltung/Regatta_Page e_type_admin
    Admin/Regattaverwaltung/Sailor e_type_admin
    Admin/Regattaverwaltung/Team e_type_admin
    Admin/Regattaverwaltung/Team_has_Boat_in_Regatta e_type_admin
    Admin/Webseitenverwaltung site_admin
    Admin/Webseitenverwaltung/Calendar e_type_admin
    Admin/Webseitenverwaltung/Clip_X e_type_admin
    Admin/Webseitenverwaltung/Event e_type_admin
    Admin/Webseitenverwaltung/Gallery e_type_admin
    Admin/Webseitenverwaltung/Page e_type_admin
    Admin/Webseitenverwaltung/Picture e_type_admin
    Admin/Webseitenverwaltung/Recurrence_Spec e_type_admin
    Admin/Webseitenverwaltung/Referral e_type_admin

    >>> php = nav_root.resource_from_href ("Admin/Personenverwaltung/Person_has_Phone/create")
    >>> print (php.href, php.template.name)
    Admin/Personenverwaltung/Person_has_Phone/create e_type_mf3|mf3

    >>> css_map = TFL.defaultdict (list)
    >>> for k, v in pyk.iteritems (TTT.css_href_map) :
    ...     css_map [v].append (k)
    >>> css_users = sorted ((sorted (vs, key = sk) for vs in pyk.itervalues (css_map)), key = sk)
    >>> print (formatted (css_users))
    [ [ 400
      , 403
      , 404
      , 405
      , 408
      , 410
      , 500
      , 503
      , 'account_register'
      , 'calendar'
      , 'calendar_day'
      , 'e_type_mf3'
      , 'html/static.jnj'
      , 'video'
      ]
    , [ 401
      , 'account_change_email'
      , 'account_change_password'
      , 'account_make_cert'
      , 'account_reset_password'
      , 'login'
      ]
    , ['console']
    , [ 'e_type_admin'
      , 'e_type_admin|ETR_table'
      ]
    , ['e_type_display']
    , [ 'e_type_mf3|mf3'
      , 'e_type_mf3|mf3|mf3_h_cols'
      ]
    , ['gallery']
    , ['photo']
    , ['site_admin']
    ]

"""

_test_qr = """
    >>> nav_root = create_app () # doctest:+ELLIPSIS
    Cache ...

    >>> crad = nav_root.ET_Map ["PAP.Company_R"].admin
    >>> crad
    <E_Type Company_R: /Admin/Personenverwaltung/Company_R>

    >>> QR = crad.QR
    >>> QR.__module__
    '_GTW._RST._TOP._MOM.Query_Restriction'

    >>> crad.E_Type.AQ.affiliate
    <affiliate.AQ [Attr.Type.Querier Id_Entity]>

    >>> crad.E_Type.AQ.affiliate.QR
    Q.affiliate
    >>> tuple (a.QR for a in crad.E_Type.AQ.affiliate.Attrs)
    (Q.affiliate.__raw_name, Q.affiliate.__raw_registered_in, Q.affiliate.lifetime, Q.affiliate.__raw_short_name, Q.affiliate.affiliate, Q.affiliate.owner)

    >>> print ((formatted (QR.Filter_Atoms (QR.Filter (crad.E_Type, "affiliate")))))
    ( Record
        ( AQ = <name.AQ [Attr.Type.Querier String]>
        , attr = String `name`
        , edit = None
        , full_name = 'name'
        , id = 'name___AC'
        , name = 'name___AC'
        , op =
          Record
            ( desc = 'Select entities where the attribute value starts with the specified value'
            , label = 'auto-complete'
            )
        , sig_key = 3
        , ui_name = 'Name'
        , value = None
        )
    , Record
        ( AQ = <registered_in.AQ [Attr.Type.Querier String]>
        , attr = String `registered_in`
        , edit = None
        , full_name = 'registered_in'
        , id = 'registered_in___AC'
        , name = 'registered_in___AC'
        , op =
          Record
            ( desc = 'Select entities where the attribute value starts with the specified value'
            , label = 'auto-complete'
            )
        , sig_key = 3
        , ui_name = 'Registered in'
        , value = None
        )
    )

    >>> print ((formatted (QR.Filter (crad.E_Type, "affiliate"))))
    Record
      ( AQ = <affiliate.AQ [Attr.Type.Querier Id_Entity]>
      , Class = 'Entity'
      , attr = Entity `affiliate`
      , attrs =
        [ Record
            ( attr = String `name`
            , full_name = 'affiliate.name'
            , id = 'affiliate__name'
            , name = 'name'
            , sig_key = 3
            , ui_name = 'Affiliate/Name'
            )
        , Record
            ( attr = String `registered_in`
            , full_name = 'affiliate.registered_in'
            , id = 'affiliate__registered_in'
            , name = 'registered_in'
            , sig_key = 3
            , ui_name = 'Affiliate/Registered in'
            )
        , Record
            ( attr = Date_Interval `lifetime`
            , attrs =
              [ Record
                  ( attr = Date `start`
                  , attrs =
                    [ Record
                        ( attr = Int `day`
                        , full_name = 'affiliate.lifetime.start.day'
                        , id = 'affiliate__lifetime__start__day'
                        , name = 'day'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Start/Day'
                        )
                    , Record
                        ( attr = Int `month`
                        , full_name = 'affiliate.lifetime.start.month'
                        , id = 'affiliate__lifetime__start__month'
                        , name = 'month'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Start/Month'
                        )
                    , Record
                        ( attr = Int `year`
                        , full_name = 'affiliate.lifetime.start.year'
                        , id = 'affiliate__lifetime__start__year'
                        , name = 'year'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Start/Year'
                        )
                    ]
                  , full_name = 'affiliate.lifetime.start'
                  , id = 'affiliate__lifetime__start'
                  , name = 'start'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start'
                  )
              , Record
                  ( attr = Date `finish`
                  , attrs =
                    [ Record
                        ( attr = Int `day`
                        , full_name = 'affiliate.lifetime.finish.day'
                        , id = 'affiliate__lifetime__finish__day'
                        , name = 'day'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Finish/Day'
                        )
                    , Record
                        ( attr = Int `month`
                        , full_name = 'affiliate.lifetime.finish.month'
                        , id = 'affiliate__lifetime__finish__month'
                        , name = 'month'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Finish/Month'
                        )
                    , Record
                        ( attr = Int `year`
                        , full_name = 'affiliate.lifetime.finish.year'
                        , id = 'affiliate__lifetime__finish__year'
                        , name = 'year'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Finish/Year'
                        )
                    ]
                  , full_name = 'affiliate.lifetime.finish'
                  , id = 'affiliate__lifetime__finish'
                  , name = 'finish'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish'
                  )
              , Record
                  ( attr = Boolean `alive`
                  , choices =
                    [ 'no'
                    , 'yes'
                    ]
                  , full_name = 'affiliate.lifetime.alive'
                  , id = 'affiliate__lifetime__alive'
                  , name = 'alive'
                  , sig_key = 1
                  , ui_name = 'Affiliate/Lifetime/Alive'
                  )
              ]
            , full_name = 'affiliate.lifetime'
            , id = 'affiliate__lifetime'
            , name = 'lifetime'
            , ui_name = 'Affiliate/Lifetime'
            )
        , Record
            ( attr = String `short_name`
            , full_name = 'affiliate.short_name'
            , id = 'affiliate__short_name'
            , name = 'short_name'
            , sig_key = 3
            , ui_name = 'Affiliate/Short name'
            )
        , Record
            ( Class = 'Entity'
            , attr = Entity `affiliate`
            , full_name = 'affiliate.affiliate'
            , id = 'affiliate__affiliate'
            , name = 'affiliate'
            , sig_key = 2
            , type_name = 'PAP.Company_R'
            , ui_name = 'Affiliate/Affiliate'
            , ui_type_name = 'Company_R'
            )
        , Record
            ( Class = 'Entity'
            , attr = Entity `owner`
            , children_np =
              [ Record
                  ( Class = 'Entity'
                  , attr = Entity `owner`
                  , attrs =
                    [ Record
                        ( attr = String `name`
                        , full_name = 'affiliate.owner[PAP.Company].name'
                        , id = 'affiliate__owner[PAP.Company]__name'
                        , name = 'name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Company]/Name'
                        )
                    , Record
                        ( attr = String `registered_in`
                        , full_name = 'affiliate.owner[PAP.Company].registered_in'
                        , id = 'affiliate__owner[PAP.Company]__registered_in'
                        , name = 'registered_in'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Company]/Registered in'
                        )
                    ]
                  , full_name = 'affiliate.owner[PAP.Company]'
                  , id = 'affiliate__owner[PAP.Company]'
                  , name = 'owner'
                  , sig_key = 2
                  , type_name = 'PAP.Company'
                  , ui_name = 'Affiliate/Owner[Company]'
                  , ui_type_name = 'Company'
                  )
              , Record
                  ( Class = 'Entity'
                  , attr = Entity `owner`
                  , full_name = 'affiliate.owner[PAP.Company_R]'
                  , id = 'affiliate__owner[PAP.Company_R]'
                  , name = 'owner'
                  , sig_key = 2
                  , type_name = 'PAP.Company_R'
                  , ui_name = 'Affiliate/Owner[Company_R]'
                  , ui_type_name = 'Company_R'
                  )
              , Record
                  ( Class = 'Entity'
                  , attr = Entity `owner`
                  , attrs =
                    [ Record
                        ( attr = String `last_name`
                        , full_name = 'affiliate.owner[PAP.Person].last_name'
                        , id = 'affiliate__owner[PAP.Person]__last_name'
                        , name = 'last_name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/Last name'
                        )
                    , Record
                        ( attr = String `first_name`
                        , full_name = 'affiliate.owner[PAP.Person].first_name'
                        , id = 'affiliate__owner[PAP.Person]__first_name'
                        , name = 'first_name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/First name'
                        )
                    , Record
                        ( attr = String `middle_name`
                        , full_name = 'affiliate.owner[PAP.Person].middle_name'
                        , id = 'affiliate__owner[PAP.Person]__middle_name'
                        , name = 'middle_name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/Middle name'
                        )
                    , Record
                        ( attr = String `title`
                        , full_name = 'affiliate.owner[PAP.Person].title'
                        , id = 'affiliate__owner[PAP.Person]__title'
                        , name = 'title'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/Academic title'
                        )
                    ]
                  , full_name = 'affiliate.owner[PAP.Person]'
                  , id = 'affiliate__owner[PAP.Person]'
                  , name = 'owner'
                  , sig_key = 2
                  , type_name = 'PAP.Person'
                  , ui_name = 'Affiliate/Owner[Person]'
                  , ui_type_name = 'Person'
                  )
              ]
            , default_child = 'PAP.Person'
            , full_name = 'affiliate.owner'
            , id = 'affiliate__owner'
            , name = 'owner'
            , sig_key = 2
            , type_name = 'PAP.Subject'
            , ui_name = 'Affiliate/Owner'
            , ui_type_name = 'Subject'
            )
        ]
      , edit = None
      , full_name = 'affiliate'
      , id = 'affiliate___AC'
      , name = 'affiliate___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 2
      , type_name = 'PAP.Company_R'
      , ui_name = 'Affiliate'
      , ui_type_name = 'Company_R'
      , value = None
      )

    >>> print ((formatted (QR.Filter (crad.E_Type, "affiliate__name"))))
    Record
      ( AQ = <affiliate.name.AQ [Attr.Type.Querier String]>
      , attr = String `name`
      , edit = None
      , full_name = 'affiliate.name'
      , id = 'affiliate__name___AC'
      , name = 'affiliate__name___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Affiliate/Name'
      , value = None
      )

    >>> print ((formatted (QR.Filter (crad.E_Type, "affiliate__lifetime"))))
    Record
      ( AQ = <affiliate.lifetime.AQ [Attr.Type.Querier Composite]>
      , attr = Date_Interval `lifetime`
      , attrs =
        [ Record
            ( attr = Date `start`
            , attrs =
              [ Record
                  ( attr = Int `day`
                  , full_name = 'affiliate.lifetime.start.day'
                  , id = 'affiliate__lifetime__start__day'
                  , name = 'day'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start/Day'
                  )
              , Record
                  ( attr = Int `month`
                  , full_name = 'affiliate.lifetime.start.month'
                  , id = 'affiliate__lifetime__start__month'
                  , name = 'month'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start/Month'
                  )
              , Record
                  ( attr = Int `year`
                  , full_name = 'affiliate.lifetime.start.year'
                  , id = 'affiliate__lifetime__start__year'
                  , name = 'year'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start/Year'
                  )
              ]
            , full_name = 'affiliate.lifetime.start'
            , id = 'affiliate__lifetime__start'
            , name = 'start'
            , sig_key = 0
            , ui_name = 'Affiliate/Lifetime/Start'
            )
        , Record
            ( attr = Date `finish`
            , attrs =
              [ Record
                  ( attr = Int `day`
                  , full_name = 'affiliate.lifetime.finish.day'
                  , id = 'affiliate__lifetime__finish__day'
                  , name = 'day'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish/Day'
                  )
              , Record
                  ( attr = Int `month`
                  , full_name = 'affiliate.lifetime.finish.month'
                  , id = 'affiliate__lifetime__finish__month'
                  , name = 'month'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish/Month'
                  )
              , Record
                  ( attr = Int `year`
                  , full_name = 'affiliate.lifetime.finish.year'
                  , id = 'affiliate__lifetime__finish__year'
                  , name = 'year'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish/Year'
                  )
              ]
            , full_name = 'affiliate.lifetime.finish'
            , id = 'affiliate__lifetime__finish'
            , name = 'finish'
            , sig_key = 0
            , ui_name = 'Affiliate/Lifetime/Finish'
            )
        , Record
            ( attr = Boolean `alive`
            , choices =
              [ 'no'
              , 'yes'
              ]
            , full_name = 'affiliate.lifetime.alive'
            , id = 'affiliate__lifetime__alive'
            , name = 'alive'
            , sig_key = 1
            , ui_name = 'Affiliate/Lifetime/Alive'
            )
        ]
      , edit = None
      , full_name = 'affiliate.lifetime'
      , id = 'affiliate__lifetime___AC'
      , name = 'affiliate__lifetime___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , ui_name = 'Affiliate/Lifetime'
      , value = None
      )

    >>> print ((formatted (QR.Filter (crad.E_Type, "affiliate__lifetime", dict (start = "20130320")))))
    Record
      ( AQ = <affiliate.lifetime.AQ [Attr.Type.Querier Composite]>
      , attr = Date_Interval `lifetime`
      , attrs =
        [ Record
            ( attr = Date `start`
            , attrs =
              [ Record
                  ( attr = Int `day`
                  , full_name = 'affiliate.lifetime.start.day'
                  , id = 'affiliate__lifetime__start__day'
                  , name = 'day'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start/Day'
                  )
              , Record
                  ( attr = Int `month`
                  , full_name = 'affiliate.lifetime.start.month'
                  , id = 'affiliate__lifetime__start__month'
                  , name = 'month'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start/Month'
                  )
              , Record
                  ( attr = Int `year`
                  , full_name = 'affiliate.lifetime.start.year'
                  , id = 'affiliate__lifetime__start__year'
                  , name = 'year'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start/Year'
                  )
              ]
            , full_name = 'affiliate.lifetime.start'
            , id = 'affiliate__lifetime__start'
            , name = 'start'
            , sig_key = 0
            , ui_name = 'Affiliate/Lifetime/Start'
            )
        , Record
            ( attr = Date `finish`
            , attrs =
              [ Record
                  ( attr = Int `day`
                  , full_name = 'affiliate.lifetime.finish.day'
                  , id = 'affiliate__lifetime__finish__day'
                  , name = 'day'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish/Day'
                  )
              , Record
                  ( attr = Int `month`
                  , full_name = 'affiliate.lifetime.finish.month'
                  , id = 'affiliate__lifetime__finish__month'
                  , name = 'month'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish/Month'
                  )
              , Record
                  ( attr = Int `year`
                  , full_name = 'affiliate.lifetime.finish.year'
                  , id = 'affiliate__lifetime__finish__year'
                  , name = 'year'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish/Year'
                  )
              ]
            , full_name = 'affiliate.lifetime.finish'
            , id = 'affiliate__lifetime__finish'
            , name = 'finish'
            , sig_key = 0
            , ui_name = 'Affiliate/Lifetime/Finish'
            )
        , Record
            ( attr = Boolean `alive`
            , choices =
              [ 'no'
              , 'yes'
              ]
            , full_name = 'affiliate.lifetime.alive'
            , id = 'affiliate__lifetime__alive'
            , name = 'alive'
            , sig_key = 1
            , ui_name = 'Affiliate/Lifetime/Alive'
            )
        ]
      , edit = {'start' : '20130320'}
      , full_name = 'affiliate.lifetime'
      , id = 'affiliate__lifetime___AC'
      , name = 'affiliate__lifetime___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , ui_name = 'Affiliate/Lifetime'
      , value = {'start' : '20130320'}
      )

    >>> print ((formatted (QR.Filter (crad.E_Type, "affiliate__lifetime__start"))))
    Record
      ( AQ = <affiliate.lifetime.start.AQ [Attr.Type.Querier Date]>
      , attr = Date `start`
      , attrs =
        [ Record
            ( attr = Int `day`
            , full_name = 'affiliate.lifetime.start.day'
            , id = 'affiliate__lifetime__start__day'
            , name = 'day'
            , sig_key = 0
            , ui_name = 'Affiliate/Lifetime/Start/Day'
            )
        , Record
            ( attr = Int `month`
            , full_name = 'affiliate.lifetime.start.month'
            , id = 'affiliate__lifetime__start__month'
            , name = 'month'
            , sig_key = 0
            , ui_name = 'Affiliate/Lifetime/Start/Month'
            )
        , Record
            ( attr = Int `year`
            , full_name = 'affiliate.lifetime.start.year'
            , id = 'affiliate__lifetime__start__year'
            , name = 'year'
            , sig_key = 0
            , ui_name = 'Affiliate/Lifetime/Start/Year'
            )
        ]
      , edit = None
      , full_name = 'affiliate.lifetime.start'
      , id = 'affiliate__lifetime__start___AC'
      , name = 'affiliate__lifetime__start___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 0
      , ui_name = 'Affiliate/Lifetime/Start'
      , value = None
      )

    >>> qrs = crad.qr_spec
    >>> qrs
    <Attr.Type.Querier.Query_Restriction_Spec for PAP.Company_R>

    >>> print ((formatted (qrs.As_Template_Elem)))
    [ Record
        ( attr = String `name`
        , full_name = 'name'
        , id = 'name'
        , name = 'name'
        , sig_key = 3
        , ui_name = 'Name'
        )
    , Record
        ( attr = String `registered_in`
        , full_name = 'registered_in'
        , id = 'registered_in'
        , name = 'registered_in'
        , sig_key = 3
        , ui_name = 'Registered in'
        )
    , Record
        ( attr = Date_Interval `lifetime`
        , attrs =
          [ Record
              ( attr = Date `start`
              , attrs =
                [ Record
                    ( attr = Int `day`
                    , full_name = 'lifetime.start.day'
                    , id = 'lifetime__start__day'
                    , name = 'day'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Day'
                    )
                , Record
                    ( attr = Int `month`
                    , full_name = 'lifetime.start.month'
                    , id = 'lifetime__start__month'
                    , name = 'month'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Month'
                    )
                , Record
                    ( attr = Int `year`
                    , full_name = 'lifetime.start.year'
                    , id = 'lifetime__start__year'
                    , name = 'year'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Year'
                    )
                ]
              , full_name = 'lifetime.start'
              , id = 'lifetime__start'
              , name = 'start'
              , sig_key = 0
              , ui_name = 'Lifetime/Start'
              )
          , Record
              ( attr = Date `finish`
              , attrs =
                [ Record
                    ( attr = Int `day`
                    , full_name = 'lifetime.finish.day'
                    , id = 'lifetime__finish__day'
                    , name = 'day'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Day'
                    )
                , Record
                    ( attr = Int `month`
                    , full_name = 'lifetime.finish.month'
                    , id = 'lifetime__finish__month'
                    , name = 'month'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Month'
                    )
                , Record
                    ( attr = Int `year`
                    , full_name = 'lifetime.finish.year'
                    , id = 'lifetime__finish__year'
                    , name = 'year'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Year'
                    )
                ]
              , full_name = 'lifetime.finish'
              , id = 'lifetime__finish'
              , name = 'finish'
              , sig_key = 0
              , ui_name = 'Lifetime/Finish'
              )
          , Record
              ( attr = Boolean `alive`
              , choices =
                [ 'no'
                , 'yes'
                ]
              , full_name = 'lifetime.alive'
              , id = 'lifetime__alive'
              , name = 'alive'
              , sig_key = 1
              , ui_name = 'Lifetime/Alive'
              )
          ]
        , full_name = 'lifetime'
        , id = 'lifetime'
        , name = 'lifetime'
        , ui_name = 'Lifetime'
        )
    , Record
        ( attr = String `short_name`
        , full_name = 'short_name'
        , id = 'short_name'
        , name = 'short_name'
        , sig_key = 3
        , ui_name = 'Short name'
        )
    , Record
        ( Class = 'Entity'
        , attr = Entity `affiliate`
        , attrs =
          [ Record
              ( attr = String `name`
              , full_name = 'affiliate.name'
              , id = 'affiliate__name'
              , name = 'name'
              , sig_key = 3
              , ui_name = 'Affiliate/Name'
              )
          , Record
              ( attr = String `registered_in`
              , full_name = 'affiliate.registered_in'
              , id = 'affiliate__registered_in'
              , name = 'registered_in'
              , sig_key = 3
              , ui_name = 'Affiliate/Registered in'
              )
          , Record
              ( attr = Date_Interval `lifetime`
              , attrs =
                [ Record
                    ( attr = Date `start`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'affiliate.lifetime.start.day'
                          , id = 'affiliate__lifetime__start__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Start/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'affiliate.lifetime.start.month'
                          , id = 'affiliate__lifetime__start__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Start/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'affiliate.lifetime.start.year'
                          , id = 'affiliate__lifetime__start__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Start/Year'
                          )
                      ]
                    , full_name = 'affiliate.lifetime.start'
                    , id = 'affiliate__lifetime__start'
                    , name = 'start'
                    , sig_key = 0
                    , ui_name = 'Affiliate/Lifetime/Start'
                    )
                , Record
                    ( attr = Date `finish`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'affiliate.lifetime.finish.day'
                          , id = 'affiliate__lifetime__finish__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Finish/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'affiliate.lifetime.finish.month'
                          , id = 'affiliate__lifetime__finish__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Finish/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'affiliate.lifetime.finish.year'
                          , id = 'affiliate__lifetime__finish__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Finish/Year'
                          )
                      ]
                    , full_name = 'affiliate.lifetime.finish'
                    , id = 'affiliate__lifetime__finish'
                    , name = 'finish'
                    , sig_key = 0
                    , ui_name = 'Affiliate/Lifetime/Finish'
                    )
                , Record
                    ( attr = Boolean `alive`
                    , choices =
                      [ 'no'
                      , 'yes'
                      ]
                    , full_name = 'affiliate.lifetime.alive'
                    , id = 'affiliate__lifetime__alive'
                    , name = 'alive'
                    , sig_key = 1
                    , ui_name = 'Affiliate/Lifetime/Alive'
                    )
                ]
              , full_name = 'affiliate.lifetime'
              , id = 'affiliate__lifetime'
              , name = 'lifetime'
              , ui_name = 'Affiliate/Lifetime'
              )
          , Record
              ( attr = String `short_name`
              , full_name = 'affiliate.short_name'
              , id = 'affiliate__short_name'
              , name = 'short_name'
              , sig_key = 3
              , ui_name = 'Affiliate/Short name'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `affiliate`
              , full_name = 'affiliate.affiliate'
              , id = 'affiliate__affiliate'
              , name = 'affiliate'
              , sig_key = 2
              , type_name = 'PAP.Company_R'
              , ui_name = 'Affiliate/Affiliate'
              , ui_type_name = 'Company_R'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `owner`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `owner`
                    , attrs =
                      [ Record
                          ( attr = String `name`
                          , full_name = 'affiliate.owner[PAP.Company].name'
                          , id = 'affiliate__owner[PAP.Company]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner[Company]/Name'
                          )
                      , Record
                          ( attr = String `registered_in`
                          , full_name = 'affiliate.owner[PAP.Company].registered_in'
                          , id = 'affiliate__owner[PAP.Company]__registered_in'
                          , name = 'registered_in'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner[Company]/Registered in'
                          )
                      ]
                    , full_name = 'affiliate.owner[PAP.Company]'
                    , id = 'affiliate__owner[PAP.Company]'
                    , name = 'owner'
                    , sig_key = 2
                    , type_name = 'PAP.Company'
                    , ui_name = 'Affiliate/Owner[Company]'
                    , ui_type_name = 'Company'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `owner`
                    , full_name = 'affiliate.owner[PAP.Company_R]'
                    , id = 'affiliate__owner[PAP.Company_R]'
                    , name = 'owner'
                    , sig_key = 2
                    , type_name = 'PAP.Company_R'
                    , ui_name = 'Affiliate/Owner[Company_R]'
                    , ui_type_name = 'Company_R'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `owner`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'affiliate.owner[PAP.Person].last_name'
                          , id = 'affiliate__owner[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'affiliate.owner[PAP.Person].first_name'
                          , id = 'affiliate__owner[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'affiliate.owner[PAP.Person].middle_name'
                          , id = 'affiliate__owner[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'affiliate.owner[PAP.Person].title'
                          , id = 'affiliate__owner[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner[Person]/Academic title'
                          )
                      ]
                    , full_name = 'affiliate.owner[PAP.Person]'
                    , id = 'affiliate__owner[PAP.Person]'
                    , name = 'owner'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Affiliate/Owner[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , default_child = 'PAP.Person'
              , full_name = 'affiliate.owner'
              , id = 'affiliate__owner'
              , name = 'owner'
              , sig_key = 2
              , type_name = 'PAP.Subject'
              , ui_name = 'Affiliate/Owner'
              , ui_type_name = 'Subject'
              )
          ]
        , full_name = 'affiliate'
        , id = 'affiliate'
        , name = 'affiliate'
        , sig_key = 2
        , type_name = 'PAP.Company_R'
        , ui_name = 'Affiliate'
        , ui_type_name = 'Company_R'
        )
    , Record
        ( Class = 'Entity'
        , attr = Entity `owner`
        , children_np =
          [ Record
              ( Class = 'Entity'
              , attr = Entity `owner`
              , attrs =
                [ Record
                    ( attr = String `name`
                    , full_name = 'owner[PAP.Company].name'
                    , id = 'owner[PAP.Company]__name'
                    , name = 'name'
                    , sig_key = 3
                    , ui_name = 'Owner[Company]/Name'
                    )
                , Record
                    ( attr = String `registered_in`
                    , full_name = 'owner[PAP.Company].registered_in'
                    , id = 'owner[PAP.Company]__registered_in'
                    , name = 'registered_in'
                    , sig_key = 3
                    , ui_name = 'Owner[Company]/Registered in'
                    )
                ]
              , full_name = 'owner[PAP.Company]'
              , id = 'owner[PAP.Company]'
              , name = 'owner'
              , sig_key = 2
              , type_name = 'PAP.Company'
              , ui_name = 'Owner[Company]'
              , ui_type_name = 'Company'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `owner`
              , attrs =
                [ Record
                    ( attr = String `name`
                    , full_name = 'owner[PAP.Company_R].name'
                    , id = 'owner[PAP.Company_R]__name'
                    , name = 'name'
                    , sig_key = 3
                    , ui_name = 'Owner[Company_R]/Name'
                    )
                , Record
                    ( attr = String `registered_in`
                    , full_name = 'owner[PAP.Company_R].registered_in'
                    , id = 'owner[PAP.Company_R]__registered_in'
                    , name = 'registered_in'
                    , sig_key = 3
                    , ui_name = 'Owner[Company_R]/Registered in'
                    )
                ]
              , full_name = 'owner[PAP.Company_R]'
              , id = 'owner[PAP.Company_R]'
              , name = 'owner'
              , sig_key = 2
              , type_name = 'PAP.Company_R'
              , ui_name = 'Owner[Company_R]'
              , ui_type_name = 'Company_R'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `owner`
              , attrs =
                [ Record
                    ( attr = String `last_name`
                    , full_name = 'owner[PAP.Person].last_name'
                    , id = 'owner[PAP.Person]__last_name'
                    , name = 'last_name'
                    , sig_key = 3
                    , ui_name = 'Owner[Person]/Last name'
                    )
                , Record
                    ( attr = String `first_name`
                    , full_name = 'owner[PAP.Person].first_name'
                    , id = 'owner[PAP.Person]__first_name'
                    , name = 'first_name'
                    , sig_key = 3
                    , ui_name = 'Owner[Person]/First name'
                    )
                , Record
                    ( attr = String `middle_name`
                    , full_name = 'owner[PAP.Person].middle_name'
                    , id = 'owner[PAP.Person]__middle_name'
                    , name = 'middle_name'
                    , sig_key = 3
                    , ui_name = 'Owner[Person]/Middle name'
                    )
                , Record
                    ( attr = String `title`
                    , full_name = 'owner[PAP.Person].title'
                    , id = 'owner[PAP.Person]__title'
                    , name = 'title'
                    , sig_key = 3
                    , ui_name = 'Owner[Person]/Academic title'
                    )
                ]
              , full_name = 'owner[PAP.Person]'
              , id = 'owner[PAP.Person]'
              , name = 'owner'
              , sig_key = 2
              , type_name = 'PAP.Person'
              , ui_name = 'Owner[Person]'
              , ui_type_name = 'Person'
              )
          ]
        , default_child = 'PAP.Person'
        , full_name = 'owner'
        , id = 'owner'
        , name = 'owner'
        , sig_key = 2
        , type_name = 'PAP.Subject'
        , ui_name = 'Owner'
        , ui_type_name = 'Subject'
        )
    , Record
        ( Class = 'Entity'
        , attr = Rev_Ref `creation`
        , attrs =
          [ Record
              ( attr = Date-Time `c_time`
              , full_name = 'creation.c_time'
              , id = 'creation__c_time'
              , name = 'c_time'
              , sig_key = 0
              , ui_name = 'Creation/C time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `c_user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'creation.c_user[Auth.Account].name'
                          , id = 'creation__c_user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Account]/Name'
                          )
                      ]
                    , full_name = 'creation.c_user[Auth.Account]'
                    , id = 'creation__c_user[Auth.Account]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Creation/C user[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'creation.c_user[PAP.Person].last_name'
                          , id = 'creation__c_user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'creation.c_user[PAP.Person].first_name'
                          , id = 'creation__c_user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'creation.c_user[PAP.Person].middle_name'
                          , id = 'creation__c_user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'creation.c_user[PAP.Person].title'
                          , id = 'creation__c_user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/Academic title'
                          )
                      ]
                    , full_name = 'creation.c_user[PAP.Person]'
                    , id = 'creation__c_user[PAP.Person]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Creation/C user[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'creation.c_user'
              , id = 'creation__c_user'
              , name = 'c_user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Creation/C user'
              , ui_type_name = 'Id_Entity'
              )
          , Record
              ( attr = String `kind`
              , full_name = 'creation.kind'
              , id = 'creation__kind'
              , name = 'kind'
              , sig_key = 3
              , ui_name = 'Creation/Kind'
              )
          , Record
              ( attr = Date-Time `time`
              , full_name = 'creation.time'
              , id = 'creation__time'
              , name = 'time'
              , sig_key = 0
              , ui_name = 'Creation/Time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'creation.user[Auth.Account].name'
                          , id = 'creation__user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Account]/Name'
                          )
                      ]
                    , full_name = 'creation.user[Auth.Account]'
                    , id = 'creation__user[Auth.Account]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Creation/User[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'creation.user[PAP.Person].last_name'
                          , id = 'creation__user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'creation.user[PAP.Person].first_name'
                          , id = 'creation__user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'creation.user[PAP.Person].middle_name'
                          , id = 'creation__user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'creation.user[PAP.Person].title'
                          , id = 'creation__user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/Academic title'
                          )
                      ]
                    , full_name = 'creation.user[PAP.Person]'
                    , id = 'creation__user[PAP.Person]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Creation/User[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'creation.user'
              , id = 'creation__user'
              , name = 'user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Creation/User'
              , ui_type_name = 'Id_Entity'
              )
          ]
        , full_name = 'creation'
        , id = 'creation'
        , name = 'creation'
        , sig_key = 2
        , type_name = 'MOM.MD_Change'
        , ui_name = 'Creation'
        , ui_type_name = 'MD_Change'
        )
    , Record
        ( Class = 'Entity'
        , attr = Rev_Ref `last_change`
        , attrs =
          [ Record
              ( attr = Date-Time `c_time`
              , full_name = 'last_change.c_time'
              , id = 'last_change__c_time'
              , name = 'c_time'
              , sig_key = 0
              , ui_name = 'Last change/C time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `c_user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'last_change.c_user[Auth.Account].name'
                          , id = 'last_change__c_user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Account]/Name'
                          )
                      ]
                    , full_name = 'last_change.c_user[Auth.Account]'
                    , id = 'last_change__c_user[Auth.Account]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Last change/C user[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'last_change.c_user[PAP.Person].last_name'
                          , id = 'last_change__c_user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'last_change.c_user[PAP.Person].first_name'
                          , id = 'last_change__c_user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'last_change.c_user[PAP.Person].middle_name'
                          , id = 'last_change__c_user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'last_change.c_user[PAP.Person].title'
                          , id = 'last_change__c_user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/Academic title'
                          )
                      ]
                    , full_name = 'last_change.c_user[PAP.Person]'
                    , id = 'last_change__c_user[PAP.Person]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Last change/C user[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'last_change.c_user'
              , id = 'last_change__c_user'
              , name = 'c_user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Last change/C user'
              , ui_type_name = 'Id_Entity'
              )
          , Record
              ( attr = String `kind`
              , full_name = 'last_change.kind'
              , id = 'last_change__kind'
              , name = 'kind'
              , sig_key = 3
              , ui_name = 'Last change/Kind'
              )
          , Record
              ( attr = Date-Time `time`
              , full_name = 'last_change.time'
              , id = 'last_change__time'
              , name = 'time'
              , sig_key = 0
              , ui_name = 'Last change/Time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'last_change.user[Auth.Account].name'
                          , id = 'last_change__user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Account]/Name'
                          )
                      ]
                    , full_name = 'last_change.user[Auth.Account]'
                    , id = 'last_change__user[Auth.Account]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Last change/User[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'last_change.user[PAP.Person].last_name'
                          , id = 'last_change__user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'last_change.user[PAP.Person].first_name'
                          , id = 'last_change__user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'last_change.user[PAP.Person].middle_name'
                          , id = 'last_change__user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'last_change.user[PAP.Person].title'
                          , id = 'last_change__user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/Academic title'
                          )
                      ]
                    , full_name = 'last_change.user[PAP.Person]'
                    , id = 'last_change__user[PAP.Person]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Last change/User[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'last_change.user'
              , id = 'last_change__user'
              , name = 'user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Last change/User'
              , ui_type_name = 'Id_Entity'
              )
          ]
        , full_name = 'last_change'
        , id = 'last_change'
        , name = 'last_change'
        , sig_key = 2
        , type_name = 'MOM.MD_Change'
        , ui_name = 'Last change'
        , ui_type_name = 'MD_Change'
        )
    , Record
        ( attr = Int `last_cid`
        , full_name = 'last_cid'
        , id = 'last_cid'
        , name = 'last_cid'
        , sig_key = 0
        , ui_name = 'Last cid'
        )
    , Record
        ( attr = Surrogate `pid`
        , full_name = 'pid'
        , id = 'pid'
        , name = 'pid'
        , sig_key = 0
        , ui_name = 'Pid'
        )
    , Record
        ( attr = String `type_name`
        , full_name = 'type_name'
        , id = 'type_name'
        , name = 'type_name'
        , sig_key = 3
        , ui_name = 'Type name'
        )
    , Record
        ( Class = 'Entity'
        , attr = Link_Ref_List `events`
        , attrs =
          [ Record
              ( attr = Date_Interval `date`
              , attrs =
                [ Record
                    ( attr = Date `start`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'events.date.start.day'
                          , id = 'events__date__start__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Start/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'events.date.start.month'
                          , id = 'events__date__start__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Start/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'events.date.start.year'
                          , id = 'events__date__start__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Start/Year'
                          )
                      ]
                    , full_name = 'events.date.start'
                    , id = 'events__date__start'
                    , name = 'start'
                    , sig_key = 0
                    , ui_name = 'Events/Date/Start'
                    )
                , Record
                    ( attr = Date `finish`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'events.date.finish.day'
                          , id = 'events__date__finish__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Finish/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'events.date.finish.month'
                          , id = 'events__date__finish__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Finish/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'events.date.finish.year'
                          , id = 'events__date__finish__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Finish/Year'
                          )
                      ]
                    , full_name = 'events.date.finish'
                    , id = 'events__date__finish'
                    , name = 'finish'
                    , sig_key = 0
                    , ui_name = 'Events/Date/Finish'
                    )
                , Record
                    ( attr = Boolean `alive`
                    , choices =
                      [ 'no'
                      , 'yes'
                      ]
                    , full_name = 'events.date.alive'
                    , id = 'events__date__alive'
                    , name = 'alive'
                    , sig_key = 1
                    , ui_name = 'Events/Date/Alive'
                    )
                ]
              , full_name = 'events.date'
              , id = 'events__date'
              , name = 'date'
              , ui_name = 'Events/Date'
              )
          , Record
              ( attr = Time_Interval `time`
              , attrs =
                [ Record
                    ( attr = Time `start`
                    , attrs =
                      [ Record
                          ( attr = Int `hour`
                          , full_name = 'events.time.start.hour'
                          , id = 'events__time__start__hour'
                          , name = 'hour'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Start/Hour'
                          )
                      , Record
                          ( attr = Int `minute`
                          , full_name = 'events.time.start.minute'
                          , id = 'events__time__start__minute'
                          , name = 'minute'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Start/Minute'
                          )
                      , Record
                          ( attr = Int `second`
                          , full_name = 'events.time.start.second'
                          , id = 'events__time__start__second'
                          , name = 'second'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Start/Second'
                          )
                      ]
                    , full_name = 'events.time.start'
                    , id = 'events__time__start'
                    , name = 'start'
                    , sig_key = 0
                    , ui_name = 'Events/Time/Start'
                    )
                , Record
                    ( attr = Time `finish`
                    , attrs =
                      [ Record
                          ( attr = Int `hour`
                          , full_name = 'events.time.finish.hour'
                          , id = 'events__time__finish__hour'
                          , name = 'hour'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Finish/Hour'
                          )
                      , Record
                          ( attr = Int `minute`
                          , full_name = 'events.time.finish.minute'
                          , id = 'events__time__finish__minute'
                          , name = 'minute'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Finish/Minute'
                          )
                      , Record
                          ( attr = Int `second`
                          , full_name = 'events.time.finish.second'
                          , id = 'events__time__finish__second'
                          , name = 'second'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Finish/Second'
                          )
                      ]
                    , full_name = 'events.time.finish'
                    , id = 'events__time__finish'
                    , name = 'finish'
                    , sig_key = 0
                    , ui_name = 'Events/Time/Finish'
                    )
                ]
              , full_name = 'events.time'
              , id = 'events__time'
              , name = 'time'
              , ui_name = 'Events/Time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `calendar`
              , attrs =
                [ Record
                    ( attr = Name `name`
                    , full_name = 'events.calendar.name'
                    , id = 'events__calendar__name'
                    , name = 'name'
                    , sig_key = 3
                    , ui_name = 'Events/Calendar/Name'
                    )
                , Record
                    ( attr = String `desc`
                    , full_name = 'events.calendar.desc'
                    , id = 'events__calendar__desc'
                    , name = 'desc'
                    , sig_key = 3
                    , ui_name = 'Events/Calendar/Description'
                    )
                ]
              , full_name = 'events.calendar'
              , id = 'events__calendar'
              , name = 'calendar'
              , sig_key = 2
              , type_name = 'EVT.Calendar'
              , ui_name = 'Events/Calendar'
              , ui_type_name = 'Calendar'
              )
          , Record
              ( attr = String `detail`
              , full_name = 'events.detail'
              , id = 'events__detail'
              , name = 'detail'
              , sig_key = 3
              , ui_name = 'Events/Detail'
              )
          , Record
              ( attr = String `short_title`
              , full_name = 'events.short_title'
              , id = 'events__short_title'
              , name = 'short_title'
              , sig_key = 3
              , ui_name = 'Events/Short title'
              )
          ]
        , full_name = 'events'
        , id = 'events'
        , name = 'events'
        , sig_key = 2
        , type_name = 'EVT.Event'
        , ui_name = 'Events'
        , ui_type_name = 'Event'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `urls`
        , attrs =
          [ Record
              ( attr = Url `value`
              , full_name = 'urls.value'
              , id = 'urls__value'
              , name = 'value'
              , sig_key = 3
              , ui_name = 'Urls/Value'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'urls.desc'
              , id = 'urls__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Urls/Description'
              )
          ]
        , full_name = 'urls'
        , id = 'urls'
        , name = 'urls'
        , sig_key = 2
        , type_name = 'PAP.Url'
        , ui_name = 'Urls'
        , ui_type_name = 'Url'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `phones`
        , attrs =
          [ Record
              ( attr = Numeric_String `sn`
              , full_name = 'phones.sn'
              , id = 'phones__sn'
              , name = 'sn'
              , sig_key = 3
              , ui_name = 'Phones/Subscriber number'
              )
          , Record
              ( attr = Numeric_String `ndc`
              , full_name = 'phones.ndc'
              , id = 'phones__ndc'
              , name = 'ndc'
              , sig_key = 3
              , ui_name = 'Phones/Network destination code'
              )
          , Record
              ( attr = Numeric_String `cc`
              , full_name = 'phones.cc'
              , id = 'phones__cc'
              , name = 'cc'
              , sig_key = 3
              , ui_name = 'Phones/Country code'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'phones.desc'
              , id = 'phones__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Phones/Description'
              )
          ]
        , full_name = 'phones'
        , id = 'phones'
        , name = 'phones'
        , sig_key = 2
        , type_name = 'PAP.Phone'
        , ui_name = 'Phones'
        , ui_type_name = 'Phone'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `emails`
        , attrs =
          [ Record
              ( attr = Email `address`
              , full_name = 'emails.address'
              , id = 'emails__address'
              , name = 'address'
              , sig_key = 3
              , ui_name = 'Emails/Email address'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'emails.desc'
              , id = 'emails__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Emails/Description'
              )
          ]
        , full_name = 'emails'
        , id = 'emails'
        , name = 'emails'
        , sig_key = 2
        , type_name = 'PAP.Email'
        , ui_name = 'Emails'
        , ui_type_name = 'Email'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `addresses`
        , attrs =
          [ Record
              ( attr = String `street`
              , full_name = 'addresses.street'
              , id = 'addresses__street'
              , name = 'street'
              , sig_key = 3
              , ui_name = 'Addresses/Street'
              )
          , Record
              ( attr = String `zip`
              , full_name = 'addresses.zip'
              , id = 'addresses__zip'
              , name = 'zip'
              , sig_key = 3
              , ui_name = 'Addresses/Zip code'
              )
          , Record
              ( attr = String `city`
              , full_name = 'addresses.city'
              , id = 'addresses__city'
              , name = 'city'
              , sig_key = 3
              , ui_name = 'Addresses/City'
              )
          , Record
              ( attr = String `country`
              , full_name = 'addresses.country'
              , id = 'addresses__country'
              , name = 'country'
              , sig_key = 3
              , ui_name = 'Addresses/Country'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'addresses.desc'
              , id = 'addresses__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Addresses/Description'
              )
          , Record
              ( attr = String `region`
              , full_name = 'addresses.region'
              , id = 'addresses__region'
              , name = 'region'
              , sig_key = 3
              , ui_name = 'Addresses/Region'
              )
          ]
        , full_name = 'addresses'
        , id = 'addresses'
        , name = 'addresses'
        , sig_key = 2
        , type_name = 'PAP.Address'
        , ui_name = 'Addresses'
        , ui_type_name = 'Address'
        )
    ]

"""

_test_esf = """
    >>> nav_root = create_app () # doctest:+ELLIPSIS
    Cache ...

    >>> nav_root
    <Root : />

    >>> nav_root.ET_Map ["PAP.Company_R"]
    E_Type_Desc (admin = <E_Type Company_R: /Admin/Personenverwaltung/Company_R>, type_name = PAP.Company_R)

    >>> crad     = nav_root.ET_Map ["PAP.Company_R"].admin
    >>> QR       = crad.QR
    >>> afa      = QR.Filter (crad.E_Type, "affiliate")

    >>> print ((formatted (afa)))
    Record
      ( AQ = <affiliate.AQ [Attr.Type.Querier Id_Entity]>
      , Class = 'Entity'
      , attr = Entity `affiliate`
      , attrs =
        [ Record
            ( attr = String `name`
            , full_name = 'affiliate.name'
            , id = 'affiliate__name'
            , name = 'name'
            , sig_key = 3
            , ui_name = 'Affiliate/Name'
            )
        , Record
            ( attr = String `registered_in`
            , full_name = 'affiliate.registered_in'
            , id = 'affiliate__registered_in'
            , name = 'registered_in'
            , sig_key = 3
            , ui_name = 'Affiliate/Registered in'
            )
        , Record
            ( attr = Date_Interval `lifetime`
            , attrs =
              [ Record
                  ( attr = Date `start`
                  , attrs =
                    [ Record
                        ( attr = Int `day`
                        , full_name = 'affiliate.lifetime.start.day'
                        , id = 'affiliate__lifetime__start__day'
                        , name = 'day'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Start/Day'
                        )
                    , Record
                        ( attr = Int `month`
                        , full_name = 'affiliate.lifetime.start.month'
                        , id = 'affiliate__lifetime__start__month'
                        , name = 'month'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Start/Month'
                        )
                    , Record
                        ( attr = Int `year`
                        , full_name = 'affiliate.lifetime.start.year'
                        , id = 'affiliate__lifetime__start__year'
                        , name = 'year'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Start/Year'
                        )
                    ]
                  , full_name = 'affiliate.lifetime.start'
                  , id = 'affiliate__lifetime__start'
                  , name = 'start'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Start'
                  )
              , Record
                  ( attr = Date `finish`
                  , attrs =
                    [ Record
                        ( attr = Int `day`
                        , full_name = 'affiliate.lifetime.finish.day'
                        , id = 'affiliate__lifetime__finish__day'
                        , name = 'day'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Finish/Day'
                        )
                    , Record
                        ( attr = Int `month`
                        , full_name = 'affiliate.lifetime.finish.month'
                        , id = 'affiliate__lifetime__finish__month'
                        , name = 'month'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Finish/Month'
                        )
                    , Record
                        ( attr = Int `year`
                        , full_name = 'affiliate.lifetime.finish.year'
                        , id = 'affiliate__lifetime__finish__year'
                        , name = 'year'
                        , sig_key = 0
                        , ui_name = 'Affiliate/Lifetime/Finish/Year'
                        )
                    ]
                  , full_name = 'affiliate.lifetime.finish'
                  , id = 'affiliate__lifetime__finish'
                  , name = 'finish'
                  , sig_key = 0
                  , ui_name = 'Affiliate/Lifetime/Finish'
                  )
              , Record
                  ( attr = Boolean `alive`
                  , choices =
                    [ 'no'
                    , 'yes'
                    ]
                  , full_name = 'affiliate.lifetime.alive'
                  , id = 'affiliate__lifetime__alive'
                  , name = 'alive'
                  , sig_key = 1
                  , ui_name = 'Affiliate/Lifetime/Alive'
                  )
              ]
            , full_name = 'affiliate.lifetime'
            , id = 'affiliate__lifetime'
            , name = 'lifetime'
            , ui_name = 'Affiliate/Lifetime'
            )
        , Record
            ( attr = String `short_name`
            , full_name = 'affiliate.short_name'
            , id = 'affiliate__short_name'
            , name = 'short_name'
            , sig_key = 3
            , ui_name = 'Affiliate/Short name'
            )
        , Record
            ( Class = 'Entity'
            , attr = Entity `affiliate`
            , full_name = 'affiliate.affiliate'
            , id = 'affiliate__affiliate'
            , name = 'affiliate'
            , sig_key = 2
            , type_name = 'PAP.Company_R'
            , ui_name = 'Affiliate/Affiliate'
            , ui_type_name = 'Company_R'
            )
        , Record
            ( Class = 'Entity'
            , attr = Entity `owner`
            , children_np =
              [ Record
                  ( Class = 'Entity'
                  , attr = Entity `owner`
                  , attrs =
                    [ Record
                        ( attr = String `name`
                        , full_name = 'affiliate.owner[PAP.Company].name'
                        , id = 'affiliate__owner[PAP.Company]__name'
                        , name = 'name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Company]/Name'
                        )
                    , Record
                        ( attr = String `registered_in`
                        , full_name = 'affiliate.owner[PAP.Company].registered_in'
                        , id = 'affiliate__owner[PAP.Company]__registered_in'
                        , name = 'registered_in'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Company]/Registered in'
                        )
                    ]
                  , full_name = 'affiliate.owner[PAP.Company]'
                  , id = 'affiliate__owner[PAP.Company]'
                  , name = 'owner'
                  , sig_key = 2
                  , type_name = 'PAP.Company'
                  , ui_name = 'Affiliate/Owner[Company]'
                  , ui_type_name = 'Company'
                  )
              , Record
                  ( Class = 'Entity'
                  , attr = Entity `owner`
                  , full_name = 'affiliate.owner[PAP.Company_R]'
                  , id = 'affiliate__owner[PAP.Company_R]'
                  , name = 'owner'
                  , sig_key = 2
                  , type_name = 'PAP.Company_R'
                  , ui_name = 'Affiliate/Owner[Company_R]'
                  , ui_type_name = 'Company_R'
                  )
              , Record
                  ( Class = 'Entity'
                  , attr = Entity `owner`
                  , attrs =
                    [ Record
                        ( attr = String `last_name`
                        , full_name = 'affiliate.owner[PAP.Person].last_name'
                        , id = 'affiliate__owner[PAP.Person]__last_name'
                        , name = 'last_name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/Last name'
                        )
                    , Record
                        ( attr = String `first_name`
                        , full_name = 'affiliate.owner[PAP.Person].first_name'
                        , id = 'affiliate__owner[PAP.Person]__first_name'
                        , name = 'first_name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/First name'
                        )
                    , Record
                        ( attr = String `middle_name`
                        , full_name = 'affiliate.owner[PAP.Person].middle_name'
                        , id = 'affiliate__owner[PAP.Person]__middle_name'
                        , name = 'middle_name'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/Middle name'
                        )
                    , Record
                        ( attr = String `title`
                        , full_name = 'affiliate.owner[PAP.Person].title'
                        , id = 'affiliate__owner[PAP.Person]__title'
                        , name = 'title'
                        , sig_key = 3
                        , ui_name = 'Affiliate/Owner[Person]/Academic title'
                        )
                    ]
                  , full_name = 'affiliate.owner[PAP.Person]'
                  , id = 'affiliate__owner[PAP.Person]'
                  , name = 'owner'
                  , sig_key = 2
                  , type_name = 'PAP.Person'
                  , ui_name = 'Affiliate/Owner[Person]'
                  , ui_type_name = 'Person'
                  )
              ]
            , default_child = 'PAP.Person'
            , full_name = 'affiliate.owner'
            , id = 'affiliate__owner'
            , name = 'owner'
            , sig_key = 2
            , type_name = 'PAP.Subject'
            , ui_name = 'Affiliate/Owner'
            , ui_type_name = 'Subject'
            )
        ]
      , edit = None
      , full_name = 'affiliate'
      , id = 'affiliate___AC'
      , name = 'affiliate___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 2
      , type_name = 'PAP.Company_R'
      , ui_name = 'Affiliate'
      , ui_type_name = 'Company_R'
      , value = None
      )

    >>> afos = QR.Filter (crad.E_Type, "owner")
    >>> afos.AQ.E_Type.polymorphic_epk
    True

    >>> print ((formatted (afos)))
    Record
      ( AQ = <owner.AQ [Attr.Type.Querier Id_Entity]>
      , Class = 'Entity'
      , attr = Entity `owner`
      , children_np =
        [ Record
            ( Class = 'Entity'
            , attr = Entity `owner`
            , attrs =
              [ Record
                  ( attr = String `name`
                  , full_name = 'owner[PAP.Company].name'
                  , id = 'owner[PAP.Company]__name'
                  , name = 'name'
                  , sig_key = 3
                  , ui_name = 'Owner[Company]/Name'
                  )
              , Record
                  ( attr = String `registered_in`
                  , full_name = 'owner[PAP.Company].registered_in'
                  , id = 'owner[PAP.Company]__registered_in'
                  , name = 'registered_in'
                  , sig_key = 3
                  , ui_name = 'Owner[Company]/Registered in'
                  )
              ]
            , full_name = 'owner[PAP.Company]'
            , id = 'owner[PAP.Company]'
            , name = 'owner'
            , sig_key = 2
            , type_name = 'PAP.Company'
            , ui_name = 'Owner[Company]'
            , ui_type_name = 'Company'
            )
        , Record
            ( Class = 'Entity'
            , attr = Entity `owner`
            , attrs =
              [ Record
                  ( attr = String `name`
                  , full_name = 'owner[PAP.Company_R].name'
                  , id = 'owner[PAP.Company_R]__name'
                  , name = 'name'
                  , sig_key = 3
                  , ui_name = 'Owner[Company_R]/Name'
                  )
              , Record
                  ( attr = String `registered_in`
                  , full_name = 'owner[PAP.Company_R].registered_in'
                  , id = 'owner[PAP.Company_R]__registered_in'
                  , name = 'registered_in'
                  , sig_key = 3
                  , ui_name = 'Owner[Company_R]/Registered in'
                  )
              ]
            , full_name = 'owner[PAP.Company_R]'
            , id = 'owner[PAP.Company_R]'
            , name = 'owner'
            , sig_key = 2
            , type_name = 'PAP.Company_R'
            , ui_name = 'Owner[Company_R]'
            , ui_type_name = 'Company_R'
            )
        , Record
            ( Class = 'Entity'
            , attr = Entity `owner`
            , attrs =
              [ Record
                  ( attr = String `last_name`
                  , full_name = 'owner[PAP.Person].last_name'
                  , id = 'owner[PAP.Person]__last_name'
                  , name = 'last_name'
                  , sig_key = 3
                  , ui_name = 'Owner[Person]/Last name'
                  )
              , Record
                  ( attr = String `first_name`
                  , full_name = 'owner[PAP.Person].first_name'
                  , id = 'owner[PAP.Person]__first_name'
                  , name = 'first_name'
                  , sig_key = 3
                  , ui_name = 'Owner[Person]/First name'
                  )
              , Record
                  ( attr = String `middle_name`
                  , full_name = 'owner[PAP.Person].middle_name'
                  , id = 'owner[PAP.Person]__middle_name'
                  , name = 'middle_name'
                  , sig_key = 3
                  , ui_name = 'Owner[Person]/Middle name'
                  )
              , Record
                  ( attr = String `title`
                  , full_name = 'owner[PAP.Person].title'
                  , id = 'owner[PAP.Person]__title'
                  , name = 'title'
                  , sig_key = 3
                  , ui_name = 'Owner[Person]/Academic title'
                  )
              ]
            , full_name = 'owner[PAP.Person]'
            , id = 'owner[PAP.Person]'
            , name = 'owner'
            , sig_key = 2
            , type_name = 'PAP.Person'
            , ui_name = 'Owner[Person]'
            , ui_type_name = 'Person'
            )
        ]
      , default_child = 'PAP.Person'
      , edit = None
      , full_name = 'owner'
      , id = 'owner___AC'
      , name = 'owner___AC'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 2
      , type_name = 'PAP.Subject'
      , ui_name = 'Owner'
      , ui_type_name = 'Subject'
      , value = None
      )

    >>> afop = QR.Filter (crad.E_Type, "owner[PAP.Person]")
    >>> afop.AQ.E_Type.polymorphic_epk
    False

    >>> print ((formatted (afop)))
    Record
      ( AQ = <owner[PAP.Person].AQ [Attr.Type.Querier _Id_Entity_NP_]>
      , Class = 'Entity'
      , attr = Entity `owner`
      , attrs =
        [ Record
            ( attr = String `last_name`
            , full_name = 'owner[PAP.Person].last_name'
            , id = 'owner[PAP.Person]__last_name'
            , name = 'last_name'
            , sig_key = 3
            , ui_name = 'Owner[Person]/Last name'
            )
        , Record
            ( attr = String `first_name`
            , full_name = 'owner[PAP.Person].first_name'
            , id = 'owner[PAP.Person]__first_name'
            , name = 'first_name'
            , sig_key = 3
            , ui_name = 'Owner[Person]/First name'
            )
        , Record
            ( attr = String `middle_name`
            , full_name = 'owner[PAP.Person].middle_name'
            , id = 'owner[PAP.Person]__middle_name'
            , name = 'middle_name'
            , sig_key = 3
            , ui_name = 'Owner[Person]/Middle name'
            )
        , Record
            ( attr = String `title`
            , full_name = 'owner[PAP.Person].title'
            , id = 'owner[PAP.Person]__title'
            , name = 'title'
            , sig_key = 3
            , ui_name = 'Owner[Person]/Academic title'
            )
        ]
      , edit = None
      , full_name = 'owner[PAP.Person]'
      , id = 'owner[PAP.Person]'
      , name = 'owner[PAP.Person]'
      , op =
        Record
          ( desc = 'Select entities where the attribute is equal to the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 2
      , type_name = 'PAP.Person'
      , ui_name = 'Owner[Person]'
      , ui_type_name = 'Person'
      , value = None
      )

"""

import os
os.environ.update \
    ( dict
        ( GTW_FULL_OBJECT_MODEL = "True"
        )
    )

from   _GTW.__test__.model      import *

_Ancestor_Essence = GTW.OMP.PAP.Company

class Company_R (_Ancestor_Essence) :
    """Company subcluss to test recursive E_Type attribute"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class affiliate  (A_Id_Entity) :
            """Affiliate of the company"""

            kind               = Attr.Optional
            P_Type             = "GTW.OMP.PAP.Company_R"

        # end class affiliate

        class owner (A_Id_Entity) :
            """Owner of the company"""

            kind               = Attr.Optional
            P_Type             = "GTW.OMP.PAP.Subject"

        # end class affiliate

    # end class _Attributes

# end class Company_R

GTW.OMP.PAP.UI_Spec.Company_R = dict (show_in_admin = True)

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_esf = _test_esf
        , test_nav = _test_nav
        , test_qr  = _test_qr
        )
    )

def _monkey_patch_xmlattr () :
    ### The jinja filter `xmlattr` isn't determistic
    ### Monkey patch to make it determistic: add `sorted`
    from jinja2 import filters as filters

    escape = filters.escape

    @filters.evalcontextfilter
    def do_xmlattr(_eval_ctx, d, autospace=True):
        rv = u' '.join( sorted
            ( u'%s="%s"' % (escape(key), escape(value))
            for key, value in pyk.iteritems (d)
            if value is not None and not isinstance (value, filters.Undefined)
            )
        )
        if autospace and rv:
            rv = u' ' + rv
        if _eval_ctx.autoescape:
            rv = Markup(rv)
        return rv

    filters.FILTERS ["xmlattr"] = do_xmlattr
# end def _monkey_patch_xmlattr

_monkey_patch_xmlattr ()

### __END__ GTW.__test__.NAV

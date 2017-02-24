# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.SRM_Graph
#
# Purpose
#    Test SRM.Graph
#
# Revision Dates
#    17-Aug-2012 (CT) Creation
#     5-Sep-2012 (CT) Add tests for connection guides
#    23-Oct-2012 (CT) Add tests for connection guides for `W`
#    24-Oct-2012 (CT) Improve guide tests
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g = graph (scope.app_type)

    >>> for v in g.nodes () :
    ...   print ("%%-45s %%s" %% (v, v.label))
    <Graph.Link2  SRM.Boat_in_Regatta>            _in_
    <Graph.Link1  SRM.Boat>                       SRM.Boat
    <Graph.Object SRM.Boat_Class>                 SRM.Boat_Class
    <Graph.Link1  SRM.Regatta>                    SRM.Regatta
    <Graph.Object SRM.Regatta_Event>              SRM.Regatta_Event
    <Graph.Object SRM.Club>                       SRM.Club
    <Graph.Link2  SRM.Crew_Member>                SRM.Crew_Member
    <Graph.Link1  SRM.Sailor>                     SRM.Sailor
    <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   _has_
    <Graph.Link1  SRM.Team>                       SRM.Team
    <Graph.Link1  SRM.Regatta_C>                  SRM.Regatta_C
    <Graph.Link1  SRM.Race_Result>                SRM.Race_Result
    <Graph.Object PAP.Person>                     PAP.Person
    <Graph.Object PAP.Subject>                    PAP.Subject

    >>> for v in g.nodes () :
    ...   print ("%%-45s %%s" %% (v, portable_repr (v.label_parts)))
    <Graph.Link2  SRM.Boat_in_Regatta>            ('_in_',)
    <Graph.Link1  SRM.Boat>                       ('SRM', '.Boat')
    <Graph.Object SRM.Boat_Class>                 ('SRM', '.Boat', '_Class')
    <Graph.Link1  SRM.Regatta>                    ('SRM', '.Regatta')
    <Graph.Object SRM.Regatta_Event>              ('SRM', '.Regatta', '_Event')
    <Graph.Object SRM.Club>                       ('SRM', '.Club')
    <Graph.Link2  SRM.Crew_Member>                ('SRM', '.Crew', '_Member')
    <Graph.Link1  SRM.Sailor>                     ('SRM', '.Sailor')
    <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   ('_has_',)
    <Graph.Link1  SRM.Team>                       ('SRM', '.Team')
    <Graph.Link1  SRM.Regatta_C>                  ('SRM', '.Regatta', '_C')
    <Graph.Link1  SRM.Race_Result>                ('SRM', '.Race', '_Result')
    <Graph.Object PAP.Person>                     ('PAP', '.Person')
    <Graph.Object PAP.Subject>                    ('PAP', '.Subject')

    >>> for v in g.nodes (sort_key = TFL.Getter.type_name) :
    ...   print ("%%-45s %%-45s %%s" %% (v, v.anchor, v.pos))
    <Graph.Object PAP.Person>                     <Graph.Link1  SRM.Sailor>                     N*3
    <Graph.Object PAP.Subject>                    <Graph.Object PAP.Person>                     E*2 + N*3
    <Graph.Link1  SRM.Boat>                       <Graph.Link2  SRM.Boat_in_Regatta>            W
    <Graph.Object SRM.Boat_Class>                 <Graph.Link1  SRM.Boat>                       W*2
    <Graph.Link2  SRM.Boat_in_Regatta>            None                                          (0,0)
    <Graph.Object SRM.Club>                       <Graph.Object SRM.Regatta_Event>              NE*2
    <Graph.Link2  SRM.Crew_Member>                <Graph.Link2  SRM.Boat_in_Regatta>            NE
    <Graph.Link1  SRM.Race_Result>                <Graph.Link2  SRM.Boat_in_Regatta>            SW
    <Graph.Link1  SRM.Regatta>                    <Graph.Link2  SRM.Boat_in_Regatta>            E
    <Graph.Link1  SRM.Regatta_C>                  <Graph.Link1  SRM.Team>                       E + S*2
    <Graph.Object SRM.Regatta_Event>              <Graph.Link1  SRM.Regatta>                    E*2
    <Graph.Link1  SRM.Sailor>                     <Graph.Link2  SRM.Boat_in_Regatta>            N*2
    <Graph.Link1  SRM.Team>                       <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   S*2
    <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   <Graph.Link2  SRM.Boat_in_Regatta>            S

    >>> for v in g.nodes (sort_key = TFL.Getter.type_name) :
    ...     print (v.type_name, v.e_type.Roles)
    PAP.Person ()
    PAP.Subject ()
    SRM.Boat (Boat_Class `left`,)
    SRM.Boat_Class ()
    SRM.Boat_in_Regatta (Boat `left`, Regatta `right`)
    SRM.Club ()
    SRM.Crew_Member (Boat_in_Regatta `left`, Sailor `right`)
    SRM.Race_Result (Boat_in_Regatta `left`,)
    SRM.Regatta (Regatta_Event `left`,)
    SRM.Regatta_C (Regatta_Event `left`,)
    SRM.Regatta_Event ()
    SRM.Sailor (Person `left`,)
    SRM.Team (Regatta_C `left`,)
    SRM.Team_has_Boat_in_Regatta (Team `left`, Boat_in_Regatta `right`)

    >>> for v in g.nodes () :
    ...     if v.rel_map :
    ...         for a, l in sorted (pyk.iteritems (v.rel_map)) :
    ...             print (l)
    <Graph.Relation.Role SRM.Boat_in_Regatta.left -> SRM.Boat>
    <Graph.Relation.Role SRM.Boat_in_Regatta.right -> SRM.Regatta>
    <Graph.Relation.Attr SRM.Boat_in_Regatta.skipper -> SRM.Sailor>
    <Graph.Relation.Role SRM.Boat.left -> SRM.Boat_Class>
    <Graph.Relation.Role SRM.Regatta.left -> SRM.Regatta_Event>
    <Graph.Relation.Attr SRM.Regatta_Event.club -> SRM.Club>
    <Graph.Relation SRM.Club IS A PAP.Subject>
    <Graph.Relation.Role SRM.Crew_Member.left -> SRM.Boat_in_Regatta>
    <Graph.Relation.Role SRM.Crew_Member.right -> SRM.Sailor>
    <Graph.Relation.Attr SRM.Sailor.club -> SRM.Club>
    <Graph.Relation.Role SRM.Sailor.left -> PAP.Person>
    <Graph.Relation.Role SRM.Team_has_Boat_in_Regatta.left -> SRM.Team>
    <Graph.Relation.Role SRM.Team_has_Boat_in_Regatta.right -> SRM.Boat_in_Regatta>
    <Graph.Relation.Role SRM.Team.left -> SRM.Regatta_C>
    <Graph.Relation SRM.Regatta_C IS A SRM.Regatta>
    <Graph.Relation.Role SRM.Race_Result.left -> SRM.Boat_in_Regatta>
    <Graph.Relation PAP.Person IS A PAP.Subject>

    >>> for v in g.nodes () :
    ...     if v.rel_map :
    ...         for a, l in sorted (pyk.iteritems (v.rel_map)) :
    ...             print (l.kind, l.source, l.target)
    Role <Graph.Link2  SRM.Boat_in_Regatta> <Graph.Link1  SRM.Boat>
    Role <Graph.Link2  SRM.Boat_in_Regatta> <Graph.Link1  SRM.Regatta>
    Attr <Graph.Link2  SRM.Boat_in_Regatta> <Graph.Link1  SRM.Sailor>
    Role <Graph.Link1  SRM.Boat> <Graph.Object SRM.Boat_Class>
    Role <Graph.Link1  SRM.Regatta> <Graph.Object SRM.Regatta_Event>
    Attr <Graph.Object SRM.Regatta_Event> <Graph.Object SRM.Club>
    IS_A <Graph.Object SRM.Club> <Graph.Object PAP.Subject>
    Role <Graph.Link2  SRM.Crew_Member> <Graph.Link2  SRM.Boat_in_Regatta>
    Role <Graph.Link2  SRM.Crew_Member> <Graph.Link1  SRM.Sailor>
    Attr <Graph.Link1  SRM.Sailor> <Graph.Object SRM.Club>
    Role <Graph.Link1  SRM.Sailor> <Graph.Object PAP.Person>
    Role <Graph.Link2  SRM.Team_has_Boat_in_Regatta> <Graph.Link1  SRM.Team>
    Role <Graph.Link2  SRM.Team_has_Boat_in_Regatta> <Graph.Link2  SRM.Boat_in_Regatta>
    Role <Graph.Link1  SRM.Team> <Graph.Link1  SRM.Regatta_C>
    IS_A <Graph.Link1  SRM.Regatta_C> <Graph.Link1  SRM.Regatta>
    Role <Graph.Link1  SRM.Race_Result> <Graph.Link2  SRM.Boat_in_Regatta>
    IS_A <Graph.Object PAP.Person> <Graph.Object PAP.Subject>

    >>> for v in g.nodes () :
    ...     print ("%%-45s %%-12s %%s" %% (v, v.pos, tuple (v.pos)))
    <Graph.Link2  SRM.Boat_in_Regatta>            (0,0)        (0, 0)
    <Graph.Link1  SRM.Boat>                       W            (-1, 0)
    <Graph.Object SRM.Boat_Class>                 W*2          (-2, 0)
    <Graph.Link1  SRM.Regatta>                    E            (1, 0)
    <Graph.Object SRM.Regatta_Event>              E*2          (2, 0)
    <Graph.Object SRM.Club>                       NE*2         (2, 2)
    <Graph.Link2  SRM.Crew_Member>                NE           (1, 1)
    <Graph.Link1  SRM.Sailor>                     N*2          (0, 2)
    <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   S            (0, -1)
    <Graph.Link1  SRM.Team>                       S*2          (0, -2)
    <Graph.Link1  SRM.Regatta_C>                  E + S*2      (1, -2)
    <Graph.Link1  SRM.Race_Result>                SW           (-1, -1)
    <Graph.Object PAP.Person>                     N*3          (0, 3)
    <Graph.Object PAP.Subject>                    E*2 + N*3    (2, 3)

    >>> ar = Ascii_Renderer (g)

    >>> for v in g.nodes () :
    ...     for a, l in sorted (pyk.iteritems (v.rel_map)) :
    ...       if l.source_connector and l.target_connector :
    ...         print ("%%-30s %%-30s %%-10s %%-10s %%-10s %%1.1s %%5.3f %%1.1s %%5.3f" %% ((
    ...            l.source.type_name, l.target.type_name, l.source.pos, l.target.pos, l.delta) + tuple(l.source_connector) + tuple(l.target_connector)))
    SRM.Boat_in_Regatta            SRM.Boat                       (0,0)      W          E          l 0.500 r 0.500
    SRM.Boat_in_Regatta            SRM.Regatta                    (0,0)      E          W          r 0.500 l 0.500
    SRM.Boat_in_Regatta            SRM.Sailor                     (0,0)      N*2        S*2        t 0.250 b 0.250
    SRM.Boat                       SRM.Boat_Class                 W          W*2        E          l 0.500 r 0.500
    SRM.Regatta                    SRM.Regatta_Event              E          E*2        W          r 0.500 l 0.500
    SRM.Regatta_Event              SRM.Club                       E*2        NE*2       S*2        t 0.500 b 0.500
    SRM.Club                       PAP.Subject                    NE*2       E*2 + N*3  S          t 0.500 b 0.500
    SRM.Crew_Member                SRM.Boat_in_Regatta            NE         (0,0)      NE         l 0.750 t 0.750
    SRM.Crew_Member                SRM.Sailor                     NE         N*2        SE         l 0.250 b 0.750
    SRM.Sailor                     SRM.Club                       N*2        NE*2       W*2        r 0.500 l 0.500
    SRM.Sailor                     PAP.Person                     N*2        N*3        S          t 0.500 b 0.500
    SRM.Team_has_Boat_in_Regatta   SRM.Team                       S          S*2        N          b 0.500 t 0.500
    SRM.Team_has_Boat_in_Regatta   SRM.Boat_in_Regatta            S          (0,0)      S          t 0.750 b 0.750
    SRM.Team                       SRM.Regatta_C                  S*2        E + S*2    W          r 0.500 l 0.500
    SRM.Regatta_C                  SRM.Regatta                    E + S*2    E          S*2        t 0.500 b 0.500
    SRM.Race_Result                SRM.Boat_in_Regatta            SW         (0,0)      SW         t 0.500 b 0.250
    PAP.Person                     PAP.Subject                    N*3        E*2 + N*3  W*2        r 0.500 l 0.500

    >>> for v in g.nodes () :
    ...     for a, l in sorted (pyk.iteritems (v.rel_map)) :
    ...       if l.source_connector and l.target_connector :
    ...         print ("%%-30s %%-30s %%-10s %%-10s %%-10s %%s" %% (
    ...            l.source.type_name, l.target.type_name, l.source.pos, l.target.pos, l.delta, tuple (tuple (tuple (p) for p in g) for g in l.guides)))
    SRM.Boat_in_Regatta            SRM.Boat                       (0,0)      W          E          ()
    SRM.Boat_in_Regatta            SRM.Regatta                    (0,0)      E          W          ()
    SRM.Boat_in_Regatta            SRM.Sailor                     (0,0)      N*2        S*2        ()
    SRM.Boat                       SRM.Boat_Class                 W          W*2        E          ()
    SRM.Regatta                    SRM.Regatta_Event              E          E*2        W          ()
    SRM.Regatta_Event              SRM.Club                       E*2        NE*2       S*2        ()
    SRM.Club                       PAP.Subject                    NE*2       E*2 + N*3  S          ()
    SRM.Crew_Member                SRM.Boat_in_Regatta            NE         (0,0)      NE         (((0, 1), (1, 0)),)
    SRM.Crew_Member                SRM.Sailor                     NE         N*2        SE         (((0, 1), (1, 0)),)
    SRM.Sailor                     SRM.Club                       N*2        NE*2       W*2        ()
    SRM.Sailor                     PAP.Person                     N*2        N*3        S          ()
    SRM.Team_has_Boat_in_Regatta   SRM.Team                       S          S*2        N          ()
    SRM.Team_has_Boat_in_Regatta   SRM.Boat_in_Regatta            S          (0,0)      S          ()
    SRM.Team                       SRM.Regatta_C                  S*2        E + S*2    W          ()
    SRM.Regatta_C                  SRM.Regatta                    E + S*2    E          S*2        ()
    SRM.Race_Result                SRM.Boat_in_Regatta            SW         (0,0)      SW         (((1, 1), (0, 0), (0, -0.25)), ((0, 1), (1, 0), (0, -0.25)))
    PAP.Person                     PAP.Subject                    N*3        E*2 + N*3  W*2        ()

    >>> ar.max_x_spec, ar.max_y_spec
    (2, 3)

    >>> ar.grid_size, ar.node_size
    (Point (32, 12), Point (16, 4))

    >>> ar.transform
    Affine (32, 0, 72, 0, -12, 39)

    >>> ar.max_x, ar.max_y
    (160, 70)

    >>> for n in ar.nodes :
    ...     print ("%%-45s %%-12s %%s" %% (n.entity, tuple (n.pos), tuple (n.entity.pos)))
    <Graph.Link2  SRM.Boat_in_Regatta>            (72, 39)     (0, 0)
    <Graph.Link1  SRM.Boat>                       (40, 39)     (-1, 0)
    <Graph.Object SRM.Boat_Class>                 (8, 39)      (-2, 0)
    <Graph.Link1  SRM.Regatta>                    (104, 39)    (1, 0)
    <Graph.Object SRM.Regatta_Event>              (136, 39)    (2, 0)
    <Graph.Object SRM.Club>                       (136, 15)    (2, 2)
    <Graph.Link2  SRM.Crew_Member>                (104, 27)    (1, 1)
    <Graph.Link1  SRM.Sailor>                     (72, 15)     (0, 2)
    <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   (72, 51)     (0, -1)
    <Graph.Link1  SRM.Team>                       (72, 63)     (0, -2)
    <Graph.Link1  SRM.Regatta_C>                  (104, 63)    (1, -2)
    <Graph.Link1  SRM.Race_Result>                (40, 51)     (-1, -1)
    <Graph.Object PAP.Person>                     (72, 3)      (0, 3)
    <Graph.Object PAP.Subject>                    (136, 3)     (2, 3)

    >>> for n in ar.nodes :
    ...     print ("%%-45s %%-12s %%s %%s" %% (n.entity, n.box.top_left, (n.min_x, n.min_y), (n.max_x, n.max_y)))
    <Graph.Link2  SRM.Boat_in_Regatta>            (72, 39)     (56.0, 19.0) (104.0, 43.0)
    <Graph.Link1  SRM.Boat>                       (40, 39)     (24.0, 39) (56.0, 43.0)
    <Graph.Object SRM.Boat_Class>                 (8, 39)      (8, 39) (24.0, 43.0)
    <Graph.Link1  SRM.Regatta>                    (104, 39)    (104, 39) (136.0, 43.0)
    <Graph.Object SRM.Regatta_Event>              (136, 39)    (136, 19.0) (152.0, 43.0)
    <Graph.Object SRM.Club>                       (136, 15)    (136, 7.0) (152.0, 19.0)
    <Graph.Link2  SRM.Crew_Member>                (104, 27)    (84.0, 19.0) (120.0, 39.0)
    <Graph.Link1  SRM.Sailor>                     (72, 15)     (72, 7.0) (136.0, 19.0)
    <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   (72, 51)     (72, 43.0) (88.0, 63.0)
    <Graph.Link1  SRM.Team>                       (72, 63)     (72, 63) (104.0, 67.0)
    <Graph.Link1  SRM.Regatta_C>                  (104, 63)    (104, 43.0) (120.0, 67.0)
    <Graph.Link1  SRM.Race_Result>                (40, 51)     (40, 43.0) (76.0, 55.0)
    <Graph.Object PAP.Person>                     (72, 3)      (72, 3) (136.0, 7.0)
    <Graph.Object PAP.Subject>                    (136, 3)     (136, 3) (152.0, 7.0)

    >>> for n in ar.nodes :
    ...     for k, l in sorted (pyk.iteritems (n.link_map)) :
    ...         print (l.relation.kind, k, l.source.entity, l.target.entity)
    Role left <Graph.Link2  SRM.Boat_in_Regatta> <Graph.Link1  SRM.Boat>
    Role right <Graph.Link2  SRM.Boat_in_Regatta> <Graph.Link1  SRM.Regatta>
    Attr skipper <Graph.Link2  SRM.Boat_in_Regatta> <Graph.Link1  SRM.Sailor>
    Role left <Graph.Link1  SRM.Boat> <Graph.Object SRM.Boat_Class>
    Role left <Graph.Link1  SRM.Regatta> <Graph.Object SRM.Regatta_Event>
    Attr club <Graph.Object SRM.Regatta_Event> <Graph.Object SRM.Club>
    IS_A IS_A_PAP.Subject <Graph.Object SRM.Club> <Graph.Object PAP.Subject>
    Role left <Graph.Link2  SRM.Crew_Member> <Graph.Link2  SRM.Boat_in_Regatta>
    Role right <Graph.Link2  SRM.Crew_Member> <Graph.Link1  SRM.Sailor>
    Attr club <Graph.Link1  SRM.Sailor> <Graph.Object SRM.Club>
    Role left <Graph.Link1  SRM.Sailor> <Graph.Object PAP.Person>
    Role left <Graph.Link2  SRM.Team_has_Boat_in_Regatta> <Graph.Link1  SRM.Team>
    Role right <Graph.Link2  SRM.Team_has_Boat_in_Regatta> <Graph.Link2  SRM.Boat_in_Regatta>
    Role left <Graph.Link1  SRM.Team> <Graph.Link1  SRM.Regatta_C>
    IS_A IS_A_SRM.Regatta <Graph.Link1  SRM.Regatta_C> <Graph.Link1  SRM.Regatta>
    Role left <Graph.Link1  SRM.Race_Result> <Graph.Link2  SRM.Boat_in_Regatta>
    IS_A IS_A_PAP.Subject <Graph.Object PAP.Person> <Graph.Object PAP.Subject>

    >>> print (ar.render ())
                                                                            +---------------+                                               +---------------+
                                                                            | PAP.Person    |                                               | PAP.Subject   |
                                                                            |               >...............................................>               |
                                                                            |               |                                               |               |
                                                                            +-------^-------+                                               +-------^-------+
                                                                                    |                                                               .
                                                                                    |                                                               .
                                                                                    |                                                               .
                                                                                    |                                                               .
                                                                                    |                                                               .
                                                                                    |                                                               .
                                                                                    |                                                               .
                                                                            +-------^-------+                                               +-------^-------+
                                                                            | SRM.Sailor    |                                               | SRM.Club      |
                                                                            |               >_______________________________________________>               |
                                                                            |               |                                               |               |
                                                                            +---^-------<---+                                               +-------^-------+
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                   +---------------+                       :
                                                                                :       +-------------------< SRM.Crew      |                       :
                                                                                :                           |  _Member      |                       :
                                                                                :       +-------------------<               |                       :
                                                                                :       |                   +---------------+                       :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
                                                                                :       |                                                           :
            +---------------+               +---------------+               +---^-------<---+               +---------------+               +-------^-------+
            | SRM.Boat      |               | SRM.Boat      |               | _in_          |               | SRM.Regatta   |               | SRM.Regatta   |
            |  _Class       <---------------<               <---------------<               >--------------->               >--------------->  _Event       |
            |               |               |               |               |               |               |               |               |               |
            +---------------+               +---------------+               +---^-------^---+               +-------^-------+               +---------------+
                                                                                |       |                           .
                                                                                |       |                           .
                                                                                |       |                           .
                                                                                |       |                           .
                                                                                |       |                           .
                                                                                |       |                           .
                                                    +---------------------------+       |                           .
                                            +-------^-------+               +-----------^---+                       .
                                            | SRM.Race      |               | _has_         |                       .
                                            |  _Result      |               |               |                       .
                                            |               |               |               |                       .
                                            +---------------+               +-------v-------+                       .
                                                                                    |                               .
                                                                                    |                               .
                                                                                    |                               .
                                                                                    |                               .
                                                                                    |                               .
                                                                                    |                               .
                                                                                    |                               .
                                                                            +-------v-------+               +-------^-------+
                                                                            | SRM.Team      |               | SRM.Regatta_C |
                                                                            |               >--------------->               |
                                                                            |               |               |               |
                                                                            +---------------+               +---------------+


    >>> sr = SVG_Renderer (g)
    >>> _ = sr.render ()
    >>> sr.min_x, sr.min_y, sr.max_x, sr.max_y
    (0, 0, 1600, 1750)

    >>> for n in sr.nodes :
    ...     print ("%%-45s %%-12s %%s %%s" %% (n.entity, n.box.top_left, (n.min_x, n.min_y), (n.max_x, n.max_y)))
    <Graph.Link2  SRM.Boat_in_Regatta>            (720, 975)   (560.0, 475.0) (1040.0, 1075.0)
    <Graph.Link1  SRM.Boat>                       (400, 975)   (240.0, 975) (560.0, 1075.0)
    <Graph.Object SRM.Boat_Class>                 (80, 975)    (80, 975) (240.0, 1075.0)
    <Graph.Link1  SRM.Regatta>                    (1040, 975)  (1040, 975) (1360.0, 1075.0)
    <Graph.Object SRM.Regatta_Event>              (1360, 975)  (1360, 475.0) (1520.0, 1075.0)
    <Graph.Object SRM.Club>                       (1360, 375)  (1360, 175.0) (1520.0, 475.0)
    <Graph.Link2  SRM.Crew_Member>                (1040, 675)  (840.0, 475.0) (1200.0, 975.0)
    <Graph.Link1  SRM.Sailor>                     (720, 375)   (720, 175.0) (1360.0, 475.0)
    <Graph.Link2  SRM.Team_has_Boat_in_Regatta>   (720, 1275)  (720, 1075.0) (880.0, 1575.0)
    <Graph.Link1  SRM.Team>                       (720, 1575)  (720, 1575) (1040.0, 1675.0)
    <Graph.Link1  SRM.Regatta_C>                  (1040, 1575) (1040, 1075.0) (1200.0, 1675.0)
    <Graph.Link1  SRM.Race_Result>                (400, 1275)  (400, 1075.0) (760.0, 1375.0)
    <Graph.Object PAP.Person>                     (720, 75)    (720, 75) (1360.0, 175.0)
    <Graph.Object PAP.Subject>                    (1360, 75)   (1360, 75) (1520.0, 175.0)

"""

_test_guides_EN = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_EN = graph_guides (scope.app_type, "E", "N")
    >>> ar   = Ascii_Renderer (g_EN)
    >>> sr   = SVG_Renderer (g_EN)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_EN.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### EN
                                            +---------------+               +---------------+
                                            | _has_         |               | PAP.Phone     |
                                +-----------<               >--------------->               |
                                |           |               |               |               |
                                |           +---------------+               +---------------+
                                |
                                |
                                |
                                |
                                |
                                |
                                |
                                |           +---------------+               +---------------+
                                |           | _has_         |               | PAP.Email     |
                                |   +-------<               >--------------->               |
                                |   |       |               |               |               |
                                |   |       +---------------+               +---------------+
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |       +---------------+               +---------------+
                                |   |       | _has_         |               | PAP.Address   |
                                |   |   +---<               >--------------->               |
                                |   |   |   |               |               |               |
                                |   |   |   +---------------+               +---------------+
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
            +---------------<---+   |   |   +---------------+
            | PAP.Person    <-------+   |   | PAP.Subject   |
            |               <-----------+   |               |
            |               >...............>               |
            +---------------+               +---------------+


"""

_test_guides_ES = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_ES = graph_guides (scope.app_type, "E", "S")
    >>> ar   = Ascii_Renderer (g_ES)
    >>> sr   = SVG_Renderer (g_ES)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_ES.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### ES
            +--------------->...............>---------------+
            | PAP.Person    <-----------+   | PAP.Subject   |
            |               <-------+   |   |               |
            |               <---+   |   |   |               |
            +---------------+   |   |   |   +---------------+
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |
                                |   |   |   +---------------+               +---------------+
                                |   |   |   | _has_         |               | PAP.Address   |
                                |   |   +---<               >--------------->               |
                                |   |       |               |               |               |
                                |   |       +---------------+               +---------------+
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |
                                |   |       +---------------+               +---------------+
                                |   |       | _has_         |               | PAP.Email     |
                                |   +-------<               >--------------->               |
                                |           |               |               |               |
                                |           +---------------+               +---------------+
                                |
                                |
                                |
                                |
                                |
                                |
                                |
                                |           +---------------+               +---------------+
                                |           | _has_         |               | PAP.Phone     |
                                +-----------<               >--------------->               |
                                            |               |               |               |
                                            +---------------+               +---------------+


"""

_test_guides_NE = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_NE = graph_guides (scope.app_type, "N", "E")
    >>> ar   = Ascii_Renderer (g_NE)
    >>> sr   = SVG_Renderer (g_NE)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_NE.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### NE
                                            +---------------+               +---------------+               +---------------+
                                            | PAP.Address   |               | PAP.Email     |               | PAP.Phone     |
                                            |               |               |               |               |               |
                                            |               |               |               |               |               |
                                            +-------^-------+               +-------^-------+               +-------^-------+
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
            +---------------+               +-------^-------+               +-------^-------+               +-------^-------+
            | PAP.Subject   |               | _has_         |               | _has_         |               | _has_         |
            |               |               |               |               |               |               |               |
            |               |               |               |               |               |               |               |
            +-^-------------+               +-------v-------+               +-------v-------+               +-------v-------+
              .   +---------------------------------+                               |                               |
              .   |   +-------------------------------------------------------------+                               |
              .   |   |   +-----------------------------------------------------------------------------------------+
              .   |   |   |
              .   |   |   |
              .   |   |   |
              .   |   |   |
            +-^---v---v---v-+
            | PAP.Person    |
            |               |
            |               |
            +---------------+

"""

_test_guides_NW = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_NW = graph_guides (scope.app_type, "N", "W")
    >>> ar   = Ascii_Renderer (g_NW)
    >>> sr   = SVG_Renderer (g_NW)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_NW.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### NW
            +---------------+               +---------------+               +---------------+
            | PAP.Phone     |               | PAP.Email     |               | PAP.Address   |
            |               |               |               |               |               |
            |               |               |               |               |               |
            +-------^-------+               +-------^-------+               +-------^-------+
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
            +-------^-------+               +-------^-------+               +-------^-------+               +---------------+
            | _has_         |               | _has_         |               | _has_         |               | PAP.Subject   |
            |               |               |               |               |               |               |               |
            |               |               |               |               |               |               |               |
            +-------v-------+               +-------v-------+               +-------v-------+               +-------------^-+
                    |                               |                               +---------------------------------+   .
                    |                               +-------------------------------------------------------------+   |   .
                    +-----------------------------------------------------------------------------------------+   |   |   .
                                                                                                              |   |   |   .
                                                                                                              |   |   |   .
                                                                                                              |   |   |   .
                                                                                                              |   |   |   .
                                                                                                            +-v---v---v---^-+
                                                                                                            | PAP.Person    |
                                                                                                            |               |
                                                                                                            |               |
                                                                                                            +---------------+


"""

_test_guides_SE = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_SE = graph_guides (scope.app_type, "S", "E")
    >>> ar   = Ascii_Renderer (g_SE)
    >>> sr   = SVG_Renderer (g_SE)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_SE.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### SE
            +---------------+
            | PAP.Person    |
            |               |
            |               |
            +-v---^---^---^-+
              .   |   |   |
              .   |   |   |
              .   |   |   |
              .   |   |   |
              .   |   |   +-----------------------------------------------------------------------------------------+
              .   |   +-------------------------------------------------------------+                               |
              .   +---------------------------------+                               |                               |
            +-v-------------+               +-------^-------+               +-------^-------+               +-------^-------+
            | PAP.Subject   |               | _has_         |               | _has_         |               | _has_         |
            |               |               |               |               |               |               |               |
            |               |               |               |               |               |               |               |
            +---------------+               +-------v-------+               +-------v-------+               +-------v-------+
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                                    |                               |                               |
                                            +-------v-------+               +-------v-------+               +-------v-------+
                                            | PAP.Address   |               | PAP.Email     |               | PAP.Phone     |
                                            |               |               |               |               |               |
                                            |               |               |               |               |               |
                                            +---------------+               +---------------+               +---------------+

"""

_test_guides_SW = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_SW = graph_guides (scope.app_type, "S", "W")
    >>> ar   = Ascii_Renderer (g_SW)
    >>> sr   = SVG_Renderer (g_SW)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_SW.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### SW
                                                                                                            +---------------+
                                                                                                            | PAP.Person    |
                                                                                                            |               |
                                                                                                            |               |
                                                                                                            +-^---^---^---v-+
                                                                                                              |   |   |   .
                                                                                                              |   |   |   .
                                                                                                              |   |   |   .
                                                                                                              |   |   |   .
                    +-----------------------------------------------------------------------------------------+   |   |   .
                    |                               +-------------------------------------------------------------+   |   .
                    |                               |                               +---------------------------------+   .
            +-------^-------+               +-------^-------+               +-------^-------+               +-------------v-+
            | _has_         |               | _has_         |               | _has_         |               | PAP.Subject   |
            |               |               |               |               |               |               |               |
            |               |               |               |               |               |               |               |
            +-------v-------+               +-------v-------+               +-------v-------+               +---------------+
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
                    |                               |                               |
            +-------v-------+               +-------v-------+               +-------v-------+
            | PAP.Phone     |               | PAP.Email     |               | PAP.Address   |
            |               |               |               |               |               |
            |               |               |               |               |               |
            +---------------+               +---------------+               +---------------+


"""

_test_guides_WN = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_WN = graph_guides (scope.app_type, "W", "N")
    >>> ar   = Ascii_Renderer (g_WN)
    >>> sr   = SVG_Renderer (g_WN)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_WN.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### WN
            +---------------+               +---------------+
            | PAP.Phone     |               | _has_         |
            |               <---------------<               >-----------+
            |               |               |               |           |
            +---------------+               +---------------+           |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
            +---------------+               +---------------+           |
            | PAP.Email     |               | _has_         |           |
            |               <---------------<               >-------+   |
            |               |               |               |       |   |
            +---------------+               +---------------+       |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
            +---------------+               +---------------+       |   |
            | PAP.Address   |               | _has_         |       |   |
            |               <---------------<               >---+   |   |
            |               |               |               |   |   |   |
            +---------------+               +---------------+   |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                            +---------------+   |   |   +--->---------------+
                                            | PAP.Subject   |   |   +-------> PAP.Person    |
                                            |               |   +----------->               |
                                            |               <...............<               |
                                            +---------------+               +---------------+


"""

_test_guides_WS = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g_WS = graph_guides (scope.app_type, "W", "S")
    >>> ar   = Ascii_Renderer (g_WS)
    >>> sr   = SVG_Renderer (g_WS)
    >>> _    = sr.render ()
    >>> with open ("/tmp/guides_WS.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)
    >>> print (ar.render ()) ### WS
                                            +---------------<...............<---------------+
                                            | PAP.Subject   |   +-----------> PAP.Person    |
                                            |               |   |   +------->               |
                                            |               |   |   |   +--->               |
                                            +---------------+   |   |   |   +---------------+
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
                                                                |   |   |
            +---------------+               +---------------+   |   |   |
            | PAP.Address   |               | _has_         |   |   |   |
            |               <---------------<               >---+   |   |
            |               |               |               |       |   |
            +---------------+               +---------------+       |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
                                                                    |   |
            +---------------+               +---------------+       |   |
            | PAP.Email     |               | _has_         |       |   |
            |               <---------------<               >-------+   |
            |               |               |               |           |
            +---------------+               +---------------+           |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
                                                                        |
            +---------------+               +---------------+           |
            | PAP.Phone     |               | _has_         |           |
            |               <---------------<               >-----------+
            |               |               |               |
            +---------------+               +---------------+


"""

_test_svg = """
    >>> from _GTW._OMP._SRM.graph import graph
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> g  = graph (scope.app_type)
    >>> sr = SVG_Renderer (g)
    >>> _  = sr.render ()
    >>> with open ("/tmp/srm.svg", "wb") as f :
    ...    sr.canvas.write_to_xml_stream (f)

"""

from _GTW.__test__.model        import *

from _MOM._Graph.Ascii          import Renderer as Ascii_Renderer
from _MOM._Graph.SVG            import Renderer as SVG_Renderer
from _MOM._Graph.Spec           import Attr, Child, ET, IS_A, Role, Skip

from _TFL._D2                   import Cardinal_Direction as CD

def graph_guides (app_type, n1 = "N", n2 = "E") :
    d1 = getattr (CD, n1)
    d2 = getattr (CD, n2)
    return MOM.Graph.Spec.Graph \
        ( app_type
        , ET.PAP.Person
           ( IS_A.PAP.Subject
               ( offset       = d1
               , source_side  = n1
               )
           , ET.PAP.Person_has_Address
               ( Role.left  (source_side = str (-d1), target_side = n1)
               , Role.right (offset = d1)
               , offset       = d1 + d2
               )
           , ET.PAP.Person_has_Email
               ( Role.left  (source_side = str (-d1), target_side = n1)
               , Role.right (offset = d1)
               , offset       = d1 + d2 * 2
               )
           , ET.PAP.Person_has_Phone
               ( Role.left  (source_side = str (-d1), target_side = n1)
               , Role.right (offset = d1)
               , offset       = d1 + d2 * 3
               )
           )
        )
# end def graph_guides

def graph (app_type) :
    return MOM.Graph.Spec.Graph \
        ( app_type
        , ET.SRM.Boat_in_Regatta
            ( Role.left
                ( Role.left (offset = CD.W)
                , offset = CD.W
                )
            , Role.right
                ( Role.left
                    ( Attr.club (offset = CD.N * 2)
                    , offset = CD.E
                    )
                , offset = CD.E
                )
            , ET.SRM.Crew_Member
                ( Role.left  (anchor = False, source_side = "W")
                , Role.right (anchor = False, source_side = "W")
                , offset = CD.NE
                )
            , ET.SRM.Team_has_Boat_in_Regatta
                ( Role.left
                    ( ET.SRM.Regatta_C
                        ( IS_A.SRM.Regatta
                        , offset = CD.E
                        )
                    , offset = CD.S
                    )
                , offset = CD.S
                )
            , ET.SRM.Race_Result (offset = CD.SW)
            , Attr.skipper
                ( Role.left
                    ( IS_A.PAP.Subject (offset = CD.E * 2)
                    , offset = CD.N
                    )
                , Attr.club (IS_A.PAP.Subject)
                , offset = CD.N * 2
                )
            )
        )
# end def graph

__test__ = Scaffold.create_test_dict \
  ( dict
      ( main       = _test_code
      , guides_NE  = _test_guides_NE
      , guides_EN  = _test_guides_EN
      , guides_SE  = _test_guides_SE
      , guides_ES  = _test_guides_ES
      , guides_WN  = _test_guides_WN
      , guides_NW  = _test_guides_NW
      , guides_WS  = _test_guides_WS
      , guides_SW  = _test_guides_SW
      , svg        = _test_svg
      )
  )

### __END__ GTW.__test__.SRM_Graph

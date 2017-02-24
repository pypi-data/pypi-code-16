# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package CAL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    CAL.G8R
#
# Purpose
#    Reverse localization, i.e., globalization, for calendary names
#
# Revision Dates
#    10-Feb-2016 (CT) Creation
#    12-Feb-2016 (CT) Factor `Week_Day_Abbrs`
#    15-Feb-2016 (CT) Add `yearday`, `nlyearday`, `leapdays`
#    15-Feb-2016 (CT) Add test for `localized`
#    15-Feb-2016 (CT) Use `G8R_Multi`, not `Multi_Re_Replacer`
#    15-Jun-2016 (CT) Add `Recurrence_Units`
#    30-Nov-2016 (CT) Factor `Month_Abbrs`, `Month_Names`,
#                     `Week_Day_Abbrs_3`, and `Week_Day_Names`
#    30-Nov-2016 (CT) Use title-case for `Month_Abbrs`, `Month_Names`
#    30-Nov-2016 (CT) Use `LC`
#                     + Remove `lowercase` from `Months`, `Recurrence_Units`
#                       and all week-day related instances
#     1-Dec-2016 (CT) Factor `Units_Abs`, `Units_Abs_Abbr`, `Units_Delta`,
#                     `Units_YD`
#    ««revision-date»»···
#--

r"""
G8R provides globalizer objects for the names of months and weekdays and for
calendary units. The globalizers translate strings in the currently selected
language to the primary language (which often is english).

    >>> from _TFL.portable_repr import portable_repr
    >>> import _CAL.G8R

    >>> mr1 = "März-Mai"
    >>> mr2 = "Jan, März, Mai, Dez"
    >>> wr1 = "Mo-Mi, Do, SO"
    >>> wr2 = "MI(-1)"
    >>> ur1 = "2 Tage 5 Stunden 3 min 5 sek"
    >>> ur2 = "2 tage 5 stunden 3 MIN 5 SEK"
    >>> ur3 = "2Tage 5Stunden 3min 5sek"
    >>> ur4 = "2Tage5Stunden3min5sek"

    >>> _show  (CAL.G8R.Months, mr1)
    de : März-Mai --> March-May

    >>> _show  (CAL.G8R.Months.LC, mr1)
    de : März-Mai --> march-may

    >>> _show  (CAL.G8R.Months, mr2, localized_p = True)
    de : Jan, März, Mai, Dez --> Jan, March, May, Dec --> Jän, März, Mai, Dez

    >>> _show  (CAL.G8R.Months.LC, mr2)
    de : Jan, März, Mai, Dez --> jan, march, may, dec

    >>> _show (CAL.G8R.Week_Days, wr1)
    de : Mo-Mi, Do, SO --> Mo-We, Th, SO

    >>> _show (CAL.G8R.Week_Days.LC, wr1)
    de : Mo-Mi, Do, SO --> mo-we, th, su

    >>> _show (CAL.G8R.Week_Days, wr2)
    de : MI(-1) --> MI(-1)

    >>> _show (CAL.G8R.Week_Days.LC, wr2)
    de : MI(-1) --> we(-1)

    >>> _show (CAL.G8R.Units, ur1)
    de : 2 Tage 5 Stunden 3 min 5 sek --> 2 days 5 hours 3 min 5 sec

    >>> _show (CAL.G8R.Units, ur1.lower ())
    de : 2 tage 5 stunden 3 min 5 sek --> 2 days 5 hours 3 min 5 sec

    >>> _show (CAL.G8R.Units, ur2, localized_p = True)
    de : 2 tage 5 stunden 3 MIN 5 SEK --> 2 days 5 hours 3 min 5 sec --> 2 tage 5 stunden 3 min 5 sek

    >>> _show (CAL.G8R.Units, ur3)
    de : 2Tage 5Stunden 3min 5sek --> 2days 5hours 3min 5sec

    >>> _show (CAL.G8R.Units, ur4, localized_p = True)
    de : 2Tage5Stunden3min5sek --> 2days5hours3min5sec --> 2tage5stunden3min5sek

    >>> with TFL.I18N.test_language ("de") :
    ...    CAL.G8R.All (mr1) == CAL.G8R.Months.LC (mr1)
    True

    >>> with TFL.I18N.test_language ("de") :
    ...    CAL.G8R.All (mr2) == CAL.G8R.Months.LC (mr2)
    True

    >>> with TFL.I18N.test_language ("de") :
    ...    CAL.G8R.All (wr1) == CAL.G8R.Week_Days.LC (wr1)
    True

    >>> with TFL.I18N.test_language ("de") :
    ...    CAL.G8R.All (ur1) == CAL.G8R.Units (ur1)
    True

    >>> _show (CAL.G8R.All, "; ".join ([mr2, wr1, "2t 30m"]), localized_p = True)
    de : Jan, März, Mai, Dez; Mo-Mi, Do, SO; 2t 30m --> jan, march, may, dec; mo-we, th, su; 2d 30m --> jän, märz, mai, dez; mo-mi, do, so; 2t 30m

    >>> with TFL.I18N.test_language ("de") :
    ...    print (portable_repr (sorted (CAL.G8R.Months.keys)))
    ['Apr', 'April', 'Aug', 'August', 'Dec', 'December', 'Feb', 'February', 'Jan', 'January', 'Jul', 'July', 'Jun', 'June', 'Mar', 'March', 'May', 'Nov', 'November', 'Oct', 'October', 'Sep', 'September']

    >>> with TFL.I18N.test_language ("de") :
    ...    print (portable_repr (sorted (CAL.G8R.Months.map.items ())))
    [('Dez', 'Dec'), ('Dezember', 'December'), ('Feber', 'February'), ('Juli', 'July'), ('Juni', 'June'), ('J\xe4n', 'Jan'), ('J\xe4nner', 'January'), ('Mai', 'May'), ('M\xe4r', 'Mar'), ('M\xe4rz', 'March'), ('Okt', 'Oct'), ('Oktober', 'October')]

    >>> with TFL.I18N.test_language ("de") :
    ...    print (portable_repr (sorted (CAL.G8R.Months.LC.map.items ())))
    [('dez', 'dec'), ('dezember', 'december'), ('feber', 'february'), ('juli', 'july'), ('juni', 'june'), ('j\xe4n', 'jan'), ('j\xe4nner', 'january'), ('mai', 'may'), ('m\xe4r', 'mar'), ('m\xe4rz', 'march'), ('okt', 'oct'), ('oktober', 'october')]

    >>> with TFL.I18N.test_language ("de") :
    ...    print (CAL.G8R.Months.replacer.regexp._pattern.pattern)
    \b(Dezember|Oktober|J\änner|Feber|Juli|Juni|M\ärz|Dez|J\än|Mai|M\är|Okt)\b

    >>> with TFL.I18N.test_language ("de") :
    ...    print (CAL.G8R.Months.LC.replacer.regexp._pattern.pattern)
    \b(dezember|oktober|j\änner|feber|juli|juni|m\ärz|dez|j\än|mai|m\är|okt)\b

    >>> with TFL.I18N.test_language ("de") :
    ...    print (CAL.G8R.Units.replacer.regexp._pattern.pattern)
    (?:\b|(?<=\d))(mikrosekunden|mikrosekunde|schalttage|wochentag|sekunden|jahrtag|minuten|quartal|sekunde|stunden|monate|stunde|wochen|jahre|monat|woche|jahr|tage|sek|tag|kw|j|t)(?:\b|(?=\d))

    >>> with TFL.I18N.test_language ("de") :
    ...    print (portable_repr (sorted (CAL.G8R.Week_Days.keys)))
    ['Fr', 'Fri', 'Friday', 'Mo', 'Mon', 'Monday', 'Sa', 'Sat', 'Saturday', 'Su', 'Sun', 'Sunday', 'Th', 'Thu', 'Thursday', 'Tu', 'Tue', 'Tuesday', 'We', 'Wed', 'Wednesday']

    >>> with TFL.I18N.test_language ("de") :
    ...    print (portable_repr (sorted (CAL.G8R.Week_Days.map.items ())))
    [('Di', 'Tu'), ('Dienstag', 'Tuesday'), ('Do', 'Th'), ('Donnerstag', 'Thursday'), ('Fr', 'Fri'), ('Freitag', 'Friday'), ('Mi', 'We'), ('Mittwoch', 'Wednesday'), ('Mo', 'Mo'), ('Montag', 'Monday'), ('Sa', 'Sa'), ('Samstag', 'Saturday'), ('So', 'Su'), ('Sonntag', 'Sunday'), ('fr', 'Fr')]

    >>> with TFL.I18N.test_language ("de") :
    ...    print (portable_repr (sorted (CAL.G8R.Week_Days.LC.map.items ())))
    [('di', 'tu'), ('dienstag', 'tuesday'), ('do', 'th'), ('donnerstag', 'thursday'), ('fr', 'fr'), ('freitag', 'friday'), ('mi', 'we'), ('mittwoch', 'wednesday'), ('mo', 'mo'), ('montag', 'monday'), ('sa', 'sa'), ('samstag', 'saturday'), ('so', 'su'), ('sonntag', 'sunday')]

    >>> with TFL.I18N.test_language ("de") :
    ...    print (CAL.G8R.Week_Days.replacer.regexp._pattern.pattern)
    \b(Donnerstag|Dienstag|Mittwoch|Freitag|Samstag|Sonntag|Montag|Di|Do|Fr|Mi|Mo|Sa|So|fr)\b

    >>> with TFL.I18N.test_language ("de") :
    ...    print (CAL.G8R.Week_Days.LC.replacer.regexp._pattern.pattern)
    \b(donnerstag|dienstag|mittwoch|freitag|samstag|sonntag|montag|di|do|fr|mi|mo|sa|so)\b

    >>> _show (CAL.G8R.Recurrence_Units, "weekly")
    de : weekly --> weekly

    >>> _show (CAL.G8R.Recurrence_Units, "Wöchentlich")
    de : Wöchentlich --> Weekly

    >>> _show (CAL.G8R.Recurrence_Units.LC, "Wöchentlich")
    de : Wöchentlich --> weekly

    >>> with TFL.I18N.test_language ("de") :
    ...     print (portable_repr (sorted (CAL.G8R.Recurrence_Units.map.items ())))
    [('J\xe4hrlich', 'Yearly'), ('Monatlich', 'Monthly'), ('T\xe4glich', 'Daily'), ('W\xf6chentlich', 'Weekly')]

    >>> with TFL.I18N.test_language ("de") :
    ...     print (portable_repr (sorted (CAL.G8R.Recurrence_Units.LC.map.items ())))
    [('j\xe4hrlich', 'yearly'), ('monatlich', 'monthly'), ('t\xe4glich', 'daily'), ('w\xf6chentlich', 'weekly')]

"""

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                       import CAL
from   _TFL                       import TFL

from   _TFL.I18N                  import _

import _TFL.G8R

Month_Abbrs = TFL.G8R \
    ( [ _("Jan"), _("Feb"), _("Mar"), _("Apr"), _("May"), _("Jun")
      , _("Jul"), _("Aug"), _("Sep"), _("Oct"), _("Nov"), _("Dec")
      ]
    )

Month_Names = TFL.G8R \
    ( [ _("January"), _("February"), _("March")
      , _("April"),   _("May"),      _("June")
      , _("July"),    _("August"),   _("September")
      , _("October"), _("November"), _("December")
      ]
    )

Months = TFL.G8R (Month_Abbrs.words, Month_Names.words)

Recurrence_Units = TFL.G8R \
    ( [ _("Daily"), _("Weekly"), _("Monthly"), _("Yearly")])

Units_Abs = TFL.G8R \
    ( [_("year"), _("month"),  _("day")]
    , [_("hour"), _("minute"), _("second"), _ ("microsecond")]
    , lowercase = True
    , re_head   = r"(?:\b|(?<=\d))" # look-behind assertion must be fixed width
    , re_tail   = r"(?:\b|(?=\d))"
    )

Units_Abs_Abbr = TFL.G8R \
    ( [_("y"), _("d")]
    , [_("h"), _("m"), _("min"), _("s"), _("sec")]
    , lowercase = True
    , re_head   = r"(?:\b|(?<=\d))" # look-behind assertion must be fixed width
    , re_tail   = r"(?:\b|(?=\d))"
    )

Units_Delta = TFL.G8R \
    ( [_("years"), _("months"),  _("days")]
    , [_("hours"), _("minutes"), _("seconds"), _ ("microseconds")]
    , lowercase = True
    , re_head   = r"(?:\b|(?<=\d))" # look-behind assertion must be fixed width
    , re_tail   = r"(?:\b|(?=\d))"
    )

Units_YD = TFL.G8R \
    ( [_("yearday"), _("nlyearday"), _("leapdays")]
    , lowercase = True
    , re_head   = r"(?:\b|(?<=\d))" # look-behind assertion must be fixed width
    , re_tail   = r"(?:\b|(?=\d))"
    )

Units = TFL.G8R \
    ( Units_Abs.words
    , Units_Abs_Abbr.words
    , Units_Delta.words
    , [ _("wk"), _("week"),  _("weeks"), _("weekday")]
    , [ _("q"),  _("quarter")]
    , Units_YD.words
    , lowercase = True
    , re_head   = r"(?:\b|(?<=\d))" # look-behind assertion must be fixed width
    , re_tail   = r"(?:\b|(?=\d))"
    )

Week_Day_Abbrs_2 = TFL.G8R \
    ( [ _("Mo"), _("Tu"), _("We"), _("Th"), _("Fr"), _("Sa"), _("Su")]
    , re_tail    = r"(?:\b|(?=\(-?\d+\)))"
    )

Week_Day_Abbrs_3 = TFL.G8R \
    ( [ _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun")])

Week_Day_Names   = TFL.G8R \
    ( [ _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday")
      , _("Friday"), _("Saturday"), _("Sunday")
      ]
    )

Week_Days = TFL.G8R \
    ( Week_Day_Abbrs_2.words, Week_Day_Abbrs_3.words, Week_Day_Names.words)

All = TFL.G8R_Multi (Units.LC, Months.LC, Week_Days.LC)

def _show (g8r, text, lang = "de", localized_p = False) :
    with TFL.I18N.test_language (lang) :
        globalized = g8r.globalized (text)
        result = (lang, ":", text, "-->", globalized)
        if localized_p :
            result += ("-->", g8r.localized (globalized))
        print (* result)
# end def _show

if __name__ != "__main__" :
    CAL._Export_Module ()
### __END__ CAL.G8R

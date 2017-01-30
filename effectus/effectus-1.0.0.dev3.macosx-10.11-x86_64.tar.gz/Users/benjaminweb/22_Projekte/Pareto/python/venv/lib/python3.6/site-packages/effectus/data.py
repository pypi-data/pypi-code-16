"""Example data sets from real life."""
import csv
from pkg_resources import resource_filename

from effectus.helpers import get_values, unfold_values


def get_data(filepath):
    """Read and unfold value-frequency mappings from file.

    Args:
        filepath: File path to source file.

    Returns:
        A list with unfolded values.
    """
    with open(resource_filename(__name__, filepath), 'r') as csvfile:
        reader = csv.reader(csvfile)
        vafreqs = get_values(reader)
        return unfold_values(vafreqs)


MISSING_TEETH = get_data('csv/missing_teeth.csv')
"""Number of missing teeth of 966 young German adults (35 to 44 years).

Source: `Institute of German Dentists, Cologne`_: Fifth German Oral Health Study
(DMS V), ISBN 978-3-7691-0020-4.

.. _Institute of German Dentists, Cologne: http://www.idz-koeln.de
"""

BELLS = tuple(get_data('csv/bells.csv'))
"""Weights of 9,605 church bells in kg of the German
archbishoprics of `Cologne`_, `Aachen`_ and `Essen`_.

Source: expert-HOFFMANN GmbH, Köln, 2016.

.. _Cologne: http://glockenbuecherebk.de
.. _Aachen: http://www.glockenbuecherbaac.de
.. _Essen: http://www.glockenbuecherbes.de
"""

WOMEN_INTERCOURSE = tuple(get_data('csv/women_intercourse.csv'))
"""Number of vaginal sex partners of 11,110 women.

Source: Jakob Pastötter, Nicolas Drey, Anthony Pryce: Sex Study 2008 - Sexual
Behaviour in Germany. DGSS and City University London.
"""

BOXOFFICE = tuple(get_data('csv/boxoffice.csv'))
"""Boxoffice revenue of 4,189 movies in US Dollars.

Source: `OMDb`_.

.. _OMDb: https://github.com/rstudio/shiny-examples/tree/master/051-movie-explorer
"""

WKZS = tuple(get_data('csv/wkzs.csv'))
"""Area designated for wind power usage in ha in 315 of 396
municipalities of North Rhine Westphalia, Germany 2012-2016.
The remaining municipalities do not have designated any area
for wind power usage.

Source: State Office for Nature, Environment and Consumer
  Affairs of North-Rhine Westphalia (`LANUV`_) based on data
  of planning regions; municipalities mentioned below, 2016.
  The data may not be complete for some parts. Data state for
  planning regions Münster, Arnsberg und Köln: July 2015,
  Detmold: June 2015. RVR: Late 2014, Düsseldorf: January 2011.
  Municipalities Anröchte, Drensteinfurt, Drolshagen, Eslohe
  (Sauerland), Hemer, Kaarst, Lippstadt, Mettmann, Metelen,
  Warendorf, Wickede (Ruhr), Wülfrath: 2016.

.. _LANUV: http://lanuv.nrw.de
"""

OIL_RESERVES = (55.0, 172.2, 10.8, 2.4, 13.0, 2.3, 8.0, 1.4, 0.7, 300.9, 0.5,
                7.0, 0.6, 0.6, 30.0, 8.0, 0.6, 102.4, 0.6, 2.8, 0.6, 2.1, 157.8,
                143.1, 101.5, 5.3, 25.7, 266.6, 2.5, 97.8, 3.0, 0.2, 12.2, 12.7,
                1.5, 1.6, 3.5, 1.1, 2.0, 48.4, 37.1, 3.5, 1.5, 0.4, 3.7, 4.0,
                1.1, 18.5, 5.7, 3.6, 3.6, 0.4, 4.4, 1.3)
"""Proved reserves of oil in million barrels per country, end of 2015.

Source: `BP Statistical Review of World Energy`_, June 2016.

.. _BP Statistical Review of World Energy: http://www.bp.com/statisticalreview
"""

OIL_CONSUMPTION = (19396, 2322, 1926, 23644, 679, 3157, 368, 331, 253, 243, 38,
                   678, 1336, 7083, 263, 99, 145, 661, 88, 200, 165, 177, 1606,
                   2338, 303, 154, 143, 1262, 271, 54, 835, 234, 546, 243, 191,
                   3113, 78, 1226, 299, 228, 835, 146, 183, 1559, 59, 677,
                   18380, 1947, 239, 531, 324, 3895, 901, 1733, 9570, 422, 824,
                   649, 1993, 3888, 1006, 112, 11968, 368, 4159, 1628, 4150,
                   831, 159, 517, 399, 1339, 2575, 1031, 1344, 422, 436, 32444)
"""Daily Oil consumption in thousand barrels per country, 2015.

Source: `BP Statistical Review of World Energy`_, June 2016.

.. _BP Statistical Review of World Energy: http://www.bp.com/statisticalreview
"""

CO2 = (5485.7, 532.5, 474.2, 190.0, 487.8, 90.1, 97.3, 37.1, 50.8, 26.7, 169.2,
       227.7, 62.8, 32.0, 56.3, 111.5, 45.2, 98.6, 37.6, 41.3, 309.4, 753.6,
       73.9, 44.2, 38.6, 341.5, 184.8, 11.2, 210.1, 36.7, 295.8, 52.5, 70.7,
       1483.2, 31.1, 291.7, 47.8, 39.1, 336.3, 92.6, 195.1, 436.9, 115.4,
       225.1, 630.2, 74.4, 107.9, 111.1, 624.5, 264.7, 355.1, 137.1, 212.1,
       436.5, 416.2, 400.2, 72.9, 9153.9, 91.2, 2218.4, 611.4, 1207.8, 246.9,
       35.7, 179.5, 106.5, 205.0, 648.7, 268.5, 295.9, 169.0, 155.2)
"""Carbon dioxide emissions in million tonnes per country, 2015.

Source: `BP Statistical Review of World Energy`_, June 2016.

.. _BP Statistical Review of World Energy: http://www.bp.com/statisticalreview
"""

SP500 = tuple(get_data('csv/sp500.csv'))
# pragma pylint: disable=line-too-long
"""Daily positive returns of S&P500 index from 1960 through 2015.

Negative returns have been replaced with zero.

Source: `Yahoo Finance`_, 2016.

.. _Yahoo Finance: http://finance.yahoo.com/quote/%5EGSPC/history?period1=-315622800&period2=1451516400&interval=1d&filter=history&frequency=1d
"""

GDP = tuple(get_data('csv/gdp.csv'))
"""Gross domestic product in billion U.S. dollars per country, 2014
(partly staff estimates; without Syria.)

Source: International Monetary Fund: `World Economic Outlook Database`_ , October 2016.

.. _World Economic Outlook Database: http://www.imf.org/external/pubs/ft/weo/2016/02/weodata/index.aspx
"""

EURO_COINS = (0.01*32734, 0.02*25114, 0.05*19509, 0.1*14148, 0.2*10778, 0.5*5901, 1*6977, 2*5815)
"""Nominal value of Euro coins in circulation in million Euro as per December 2016.

Source: European Central Bank: `Banknotes and coins circulation`_, 2017.

.. _Banknotes and coins circulation: http://www.ecb.europa.eu/stats/money/euro/circulation/html/index.en.html
"""

EURO_BANKNOTES = (5*1805, 10*2387, 20*3590, 50*9231, 100*2433, 200*234, 500*540)
"""Nominal value of Euro bank notes in circulation in million Euro as per December 2016.

Source: European Central Bank: `Banknotes and coins circulation`_, 2017.

.. _Banknotes and coins circulation: http://www.ecb.europa.eu/stats/money/euro/circulation/html/index.en.html
"""

HOPEI_RAIN = tuple(get_data('csv/hopei_rain.csv'))
"""
Daily precipitation in mm on Hohenpeißenberg, Germany
(the world's oldest mountain weather station) from 1781 to 2015.

Source: `German Meteorological Office`_, 2016.

.. _German Meteorological Office: http://www.dwd.de
"""

HOPEI_SUN = tuple(get_data('csv/hopei_sun.csv'))
"""
Daily sun hours on Hohenpeißenberg, Germany
(the world's oldest mountain weather station) from 1937 to 2015.

Source: `German Meteorological Office`_, 2016.

.. _German Meteorological Office: http://www.dwd.de
"""

GERMAN_RIVERS = (1236, 1091, 866, 744, 524, 371, 300, 290, 256, 220, 219, 208,
                 188, 185, 182, 176, 169, 166, 165, 153, 153, 150, 143, 128,
                 124, 121, 118, 114, 107, 105, 105, 102, 101, 97, 97, 92, 91,
                 90, 80, 75, 73, 72, 72, 70, 68, 68, 67, 67, 65, 67, 63, 63,
                 62, 62, 61, 60, 60, 59, 59, 58, 57, 57, 57, 57, 57, 56, 55,
                 54, 52, 52, 52, 51, 50, 49, 49, 49, 48, 47, 47, 46, 45, 45,
                 45, 45, 45, 44, 43, 42, 42, 40, 40, 40, 40, 40, 40, 40, 39,
                 39, 38, 37, 37, 37, 36, 35, 35, 35, 35, 35, 35, 34, 34, 34,
                 34, 33, 33, 33, 33, 32, 31, 31, 31, 31, 30, 30, 30, 30, 30,
                 30, 30, 30, 30, 30, 29, 29, 29, 28, 28, 28, 28, 28, 28, 27,
                 27, 27, 27, 27, 26, 26, 26, 25, 25, 25, 25, 25, 25, 25, 25,
                 24, 24, 24, 24, 24, 23, 23, 23, 23, 23, 22, 22, 22, 22, 22,
                 22, 22, 22, 22, 22, 22, 22, 21, 21, 21, 21, 21, 21, 21, 21,
                 21, 20, 20, 20, 20, 20, 19, 18, 18, 18, 18, 18, 18, 18, 18,
                 17, 17, 17, 17, 17, 17, 16, 16, 16, 16, 16, 16, 16, 16, 16,
                 16, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 14,
                 14, 14, 13, 13, 13, 13, 13, 13, 13, 13, 12, 12, 12, 12, 12,
                 12, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
                 11, 10, 10, 10, 10)
"""Lengths of 267 longest German rivers in km.

Source: `Wikipedia`_, 2016.

.. _Wikipedia: https://de.wikipedia.org/w/index.php?title=Liste_von_Flüssen_in_Deutschland&oldid=158665390
"""

GERMAN_MOTORWAYS = tuple(get_data('csv/german_motorways.csv'))
"""Lengths of 120 German federal motorways (Autobahnen) in km.

Source: `Bundesanstalt für Straßenwesen`_, 2016.

.. _Bundesanstalt für Straßenwesen: http://www.bast.de
"""

GERMAN_HIGHWAYS = tuple(get_data('csv/german_highways.csv'))
"""Lengths of 393 German federal highways (Bundesstraßen) in km.

Source: `Bundesanstalt für Straßenwesen`_, 2016.

.. _Bundesanstalt für Straßenwesen: http://www.bast.de
"""

COUNTRIES_AREA = tuple(get_data('csv/countries_area.csv'))
"""Country area of 257 countries in square kilometres.

Source: Central Intelligence Agency: `The World Factbook, Country Comparison, Area`_, 2016.

.. _The World Factbook, Country Comparison, Area: https://www.cia.gov/library/publications/the-world-factbook/rankorder/2147rank.html
"""

COUNTRIES_POPULATION = tuple(get_data('csv/countries_population.csv'))
"""Country population of 238 countries.

Source: Central Intelligence Agency: `The World Factbook, Country Comparison, Population`_, July 2016 estimate.

.. _The World Factbook, Country Comparison, Population: https://www.cia.gov/library/publications/resources/the-world-factbook/rankorder/2119rank.html
"""

# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius                                                                     #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides currency and other utilities.                          #
#                                                                              #
# copyright (C) 2017 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

from __future__ import division

name    = "denarius"
version = "2017-03-08T1411Z"

import ast
import datetime
import json
import time
import urllib2

import currency_converter
import dataset
import datavision
import numpy
import pyprel
import shijian

def value_Bitcoin(
    price    = "last",
    currency = "EUR"
    ):

    return ticker_Bitcoin(
        currency = currency
    )[price]

    if day:
        URL = URL_day
    if hour:
        URL = URL_hour

    # Access a Bitcoin ticker.
    file_URL                = urllib2.urlopen(URL)
    data_string             = file_URL.read()
    # Convert the data from string to dictionary.
    data_dictionary_strings = ast.literal_eval(data_string)
    #
    #    example hour ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1000.6,
    #        'last':      999.31,
    #        'low':       996.67,
    #        'open':      990.0,
    #        'timestamp': 1487600377.0,
    #        'volume':    21.11748617,
    #        'vwap':      998.34
    #    }
    #
    #    example day ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1004.0,
    #        'last':      999.31,
    #        'low':       985.31,
    #        'open':      990.0,
    #        'timestamp': 1487600340.0,
    #        'volume':    324.21451971,
    #        'vwap':      996.27
    #    }
    #
    # Convert numbers from strings to floats.
    data_dictionary = dict()
    for key in data_dictionary_strings:
        data_dictionary[key] = float(data_dictionary_strings[key])
    if currency != "EUR":
        # Convert currency EUR to requested currency.
        data_dictionary_currency = dict()
        converter_currency = currency_converter.CurrencyConverter()
        for key in data_dictionary:
            if key == "timestamp":
                data_dictionary_currency[key] = data_dictionary[key]
            else:
                data_dictionary_currency[key] =\
                    converter_currency.convert(
                        data_dictionary_strings[key],
                        "EUR",
                        currency
                    )
        return data_dictionary_currency
    return data_dictionary

def fluctuation_value_Bitcoin(
    days                      = 10,
    factor_standard_deviation = 3.5,
    details                   = False
    ):

    data_Bitcoin = data_historical_Bitcoin(
        days        = days,
        return_list = True
    )
    value_current_Bitcoin = value_Bitcoin()
    values_Bitcoin = [float(element[1]) for element in data_Bitcoin]
    mean_Bitcoin               = numpy.array(values_Bitcoin).mean()
    standard_deviation_Bitcoin = numpy.array(values_Bitcoin).std()
    low_Bitcoin  =\
        mean_Bitcoin - factor_standard_deviation * standard_deviation_Bitcoin
    high_Bitcoin =\
        mean_Bitcoin + factor_standard_deviation * standard_deviation_Bitcoin

    if details:
        print("Bitcoin values from last {days} days:\n\n{values}\n".format(
            days   = days,
            values = ", ".join([str(element) for element in values_Bitcoin])
        ))
        print("high bound Bitcoin:    {value}".format(value = high_Bitcoin))
        print("Bitcoin current value: {value}".format(
            value = value_current_Bitcoin
        ))
        print("low bound Bitcoin:     {value}".format(value = low_Bitcoin))

    if low_Bitcoin <= value_current_Bitcoin <= high_Bitcoin:
        return False
    else:
        return True

def ticker_Bitcoin(
    URL_hour = "https://www.bitstamp.net/api/v2/ticker/btceur",
    URL_day  = "https://www.bitstamp.net/api/v2/ticker_hour/btceur",
    currency = "EUR",
    hour     = True,
    day      = False
    ):

    if day:
        URL = URL_day
    if hour:
        URL = URL_hour

    # Access a Bitcoin ticker.
    file_URL                = urllib2.urlopen(URL)
    data_string             = file_URL.read()
    # Convert the data from string to dictionary.
    data_dictionary_strings = ast.literal_eval(data_string)
    #
    #    example hour ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1000.6,
    #        'last':      999.31,
    #        'low':       996.67,
    #        'open':      990.0,
    #        'timestamp': 1487600377.0,
    #        'volume':    21.11748617,
    #        'vwap':      998.34
    #    }
    #
    #    example day ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1004.0,
    #        'last':      999.31,
    #        'low':       985.31,
    #        'open':      990.0,
    #        'timestamp': 1487600340.0,
    #        'volume':    324.21451971,
    #        'vwap':      996.27
    #    }
    #
    # Convert numbers from strings to floats.
    data_dictionary = dict()
    for key in data_dictionary_strings:
        data_dictionary[key] = float(data_dictionary_strings[key])
    if currency != "EUR":
        # Convert currency EUR to requested currency.
        data_dictionary_currency = dict()
        converter_currency = currency_converter.CurrencyConverter()
        for key in data_dictionary:
            if key == "timestamp":
                data_dictionary_currency[key] = data_dictionary[key]
            else:
                data_dictionary_currency[key] =\
                    converter_currency.convert(
                        data_dictionary_strings[key],
                        "EUR",
                        currency
                    )
        return data_dictionary_currency
    return data_dictionary

def data_historical_Bitcoin(
    URL               = "https://api.coindesk.com/v1/bpi/historical/close.json",
    currency          = "EUR",
    date_start        = None, # YYYY-MM-DD
    date_stop         = None, # YYYY-MM-DD
    days              = None, # last days (start/stop dates alternative)
    return_list       = False,
    return_UNIX_times = False,
    sort_reverse      = False
    ):

    if days:
        time_current = datetime.datetime.utcnow()
        date_stop    = time_current.strftime("%Y-%m-%d")
        date_start   = (time_current -\
                       datetime.timedelta(days = days)).strftime("%Y-%m-%d")
    # Construct the URL using the API (http://www.coindesk.com/api/).
    URL = URL + "?currency=" + currency
    if date_start is not None and date_stop is not None:
        URL = URL + "&start=" + date_start + "&end=" + date_stop
    # Access the online data.
    file_URL                = urllib2.urlopen(URL)
    data_string             = file_URL.read()
    # Convert the data from string to dictionary.
    data_dictionary_strings = ast.literal_eval(data_string)

    if return_list or return_UNIX_times:
        data_dictionary_list = list()
        for key in data_dictionary_strings["bpi"]:
            if return_UNIX_times:
                date = int(
                    time.mktime(
                        datetime.datetime.strptime(
                            key,
                            "%Y-%m-%d"
                        ).timetuple()
                    )
                )
            else:
                date = key
            data_dictionary_list.append(
                [date, float(data_dictionary_strings["bpi"][key])]
            )
        # sort
        data_dictionary_list_tmp = sorted(
            data_dictionary_list,
            key = lambda data_dictionary_list: (
                      data_dictionary_list[0],
                      data_dictionary_list[1]
                  ),
            reverse = sort_reverse
        )
        data_dictionary_list = data_dictionary_list_tmp
        return data_dictionary_list
    else:
        return data_dictionary_strings

def table_Bitcoin(
    currency   = "EUR",
    date_start = None, # YYYY-MM-DD
    date_stop  = None, # YYYY-MM-DD
    UNIX_times = False
    ):

    # Get Bitcoin value data.
    data = data_historical_Bitcoin(
        currency          = currency,
        date_start        = None, # YYYY-MM-DD
        date_stop         = None, # YYYY-MM-DD
        return_UNIX_times = UNIX_times,
        return_list       = True
    )
    
    # Return a table of the Bitcoin value data.
    table_contents = [[
                         "time",
                         "Bitcoin value ({currency})".format(
                             currency = currency
                         )
                     ]]
    table_contents.extend(data)
    table = pyprel.Table(
                contents = table_contents
            )
    return table

def save_graph_Bitcoin(
    currency   = "EUR",
    filename   = None,
    directory  = ".",
    overwrite  = True,
    date_start = None, # YYYY-MM-DD
    date_stop  = None, # YYYY-MM-DD
    days       = None  # last days (start/stop dates alternative)
    ):

    if filename is None:
        filename = "Bitcoin_value_{currency}_versus_time.png".format(
            currency = currency
        )

    data = data_historical_Bitcoin(
        currency          = currency,
        date_start        = date_start, # YYYY-MM-DD
        date_stop         = date_stop,  # YYYY-MM-DD
        days              = days,
        return_UNIX_times = True
    )

    datavision.save_graph_matplotlib(
        values       = data,
        title_axis_x = "time",
        title_axis_y = "value ({currency})".format(
                           currency = currency
                       ),
        filename     = filename,
        directory    = directory,
        overwrite    = overwrite,
        line         = True,
        line_width   = 0.5,
        time_axis_x  = True
    )

def graph_TTY_Bitcoin(
    currency   = "EUR",
    date_start = None, # YYYY-MM-DD
    date_stop  = None, # YYYY-MM-DD
    days       = None  # last days (start/stop dates alternative)
    ):

    data = data_historical_Bitcoin(
        currency          = currency,
        date_start        = date_start, # YYYY-MM-DD
        date_stop         = date_stop,  # YYYY-MM-DD
        days              = days,
        return_UNIX_times = True
    )
    x = [element[0] for element in data]
    y = [element[1] for element in data]
    plot = datavision.TTYFigure()
    tmp = plot.plot(
        x,
        y,
        marker = "_o",
        plot_slope = False
    )
    return tmp

def create_database(
    filename = None
    ):

    os.system(
        "sqlite3 " + \
        filename + \
        " \"create table aTable(field1 int); drop table aTable;\""
    )

def access_database(
    filename = "database.db"
    ):

    database = dataset.connect("sqlite:///" + str(filename))
    return database

def save_database_Bitcoin(
    filename   = "database.db",
    date_start = "2010-07-17",
    date_stop  = None
    ):

    if date_stop is None:
        date_stop = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    data = data_historical_Bitcoin(
        date_start        = date_start,
        date_stop         = date_stop,
        return_list       = True,
        return_UNIX_times = True
    )
    database = access_database(filename = filename)
    table    = database["Bitcoin"]
    progress = shijian.Progress()
    progress.engage_quick_calculation_mode()
    number_of_entries = len(data)
    for index, element in enumerate(data):
        table.insert(dict(
            time      = element[0],
            value_EUR = element[1]
        ))
        print(progress.add_datum(fraction = index / number_of_entries))

def table_database(
    filename           = "database.db",
    name_table         = "Bitcoin",
    include_attributes = None,
    rows_limit         = None
    ):

    database = access_database(filename = filename)

    return pyprel.Table(
        contents = pyprel.table_dataset_database_table(
            table              = database[name_table],
            include_attributes = include_attributes,
            rows_limit         = rows_limit
        )
    )

def values_Bitcoin_LocalBitcoin(
    URL = "https://localbitcoins.com/buy-bitcoins-online/"
          "GB/united-kingdom/national-bank-transfer/.json"
    ):

    file_URL    = urllib2.urlopen(URL)
    data_string = file_URL.read()
    data_JSON   = json.loads(data_string)

    advertisements = data_JSON["data"]["ad_list"]
    advertisement_prices = []
    for advertisement in advertisements:
        advertisement_prices.append(float(advertisement["data"]["temp_price"]))
    advertisement_prices.sort()
    return advertisement_prices

def save_current_values_LocalBitcoins_to_database(
    filename   = "database_LocalBitcoins.db"
    ):

    # Data saved to the database is a UTC datetime timestamp, a UTC UNIX,
    # timestamp, the LocalBitcoins API string returned (JSON) and a list of the
    # current prices in GBP.

    timestamp      = datetime.datetime.utcnow()
    timestamp_UNIX = (timestamp -\
                     datetime.datetime.utcfromtimestamp(0)).total_seconds()

    URL = "https://localbitcoins.com/buy-bitcoins-online/"\
          "GB/united-kingdom/national-bank-transfer/.json"

    file_URL    = urllib2.urlopen(URL)
    data_string = file_URL.read()
    data_JSON   = json.loads(data_string)

    advertisements = data_JSON["data"]["ad_list"]
    advertisement_prices = []
    for advertisement in advertisements:
        advertisement_prices.append(float(advertisement["data"]["temp_price"]))
    advertisement_prices.sort()

    database = access_database(filename = filename)
    table    = database["LocalBitcoins"]

    table.insert(dict(
        time        = timestamp,
        time_UNIX   = timestamp_UNIX,
        JSON_GB_NBT = str(data_string),
        values_GBP  = str(advertisement_prices)
    ))

def loop_save_current_values_LocalBitcoins_to_database(
    filename    = "database_LocalBitcoins.db",
    time_period = 1800, # seconds (30 minutes)
    verbose     = True
    ):

    while True:
        if verbose:
            print(
                "{time} save LocalBitcoins current data to database "\
                "{filename} (next save in {seconds} s)".format(
                    time     = datetime.datetime.utcnow(),
                    filename = filename,
                    seconds  = time_period
                )
            )
        save_current_values_LocalBitcoins_to_database(
            filename = filename
        )
        time.sleep(time_period)

def table_database_LocalBitcoins(
    filename           = "database_LocalBitcoins.db",
    name_table         = "LocalBitcoins",
    include_attributes = ["time", "time_UNIX", "values_GBP"],
    rows_limit         = None
    ):

    return table_database(
        filename           = filename,
        name_table         = name_table,
        include_attributes = include_attributes,
        rows_limit         = rows_limit
    )

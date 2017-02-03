#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import getopt
import string
import csv
import re
import xml.etree.ElementTree as ET
import adsutils
import keys
import regexputils
import csvutils
import alertutils


def parse_session(INPUT_FILE, OUTPUT_FILE):

    try:
        tree = ET.parse(INPUT_FILE)
    except IOError:
        print 'ERROR: Cannot find file \'' + INPUT_FILE + '\''
        sys.exit(2)
    except ET.ParseError:
        print 'ERROR: File \'' + INPUT_FILE + '\' doesn\'t appear to be in the correct format. Make sure you export your Charles session as an XML Session File (File > Export Session... > Format: XML Session File)'
        sys.exit(2)
    root = tree.getroot()


    first_request = True
    startTimeMillis = 0
    requestNum = 1
    ad = 1
    activity_list = []

    for transaction in root.iter('transaction'):
        # initalize
        trans_dict = dict.fromkeys(keys.keys, '')
        for attribute in transaction.attrib:
            if attribute in keys.keys:
                trans_dict[attribute] = transaction.attrib[attribute]
        trans_dict['request'] = requestNum
        requestNum += 1

        # edge case for "CONNECT" requests
        if trans_dict['method'].lower() == 'connect':
            trans_dict['latency'] = 0

        #size
        trans_dict['totalSizeKB'] = float(trans_dict['totalSize']) / 1024.0

        # timings
        if first_request:
            startTimeMillis = int(trans_dict['startTimeMillis'])
            first_request = False
        trans_dict['startTime'] = regexputils.extractRegex(r'T([\d:]*)'
                , trans_dict['startTime'])
        trans_dict['relativeStart'] = int(trans_dict['startTimeMillis'
                ]) - startTimeMillis
        if trans_dict['status'].lower() == 'complete':
            trans_dict['relativeEnd'] = int(trans_dict['endTimeMillis'
                    ]) - startTimeMillis
            trans_dict['requestBeginTime'] = \
                regexputils.extractRegex(r'T([\d:]*)',
                    trans_dict['requestBeginTime'])
            trans_dict['requestTime'] = \
                regexputils.extractRegex(r'T([\d:]*)',
                    trans_dict['requestTime'])
            trans_dict['responseTime'] = \
                regexputils.extractRegex(r'T([\d:]*)',
                    trans_dict['responseTime'])
            trans_dict['endTime'] = \
                regexputils.extractRegex(r'T([\d:]*)',
                    trans_dict['endTime'])

        # referrer
        for header in transaction.iter('header'):
            for name in header.findall('name'):
                if name.text == 'Referer':
                    trans_dict['referer'] = header.find('value').text

        # Google ads
        if adsutils.isGoogleAds(transaction) and trans_dict['status'].lower() \
            == 'complete':
            trans_dict['type'] = 'googleads' + '/' \
                + adsutils.getType(transaction)
            if adsutils.getType(transaction) == 'ad':
                query = trans_dict['query']
                trans_dict['ad_number'] = ad
                ad += 1
                trans_dict['ad_type'] = adsutils.getAdType(transaction)
                print 'query: ' + query
                trans_dict['network_id'] = regexputils.extractRegex(r'iu_parts=(\d*)', query) if not re.search(r'iu=%2F([^%]*)', query) else regexputils.extractRegex(r'iu=%2F([^%]*)', query)
                trans_dict['ad_unit'] = '' if not re.search(r'iu=%2F\d*%2F([^&]*)', query) else re.sub('%2F', '/', regexputils.extractRegex(r'iu=%2F\d*%2F([^&]*)', query))
                trans_dict['cust_params'] = re.sub('%26', '&',
                        re.sub('%3D', '=',
                        regexputils.extractRegex(r'cust_params=([^&]*)'
                        , query)))
                trans_dict['seq_num'] = \
                    regexputils.extractRegex(r'seq_num=([^&]*)', query)
                trans_dict['size'] = re.sub('%7C', '|', regexputils.extractRegex(r'prev_iu_szs=([^&]*)', query)) if not re.search(r'sz=([^&]*)', query) else re.sub('%7C', '|', regexputils.extractRegex(r'sz=([^&]*)', query))
                trans_dict['content_url'] = \
                    regexputils.extractRegex(r'url=([^&]*)', query)

                # capture what is returned
                for header in transaction.iter('header'):
                    for name in header.findall('name'):
                        if name.text == 'User-Agent':
                            ua = header.find('value').text
                            match = \
                                re.search(r'afma-sdk-[ai]-v([\w.-]*)',
                                    ua)
                            if match != None:
                                trans_dict['sdk_version'] = \
                                    match.group(1)
                        if name.text == 'google-lineitem-id':
                            trans_dict['lineitems'] = header.find('value').text
                        if name.text == 'google-creative-id':
                            trans_dict['creatives'] = header.find('value').text
                        if name.text == 'X-Afma-Ad-Size':
                            trans_dict['ad_size'] = header.find('value'
                                    ).text
                        if name.text == 'X-Afma-Ad-Slot-Size':
                            trans_dict['ad_slot_size'] = \
                                header.find('value').text
                        if name.text == 'X-Afma-Debug-Dialog':
                            value = header.find('value').text
                            match = \
                                re.search(r'Creatives=([\d,]*)&Lineitems=([\d,]*)'
                                    , value).groups()
                            creatives = match[0]
                            lineitems = match[1]
                            trans_dict['creatives'] = creatives
                            trans_dict['lineitems'] = lineitems
                        if name.text == 'X-Afma-ActiveView':
                            val = header.find('value').text
                            match = re.search(r'click_string":"([^"]*)'
                                    , val)
                            if match:
                                trans_dict['click_string'] = \
                                    match.group(1)

            # activeview ping
            if adsutils.getType(transaction) == 'activeview':
                match = re.search(r'avi=([^&]*)',
                                  transaction.get('query'))
                if match:
                    trans_dict['click_string'] = match.group(1)
        else:
            trans_dict['type'] = transaction.findall('response'
                    )[0].get('mime-type')
        activity_list.append(trans_dict)

    # find matching activeview pings
    for item1 in activity_list:
        print item1
        if item1['type'] == 'googleads/ad':
            item1_avcid = item1['click_string']
            if item1_avcid != '':
                for item2 in activity_list:
                    if item2['type'] == 'googleads/activeview' \
                        and item1_avcid == item2['click_string']:
                        item1['av_request'] = item2['request']
                        item2['av_request'] = item1['request']
        item1['alerts'] = alertutils.getAlerts(item1)

    # print to CSV
    csvutils.writeCSV(OUTPUT_FILE, activity_list)

    # summary metrics
    metrics = set(['latency', 'duration', 'totalSize', 'overallSpeed'])
    stats = ['max', 'min', 'sum', 'avg']
    hosts = set()
    summary_stats = {}
    summary_output = []
    ads = 0
    ads_fill = 0
    ads_display = 0
    ads_video = 0
    ads_native = 0
    ads_viewed = 0
    totalSize = 0
    totalDuration = 0
    totalRequests = 0

    for item in activity_list:
        hosts.add(item['host'])

    for host in hosts:
        host_stats = dict.fromkeys(metrics)
        for metric in metrics:
            host_stats[metric] = dict.fromkeys(stats, 0)
        host_stats['count'] = 0
        host_stats['host'] = host
        summary_stats[host] = host_stats

    for host in summary_stats:
        #print host
        # min, max, sum
        for item in activity_list:
            #print 'item host: ' + item['host']
            #print 'item status: ' + item['status']
            if item['host'] == host and item['status'].lower() == 'complete':
                summary_stats[host]['count'] += 1
                totalRequests += 1
                for metric in metrics:
                    #print metric
                    # min
                    if summary_stats[host][metric]['min'] == 0 \
                        or summary_stats[host][metric]['min'] \
                        > int(item[metric]):
                        summary_stats[host][metric]['min'] = \
                            int(item[metric])
                    # max
                    if summary_stats[host][metric]['max'] == 0 \
                        or summary_stats[host][metric]['max'] \
                        < int(item[metric]):
                        summary_stats[host][metric]['max'] = \
                            int(item[metric])
                    summary_stats[host][metric]['sum'] += \
                        int(item[metric])
                    if metric == 'totalSize':
                        #print int(item[metric])
                        totalSize += int(item[metric])
                    if metric == 'duration':
                        totalDuration += int(item[metric])

        # get averages
        for metric in metrics:
            if summary_stats[host]['count'] == 0:
                summary_stats[host][metric]['avg'] = 'n/a'
                summary_stats[host][metric]['min'] = 'n/a'
                summary_stats[host][metric]['max'] = 'n/a'
            elif metric == 'overallSpeed':
                summary_stats[host][metric]['avg'] = \
                    summary_stats[host]['totalSize']['sum'] \
                    / summary_stats[host]['duration']['sum'] * 1024
            else:
                summary_stats[host][metric]['avg'] = \
                    summary_stats[host][metric]['sum'] \
                    / summary_stats[host]['count']

    print '\n----SUMMARY----'
    print '  Total requests\t' + str(totalRequests)
    print '  Total duration\t' + adsutils.formatSec(totalDuration)  # '{:.2f} sec'.format(float(totalDuration)/1000)
    print '  Total size\t\t' + adsutils.formatSize(totalSize)  # '{:.2f} MB'.format(float(totalSize)/(1024*1024))
    print '  Average speed\t\t' + adsutils.formatSpeedTtl(totalSize, totalDuration)

    print '\n----Non-Google Domains----'
    for host in summary_stats:
        if host not in adsutils.gdomains:
            print '\nSummary for ' + host + ':'
            print '  Requests \t' + str(summary_stats[host]['count'])
            print '\t\tmin\tavg\tmax\tttl'
            s = '  {4}\t{0}\t{1}\t{2}\t{3}'
            for metric in metrics:
                ttl = ''
                if metric in ('duration', 'totalSize', 'latency'):
                    ttl = summary_stats[host][metric]['sum']
                if metric in ('duration', 'latency'):
                    print s.format(str(summary_stats[host][metric]['min'
                                   ]),
                                   str(summary_stats[host][metric]['avg'
                                   ]),
                                   str(summary_stats[host][metric]['max'
                                   ]), str(ttl), metric + ' (ms)')
                if metric == 'totalSize':
                    print s.format(adsutils.formatSizeKB(summary_stats[host][metric]['min'
                                   ]),
                                   adsutils.formatSizeKB(summary_stats[host][metric]['avg'
                                   ]),
                                   adsutils.formatSizeKB(summary_stats[host][metric]['max'
                                   ]), adsutils.formatSizeKB(ttl),
                                   'Size (KB)')
                if metric == 'overallSpeed':
                    print s.format(adsutils.formatSpeed(summary_stats[host][metric]['min'
                                   ]),
                                   adsutils.formatSpeed(summary_stats[host][metric]['avg'
                                   ]),
                                   adsutils.formatSpeed(summary_stats[host][metric]['max'
                                   ]), ttl, 'Speed (KB/s)')

    print '\n----Google Domains----'
    for host in summary_stats:
        if host in adsutils.gdomains:
            print '\nSummary for ' + host + ':'
            print '  Requests \t' + str(summary_stats[host]['count'])
            print '\t\tmin\tavg\tmax\tttl'
            s = '  {4}\t{0}\t{1}\t{2}\t{3}'
            for metric in metrics:
                ttl = ''
                if metric in ('duration', 'totalSize', 'latency'):
                    ttl = summary_stats[host][metric]['sum']
                if metric in ('duration', 'latency'):
                    print s.format(str(summary_stats[host][metric]['min'
                                   ]),
                                   str(summary_stats[host][metric]['avg'
                                   ]),
                                   str(summary_stats[host][metric]['max'
                                   ]), str(ttl), metric + ' (ms)')
                if metric == 'totalSize':
                    print s.format(adsutils.formatSizeKB(summary_stats[host][metric]['min'
                                   ]),
                                   adsutils.formatSizeKB(summary_stats[host][metric]['avg'
                                   ]),
                                   adsutils.formatSizeKB(summary_stats[host][metric]['max'
                                   ]), adsutils.formatSizeKB(ttl),
                                   'Size (KB)')
                if metric == 'overallSpeed':
                    print s.format(adsutils.formatSpeed(summary_stats[host][metric]['min'
                                   ]),
                                   adsutils.formatSpeed(summary_stats[host][metric]['avg'
                                   ]),
                                   adsutils.formatSpeed(summary_stats[host][metric]['max'
                                   ]), ttl, 'Speed (KB/s)')

    for item in activity_list:
        #print 'item host: {}, type: {}'.format(item['host'], item['type'])
        if item['type'] == 'googleads/ad':
            ads += 1
            if item['creatives'] != '':
                ads_fill += 1
                if item['ad_type'] == 'video':
                    ads_video += 1
                if item['ad_type'] == 'display':
                    ads_display += 1
                if item['ad_type'] == 'native':
                    ads_native += 1
        if item['type'] == 'googleads/activeview':
            ads_viewed += 1

    print '\n----Ads Summary----'
    print '  Ad requests:\t' + str(ads)
    print '  Filled req:\t' + str(ads_fill)
    print '  Viewed ads:\t' + str(ads_viewed)
    print '  Display ads:\t' + str(ads_display)
    print '  Native ads:\t' + str(ads_native)
    print '  Video ads:\t' + str(ads_video)
    print ''
    print 'Parsing complete! Created file \'' + OUTPUT_FILE + '\' for analysis.' 


if __name__ == "__main__":
   main(sys.argv[1:])


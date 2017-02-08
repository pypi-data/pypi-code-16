# -*- coding: utf-8 -*-
import re
from collections import defaultdict, namedtuple
from datetime import datetime, timedelta

from .proxy import init_proxy

Timelog = namedtuple('Timelog', ['issue_id', 'hours', 'spent_on', 'activity_id', 'comments'])


def merge_sieblings(timelogs, logger):
    merged_timelogs = []

    # Pop timelogs and group them by (issue, date) pair
    D = defaultdict(list)

    for x in range(len(timelogs) - 1, -1, -1):
        timelog = timelogs.pop()
        D[(timelog.issue_id, timelog.spent_on)].append(timelog)

    # Merge back
    for k, v in list(D.items()):
        if len(v) == 1:
            rhours = v[0].hours
            t = Timelog(v[0][0], rhours, v[0][2], v[0][3], v[0][4])
            merged_timelogs.append(t)
        elif len(v) > 1:
            mhours = 0
            mcomments = ''
            for timelog in v:
                c = timelog.comments.strip()
                mhours += timelog.hours
                if mcomments.find(c) == -1:
                    mcomments += (c + '|')
                mactivity = timelog.activity_id
            mcomments = mcomments.rstrip('|')
            merged_timelogs.append(Timelog(k[0], mhours, k[1], mactivity, mcomments))

    return merged_timelogs


def round_timelogs(timelogs):
    rounded_timelogs = []

    for t in timelogs:
        rhours = round_hours(t.hours)
        rt = Timelog(issue_id=t.issue_id, hours=rhours,
                     spent_on=t.spent_on,
                     activity_id=t.activity_id,
                     comments=t.comments)
        rounded_timelogs.append(rt)

    return rounded_timelogs


def round_hours(hours):
    return round(hours * 4) / 4


def get_batch_timelogs(logger, config, batch, input, date, all):
    '''
    gtimelog/utt format (read from input):
        2016-12-04 05:00: arrived
        2016-12-04 05:45: 12345 bake breakfast
        2016-12-04 06:30: 12346 shower
        2016-12-04 07:15: 12347 walk the spiders
        2016-12-04 08:00: 12348 fix the hamsters
        2016-12-04 09:00: 12349 stick the stickers
        2016-12-04 09:15: 12346 shower
        2016-12-04 12:00: 12347 clean the dumpsters
        2016-12-04 12:45: 12346 shower**
        2016-12-04 13:15: lunch ***
        2016-12-04 13:45: 12346 shower
    '''

    logger.debug('importing input-file-fed timelogs, {} format'.format(batch))
    activity_id = config['user']['activity_id']

    timelogs = []
    t0 = [0, 0]
    for line in input:
        line_strip = line.strip()
        if not line_strip:
            continue
        logger.debug(u'playing on line: {}'.format(line_strip))
        try:
            raw_date, raw_time, raw_issue = line_strip.split(' ', 2)
        except(ValueError):
            raise ValueError('Stumbled on line {}'.format(line_strip))

        raw_time = raw_time.rstrip(':')
        record_date = vali_date(raw_date)
        record_time = convert_time_string(raw_time)
        record_issue = raw_issue
        logger.debug('working on batch line record_date: {} record_time: {}'.format(record_date, record_time))

        # off focus
        if not all and (record_date != date):
            continue

        # reset day
        elif t0 == [0, 0]:
            logger.debug('new day: {}'.format(record_date))
            t0 = [record_date, record_time]
            continue
        else:
            assert(t0[0] == record_date)
            current_time = datetime.combine(datetime(1, 1, 1, 0, 0, 0), record_time)
            previous_time = datetime.combine(datetime(1, 1, 1, 0, 0, 0), t0[1])
            time_diff = current_time - previous_time
            t0[1] = record_time  # reset timer

            # off-records
            if batch == 'gtl' and record_issue.startswith('**'):
                continue  # only gtimelog accepts starting ** as escape sequence
            if record_issue.endswith('**'):
                continue

            logger.debug('New timelog! {} record_date: {} record_time: {}'
                         .format(t0, record_date, record_time))
            # add timelog
            hours = time_diff.total_seconds() / timedelta(hours=1).total_seconds()
            issue_id = 0
            try:
                split = split_comments(record_issue)
                if not split:
                    continue

                issue_id, description = split

                t = Timelog(issue_id=issue_id, hours=hours,
                            spent_on=record_date,
                            activity_id=activity_id,
                            comments=description)
                logger.debug('adding timelog: {}'.format(t))

                timelogs.append(t)

            except ValueError:
                # add to drop list
                logger.debug('stdin dropped timelog: %s|%s', record_issue, line)
                pass

    timelogs = merge_sieblings(timelogs, logger)
    logger.debug('Batched-parsed-timelogs: %s', timelogs)
    return timelogs


def split_comments(l):
    """
    returns a (0000, 'Aaa aa aaaa') pair from various string patterns:

    '0000:Aaa aa aaaa.'
    '0000 Aaa aa aaaa.'
    'Category: 0000 Aaa aa aaaa.'
    'Category: Aaa aa aaaa. 0000'
    'minetime: Aaa aa aaaa. 0000'
    'Aaa aa aaaa. 0000'
    """

    s = re.split('(\d+)', l, 1)
    ss = [i.strip(' :') for i in s if i]
    if len(ss) < 2:
        return False
    if len(ss) == 3:    # ['Category:', '0000', 'issue description']
        ss = ss[1:]      # ['0000', 'issue description']
    if ss[1].isdigit():
        ss = list(reversed(ss))
    return (int(ss[0]), re.sub('^minetime: ', '', ss[1]))


def string_to_timelogs(s):
    """
    Id   Hours Date       Activity Comments
    ---- ----- ---------- -------- --------
    0123 StrHo YYYY-MM-DD 9        Abc Def
    """

    timelogs = []

    for line in s.splitlines():
        line_strip = line.strip()
        if not line_strip:
            continue
        try:
            raw_timelog = line_strip.split(None, 4)
            raw_id = raw_timelog[0]
            raw_hours = raw_timelog[1]
            raw_date = raw_timelog[2]
            raw_activity = raw_timelog[3]
            t_comments = ''
            if(len(raw_timelog) > 4):
                t_comments = raw_timelog[4]
            t_id = int(raw_id)
            t_hours = float(raw_hours)
            t_date = vali_date(raw_date)
            t_activity = int(raw_activity)

        except (IndexError, ValueError):
            continue

        t = Timelog(issue_id=t_id, hours=t_hours,
                    spent_on=t_date,
                    activity_id=t_activity,
                    comments=t_comments)

        timelogs.append(t)

    return timelogs


def get_new_config(redmine_url, api_key):
    config = {}
    config['general'] = {}
    config['general']['uri'] = redmine_url
    config['user'] = {}
    config['user']['api_key'] = api_key
    config['user']['activity_id'] = 9
    config['tracked_queries'] = {}
    config['tracked_projects'] = {}
    config['activities'] = {}
    return config


def humanize_timelogs(timelogs, activities):
    return [[t[0],
             t[1],
             humanize_date(t[2]),
             get_activity_name(t[3], activities),
             t[4]]
                      for t in timelogs]


def humanize_date(d):
    today = datetime.now().date()
    delta = d - today
    if delta.days == 0:
        return 'today'
    elif delta.days == 1:
        return 'tomorrow'
    elif delta.days == -1:
        return 'yesterday'
    else:
        return d.strftime('%Y-%m-%d')


def vali_date(value):
    try:
        return convert_date_string(value)
    except ValueError:
        return False


def convert_date_string(value):
        return datetime.strptime(value, '%Y-%m-%d').date()


def convert_time_string(value):
        return datetime.strptime(value, '%H:%M').time()


def total_hours(time_entries):
    return sum([t.hours for t in time_entries])


def get_activity_name(activity_id, activities):
    if not activities:
        activities = {}
        activities[9] = u"Development"

    try:
        return activities[activity_id]
    except:
        return str(activity_id)


def get_logo():
    return """
                         MMNNNNNNMM
                         MMooooooMM
                         ooMMooMMoo    .o.
                         `:MMooMM:`  .yMNMy.
                      :ymNdysoosydNmydMMy+NMy
                    +NNs:: \ || / ::sNMdMMMy.
                  .dMo.+`.   ||   .`+.oMM+.
                 `mN::.`.    ||    .`.::Nm`
                 yM+:-       ||       -:+My
        `//ooooooNMsooooooooohhooooooooosMNoooooo//`
         smMMMdoooooooooooooooooooooooooooooodMMMms
         .MN/yNNy/`                      `/yNNy/NM.
          sMs  -odMdo-                -odMdo-  sMs
          `NM.    `/yNNy:`        `:yNNy/`    .MN`
           /Mh        :smMh+.  .+hMms:        hM/
            hM/          .+hMyyMh+.          /Mh
            .Mm`        `/yNNssNNy/`        `NM.
             sMs     -odMdo-    -odMdo-     sMs
             `NM.`:yNNy/`          `/yNNy:`.MN`
              /mdMMMdoooooooooooooooooodMMMdm/
               :/oosdMMdsoooooooooosdMMdsoo/:
oooooooooMMoooooo MMMMMmMy         ymMMMMM ooooooMMooooooMMo
oooooooooMMooooooMMmmddsmMdoooooodMmsddmmMMooooooMMooooooMMo
         MM      MMy+  smMMooooooMMms  +yMM      MM      MM
         MM      MMMmmmmMM        MMmmmmMMM      MM      MM
dddddddddMMddddddMMmMMMMmMMddddddMMmMMMMmMMddddddMMddddddMMd
         MM      MM      MM      MM      MM      MM      MM
"""

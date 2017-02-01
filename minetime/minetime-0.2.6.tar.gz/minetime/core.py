# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
from itertools import groupby
import pkg_resources

import click
from . import helpers
import yaml
from minetime_lib import minetime_lib
from tabulate import tabulate


def vali_date_option(ctx, param, value):
    return minetime_lib.vali_date(value)


@click.command()
@click.option('--all', '-a', is_flag=True, default=False,
              help='Import all timelogs in --batch, regardless of --date.')
@click.option('--date', '-d', callback=vali_date_option,
              default=datetime.today().strftime('%Y-%m-%d'),
              help='YYYY-MM-DD date of timelogs, default: today.')
@click.option('--batch', '-b', type=click.Choice(['gtl', 'utt']),
              help='Read gtimelog|utt from input. See gtimelog integration documentation.')
@click.option('--timelog', '-t', multiple=True, type=(int, float, str, int),
              help="""
ISSUEID, HOURS, COMMENTS, ACTIVITYID
              HOURS: decimal float (0.25 : 15 minutes).
              """)
@click.option('--issues', '-i', is_flag=True, default=False,
              help='Show issues and exit. See gtimelog integration documentation.')
@click.option('--report', '-r', is_flag=True, help='Project Time Report for any tracked projects or manually-fed project-string.')
@click.option('--debug', is_flag=True, default=False,
              help='Enable debug logging.')
@click.version_option()
@click.argument('input', type=click.File('r', encoding='UTF-8'), required=False)
def mine_time(all, date, batch, timelog, issues, report, debug, input):
    logger = helpers.get_logger(debug)
    timelogs = []

    config = init_config()
    logger.debug('config: %s', config)
    proxy = minetime_lib.init_proxy(logger, config)
    activity_id = config['user']['activity_id']
    if issues:
        focused_issues = proxy.get_issues(config['tracked_queries'])
        return issues_report(focused_issues)
    if report:
        return project_report(config, proxy)
    if batch:
        timelogs = minetime_lib.get_batch_timelogs(logger, config, batch, input, date, all)
    elif timelog:
        logger.debug('importing cli-fed timelog (-t)')
        for (issue_id, hours, comments, activity_id) in timelog:
            t = minetime_lib.Timelog(issue_id=issue_id, hours=hours, spent_on=date,
                                     activity_id=activity_id, comments=comments)
            timelogs.append(t)

    logger.debug('entering cli wizard')
    cli_wizard(proxy, logger, config, timelogs, date)


def cli_wizard(proxy, logger, config, timelogs, date):
    click.clear()
    focused_issues = proxy.get_issues(config['tracked_queries'])
    activity_id = config['user']['activity_id']

    cli_wizard_print_intro(config)

    while(True):

        if timelogs:
            echo_timelogs(timelogs, config)

        response = cli_wizard_action()

        # New
        if response == 'n':
            timelogs.append(cli_wizard_new_timelog(focused_issues, activity_id, date))

        # Abort
        elif response == 'q':
            if click.confirm('\nReally abort and quit? All timelogs will be lost.'):
                logger.debug('Did not post a jiffy!')
                return False

        # Merge
        elif response == 'm':
            if click.confirm('\nMerge sieblings? All worked hours on a given day and issue will be merged into a single entry with all unique comments appended one another.'):
                timelogs = minetime_lib.merge_sieblings(timelogs, logger)

        # Round
        elif response == 'r':
            if click.confirm('\nProceed? This will round all timelogs hours to the smartest 15 minutes (ex: 3h09 becomes 3h15)'):
                timelogs = minetime_lib.round_timelogs(timelogs)

        # Post
        elif response == 'p':
            cli_wizard_post_feedback_exit(proxy, timelogs)
            return

        # Edit
        elif response == 'e':
            timelogs = cli_wizard_edit_timelogs(timelogs)

        elif response == 'h':
            cli_wizard_display_help()

        else:
            assert(False)
            pass


def cli_wizard_print_intro(config):
    version = pkg_resources.require("minetime")[0].version
    click.secho('Welcome to minetime {}.\n'.format(version), fg='blue', bold=True)
    click.echo('Timelogs will remain in memory only, until you decide to post them.\n')


def cli_wizard_new_timelog(focused_issues, activity_id, date):
        click.clear()
        issue_id, issue_subject = cli_wizard_choose_issue(focused_issues)

        hours = click.prompt("Enter decimal hours worked (0.25 per 15 minutes)", type=float)
        import_date = click.prompt("Input new date for timelog or keep current default",
                                   default=date, value_proc=minetime_lib.vali_date)

        comments = cli_wizard_comments_message(issue_id, issue_subject, hours, import_date)

        # All is good. Add timelog.
        date = import_date
        t = minetime_lib.Timelog(issue_id=issue_id, hours=hours, spent_on=date,
                                 activity_id=activity_id, comments=comments)
        return t


def cli_wizard_display_help():
    click.echo("""
Available commands:

   n   new timelog
   e   edit timelogs

   m   merge timelogs
   r   round timelogs

   p   post timelogs
   q   abort and quit

   h   display this help

    """)


def cli_wizard_action():
    response = False
    while not response:
        try:
            vali_confirm_char = lambda v: v.lower() if v in ['N', 'n', 'E', 'e', 'M', 'm', 'R', 'r', 'P', 'p', 'Q', 'q', 'H', 'h'] else False
            response = click.prompt('Command (h for help)', value_proc=vali_confirm_char)

        except click.Abort:
            response = 'q'

    return response


def cli_wizard_post_feedback_exit(proxy, timelogs):
    posted, rejected = proxy.post_timelogs(timelogs)
    if posted:
        posted_string = u'\n✓ Posted following timelogs'
        click.secho(posted_string, fg='green', bold=True, underline=True)
        click.echo(u'{}'.format(tabulate(posted)))
    if rejected:
        rejected_string = u'\n✘ Some timelogs were rejected'
        click.secho(rejected_string, fg='red', bold=True, underline=True)
        click.secho(u'{}'.format(tabulate(rejected)), fg='red', bold=True)
        click.secho('Do all issues exist on redmine?\n', fg='red', bold=True)

    click.echo('Goodbye, until minetime!')
    sys.exit(0)


def cli_wizard_choose_issue(focused_issues):
    assigned_issues, tracked_issues_list = focused_issues
    if(len(tracked_issues_list)):
        tracked_issues = tracked_issues_list[0]  # TODO: handle tracked_issues_list
    else:
        tracked_issues = []
    len_assigned_issues = len(assigned_issues)
    len_tracked_issues = len(tracked_issues)
    assigned_index = list(range(1, len_assigned_issues + 1))
    tracked_index = list(range(len_assigned_issues + 1,
                               len_assigned_issues + len_tracked_issues + 1))
    click.echo("Assigned Issues\n")
    click.echo(tabulate(assigned_issues, headers="keys", showindex=assigned_index))
    if len_tracked_issues:
        click.echo("\nTracked Issues\n")
        click.echo(tabulate(tracked_issues, headers="keys", showindex=tracked_index))
    click.echo("\n")

    selected = 0
    while not selected:
        raw_selected = click.prompt("Select Issue", type=int)
        try:
            selected = int(raw_selected)
            s = selected - 1

            if selected in assigned_index:
                issue_id = assigned_issues[s]['id']
                issue_subject = assigned_issues[s]['subject']
            elif selected in tracked_index:
                s = s - len_assigned_issues
                issue_id = tracked_issues[s]['id']
                issue_subject = tracked_issues[s]['subject']
            else:
                raise ValueError
        except ValueError:
            click.echo('selected invalid value. Please select one of the listed issues')
            selected = 0

    return (issue_id, issue_subject)


def issues_report(issues):
    assigned_issues, tracked_issues_list = issues
    for i in assigned_issues:
        click.echo(u'minetime: {} {}'.format(i['id'], i['subject']))
    for l in tracked_issues_list:
        for i in l:
            click.echo(u'minetime: {} {}'.format(i['id'], i['subject']))


def project_report(config, proxy):
    p = None
    pid = None
    if 'tracked_projects' in config:
        projects = config['tracked_projects']
        refs = range(len(projects))
        vali_tracked_project = lambda pos: int(pos) if pos.isdigit() and int(pos) in refs else False
        for i in refs:
            click.echo('{} : {}'.format(i, projects[i]))
        pos = click.prompt('Please select tracked project. Leave empty to input custom project-id string',
                           default='', value_proc=vali_tracked_project)

        if pos is not False:
            if pos in refs:
                pid = projects[pos]

    p = proxy.get_project(pid)
    while not p:
        pid = click.prompt('Please input a valid project-id string (can be found in project url). Type quit to do so.')
        if pid == 'quit':
            sys.exit(0)
        p = proxy.get_project(pid)

    click.echo("""
    {} Project Report.
    Please wait while data is fetched from server.
    This should take more or less 30 seconds depending on dataset size and network connection.""".format(pid))


    data = []
    username = lambda item: item['user']['name'] if hasattr(item, 'user') and hasattr(item['user'], 'name') else '-'
    if not p.versions:
        click.echo('No version found. Goodbye for now.')
        return
    previous_due_date = None
    for iv in p.versions:
        if not hasattr(iv, 'due_date'):
            continue
        iv.start_date = previous_due_date + timedelta(days=1) if previous_due_date else iv.created_on.date()
        previous_due_date = iv.due_date
        period_time_entries = [t for t in p.time_entries
                               if helpers.day_between(iv.start_date,
                                                      iv.due_date, t.spent_on) and
                               hasattr(t, 'spent_on')]
        total_period = minetime_lib.total_hours(period_time_entries)

        period_time_entries.sort(key=username)
        user_grouped_entries = groupby(period_time_entries, username)
        si = [s for s in p.issues
              if (s.tracker.id in (1, 5) and hasattr(s, 'fixed_version') and (s.fixed_version.id == iv.id))]
        if iv.status == 'open':
            issues_no_estimate = [(i.id, i.subject)
                                  for i in p.issues
                                  if (hasattr(i, 'estimated_hours') and
                                      i.estimated_hours == 0 and
                                      hasattr(i, 'fixed_version') and
                                      (i.fixed_version.id == iv.id))]

            new_issues_worked = [(i.id, i.subject)
                                 for i in p.issues
                                 if (i.status == 1 and
                                     i.time_entries and
                                     hasattr(i, 'fixed_version') and
                                     (i.fixed_version.id == iv.id))]
        else:
            issues_no_estimate = []
            new_issues_worked = []

        data.append((iv,
                     total_period,
                     period_time_entries,
                     user_grouped_entries,
                     si,
                     issues_no_estimate,
                     new_issues_worked))
    print_project_report(p, data)


def print_project_report(p, data):
    click.clear()
    project_total_hours = sum([t[1] for t in data])
    sep = '-' * 80
    p1 = u'Project {}'.format(p.name)
    p2 = 'Total Worked Hours: {}'.format(project_total_hours)
    pline = space_line(p1, p2) + '\n'

    click.clear()
    click.echo(sep)
    click.echo(pline)
    click.echo(sep)
    sort_on_due_date = lambda item: item[0]['due_date'] if len(item) and hasattr(item[0], 'due_date') else datetime.strptime('1900-01-01', '%Y-%m-%d').date()
    data.sort(key=sort_on_due_date)
    for vperiod, period_total, period_entries, periodi, \
            scenarios, unestimated_issues, new_issues_worked in data:

        v1 = u'V: {} ({})'.format(vperiod.name, vperiod.status)
        if hasattr(vperiod, 'due_date'):
            vdue = vperiod.due_date
        else:
            vdue = datetime.strptime('1900-01-01', '%Y-%m-%d')
        v2 = 'Period From {} To {}'.format(vperiod.start_date, vdue)
        vline = space_line(v1, v2) + '\n'

        click.echo(vline)
        for key, group in periodi:
            onesum = sum([item["hours"] for item in group])
            click.echo(u'{} : {}'.format(key, onesum))
        click.echo(space_line('', 'Period Total Worked Hours: {}'.format(period_total)))
        report_print_version_scenarios(scenarios)
        click.echo(sep)
        if unestimated_issues:
            echo_boom('Issues with no estimated_hours:')
            echo_boom(tabulate(unestimated_issues))
        if new_issues_worked:
            echo_boom('New Issues with time entries:')
            echo_boom(tabulate(new_issues_worked))
    click.echo(sep)
    click.echo(pline)
    click.echo(sep)


def report_print_version_scenarios(scenarios):
    click.echo()
    vhours = 0
    vestimate = 0
    scolor = {
        1: 'blue',  # New
        2: 'yellow',  # Open
        8: 'green',  # Done
        4: 'red',  # Feedback
        9: 'magenta',  # Review
    }

    for s in scenarios:
        sestimate = 0
        spoints = int(s.story_points or 0)
        shours = minetime_lib.total_hours(s.time_entries)
        vhours += shours
        if hasattr(s, 'estimated_hours'):
            sestimate = s.estimated_hours
            vestimate += sestimate
        echostr = (u'{} ({}) / story: {} / estimate: {} / progress: {} /'.format(s.subject, s.status.name, spoints, sestimate, shours))

        if shours and s.status.id == 1:
            echo_boom(echostr)
        elif 1 == 2:
            echo_boom(echostr)
        elif s.status.id == 4:
            click.secho(echostr, fg=scolor[s.status.id], bg='white', bold=True)
        else:
            click.secho(echostr, fg='white', bg=scolor[s.status.id], bold=True)

    click.echo()
    if vhours:
        click.echo(space_line('', 'Work in progress: {}'.format(vhours)))
    if vestimate:
        click.echo(space_line('', 'Estimated Work Left: {}'.format(vestimate)))


def echo_boom(boom):
    click.secho(boom, bg='red', fg='white', bold=True)


def init_config():
    config_dir = click.get_app_dir('minetime')
    config_file = os.path.join(config_dir, 'config.yml')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    if not os.path.exists(config_file):
        wizard_create_config(config_file)

    config = helpers.get_config()
    if not config:
        click.echo('wrong config!')
        sys.exit(1)

    return config


def space_line(a, b, total=80):
    space = (total - len(a) - len(b)) * ' ' or '\n' + ' ' * (total - len(b))
    return a + space + b


def cli_wizard_edit_timelogs(timelogs):
    MARKER = '# Everything under this line will be ignored\n'
    INSTRUCTION1 = '# Only correctly formatted timelogs will be considered.\n'
    INSTRUCTION2 = '# To add new custom timelog, insert new line.\n# To delete existing timelogs, remove undesired lines.\n# And do feel free to edit existing timelogs.\n'

    precontent = tabulate(timelogs, headers=('Id', 'Hours', 'Date', 'Activity', 'Comments'))
    message = click.edit(precontent + '\n\n' + MARKER + INSTRUCTION1 + INSTRUCTION2)
    if not message:
        return timelogs  # Return original timelogs if user aborts edit
    timelogs_table_string = message.split(MARKER, 1)[0].rstrip('\n')
    return minetime_lib.string_to_timelogs(timelogs_table_string)


def cli_wizard_comments_message(issue_id, issue_subject, hours, date):
    MARKER = '# Everything below is ignored\n'
    INSTRUCTION = '# Describe your time entry (to complete issue name)\n'
    CONTEXT = u'# Task ({}) : {}\n'.format(issue_id, issue_subject)
    HOURS = '# Hours worked: {}\n'.format(hours)
    DATE = '# Date worked on: {}\n'.format(date)
    message = ''
    while not message:
        if click.confirm('Enter Comments?'):
            message = click.edit('\n\n' + MARKER + INSTRUCTION + CONTEXT + HOURS + DATE)
        else:
            return ''
    return message.split(MARKER, 1)[0].rstrip('\n')


def echo_timelogs(timelogs, config):
    activities = config['activities'] or None
    total_hours = minetime_lib.total_hours(timelogs)
    human_timelogs = minetime_lib.humanize_timelogs(timelogs, activities)

    click.echo()
    click.echo(tabulate(human_timelogs, headers=('Id', 'Hours', 'Date', 'Activity', 'Comments')))
    click.echo("\nTotal Hours: {}".format(total_hours))


def wizard_create_config(config_file):
    wizard_confirm_file = '''
    It seems like you have no configuration file.
    Wizard can create one for you.
    What you will need:
      - The redmine instance URL
      - Your API Key
    Go?'''

    if not click.confirm(wizard_confirm_file):
        return

    redmine_url = click.prompt("What is your Redmine URL?", type=str)
    api_key = click.prompt("What is your Redmine API Key?", type=str)

    config = minetime_lib.get_new_config(redmine_url, api_key)

    write_new_config(config, config_file)


def write_new_config(config, config_file):
    with click.open_file(config_file, 'w') as f:
        return yaml.safe_dump(config, f, default_flow_style=False)

"""CALLER.PY

Call the rpc ``conf['wamp']['rpc_simc_dps']`` and produce a report based on the output.

Usage:
    caller.py start [--limit=<amount>] [--multi_enemy] [--rpc_mode] [--non_interactive] [--open_result] [--debug] [--publish_off] [--log_off]
    caller.py -h | --help
    caller.py --version

Options:
    -h --help           Show this screen.
    --limit=<amount>    Limit permutations to <amount> [default: 2]. 0 means no limit.
    --multi_enemy       Use 4 Targets instead of 1.
    --rpc_mode          Don' run programm butt register as rpc (currently untested if it still works).
    --non_interactive   Don' t ask for user input regarding the --limit value.
    --open_result       Automatically open a browser windows with the result.
    --log_off           Don't output anything per self.log.info/ .debug.
    --publish_off       Don't output anything per publish.
    --debug             Output debug messages.
    """
import simc_autobahn.py_version_check
import asyncio
import configparser
import hashlib
import json
import sys
import time
import timeit
import traceback
import webbrowser
from functools import partial
from os import path, makedirs
from urllib.parse import urlparse
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import CallOptions
from autobahn.wamp.types import RegisterOptions
from bs4 import BeautifulSoup
from docopt import docopt
from yattag import Doc
sys.path.append("..")
from simc_autobahn.simc_permutations import simperm_create
from simc_autobahn.models import Task, create_tables
from simc_autobahn.my_logger import MyLogger

conf = configparser.ConfigParser()
conf.read(path.join(path.dirname(__file__), '..', 'config.ini'))


# MAIN CLASS
#
class MyComponent(ApplicationSession):

    # create tables
    create_tables()

    async def onJoin(self, details):

        async def do_it():
            start = timeit.default_timer()
            ret = []
            calls = []
            l = MyLogger('', conf['caller']['topic_caller_log'], args, self)
            # CREATE PERMUTATIONS
            #
            permutations_count, permutations = simperm_create(path.join(path.dirname(__file__), conf['caller']['autosimc_in']), multi_enemy=args['--multi_enemy'])
            l.info(f"Started with --limit={args['--limit']}, --multi_emeny={args['--multi_enemy']}, permutations={permutations_count}")

            # CALL RPC
            #
            timestamps = []
            avg_times = [1]  # put in initial value, else code crashes

            # callback
            def got(total, ha, d):
                try:
                    d = json.loads(d.result())
                    # store returned data
                    ret.append(d)
                    print(ha)
                    # store also also in db
                    t = Task.get(Task.hash == ha)
                    t.hostname = d['hostname']
                    t.session = d['session']
                    t.profile = d['profile']
                    t.iterations = d['iterations']
                    t.dps = d['dps']
                    t.items = d['items']
                    t.save()
                    l.debug(f"New caching db entry for {d['profile']} created")

                    # display progress bar
                    timestamps.append(timeit.default_timer())
                    for idx, timestamp in enumerate(timestamps):
                        if idx > 0:
                            avg_times.append(timestamp - timestamps[idx - 1])
                    avg = sum(avg_times) / len(avg_times)
                    remaining = (total - print_iter)
                    suffix = avg * remaining
                    suffix = time.strftime("%H:%M:%S", time.gmtime(suffix))

                    if sys.stdout.isatty():
                        # this only works if programm was opened in interactive shell
                        print_progress(total, f"{suffix}s remaining")
                    else:
                        l.info(suffix)
                except:
                    l.error(traceback.print_exc())

            # if tty ask for user input and set max value accordingly
            if sys.__stdin__.isatty() and not args['--non_interactive']:
                user_input = input(
                    f"Insert a new limit [0 = no limit] or press Enter to use default [{args['--limit']}]: ")
                if len(user_input) > 0:
                    try:
                        args['--limit'] = int(user_input)
                    except Exception as e:
                        pass

            l.debug(f"Session ready on {conf['wamp']['uri']}, {conf['wamp']['realm']}")

            # ONLY GO AHEAD AT LEAST ONE RPC IS PRESENT
            #
            res = self.call("wamp.registration.lookup", conf['wamp']['rpc_simc_dps'])
            await res
            if res.result() is None:
                l.info(f"No callees on procedure {conf['wamp']['rpc_simc_dps']}")
            else:
                res = self.call("wamp.registration.count_callees", res.result())
                await res
                l.info(f"{res.result()} callees on procedure {conf['wamp']['rpc_simc_dps']}")

                # limit it to max, if it was set
                if args['--limit'] > 0:
                    permutations_count = args['--limit']

                for i, simc_args in enumerate(permutations):
                    # check if max was reached
                    if args['--limit'] == i > 0:
                        break
                    # convert array into string
                    simc_args = " ".join(simc_args)
                    if len(simc_args) > 0:
                        try:
                            h = hashlib.md5(simc_args.encode())
                            h = h.hexdigest()
                            task, created = Task.get_or_create(hash=h)
                            if created is True or task.dps is None:
                                # new Task entry created or there are no values (because of error, disconnect, etc)
                                o = self.call(conf['wamp']['rpc_simc_dps'], simc_args, options=CallOptions(timeout=5))
                                o.add_done_callback(partial(got, permutations_count, h))
                                calls.append(o)
                            else:
                                # read from cache
                                data = {
                                    "hostname": task.hostname,
                                    "session": task.session,
                                    "profile": task.profile,
                                    "iterations": task.iterations,
                                    "dps": task.dps,
                                    "items": task.items
                                }
                                ret.append(data)
                                print_progress(permutations_count, f"read from cache")
                                l.debug(f"Caching db entry for {task.profile} loaded")

                        except Exception as e:
                            l.error(traceback.print_exc())

                # AWAIT RPC
                #
                await asyncio.gather(*calls)

                # PUT RESULT INTO ARRAY
                #
                ret_sorted = reversed(sorted(ret, key=lambda k: k['dps']))
                table_data = []
                for i, el in enumerate(ret_sorted):
                    table_data.append(
                        [i + 1, el['hostname'], el['session'], el['profile'], el['dps'], el['iterations']])

                    # get item info
                    m_ids = []
                    for ii in el['items']:
                        soup = BeautifulSoup(ii, 'html.parser')
                        item_url = urlparse(soup.a['href'])
                        item_id = item_url.path.split('/')[-1]
                        m_ids.append(item_id)
                        table_data.append([soup.a])
                    macro = "/run for i, v in next, {%s} do EquipItemByName(v) end" % ", ".join(m_ids)
                    table_data.append([macro])

                # BUILD& SAVE HTML OUT OF ARRAY
                #
                headers = ['', 'Host', 'WAMP ID', 'Profile', 'DPS', 'Iterations']  # must be same len() as max len of table_data!
                doc, tag, text, line = Doc().ttl()
                doc.asis('<!DOCTYPE html>')

                js = '''
                    $('.header').click(function(){
                        $(this).toggleClass('expand').nextUntil('tr.header').toggle();
                    });
                    $('.header').click();
                '''

                css = '''
                    table, tr, td, th {
                        border: 1px solid black;
                        border-collapse:collapse;
                    }
                    tr.header {
                        cursor:pointer;
                    }
                    .header .sign:after {
                        content:"+";
                        display:inline-block;
                    }
                    .header.expand .sign:after {
                        content:"-";
                    }
                '''

                with tag('html'):
                    with tag('head'):
                        doc.asis('<script type="text/javascript" src="http://static-azeroth.cursecdn.com/current/js/syndication/tt.js"></script>')
                        doc.asis('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>')
                        with tag('style'):
                            doc.asis(css)
                    with tag('body'):
                        with tag('table'):
                            with tag('tr'):
                                for el in headers:
                                    line('th', el)
                            for row in table_data:
                                with tag('tr'):
                                    if len(headers) == len(row):
                                        doc.attr(klass="header expand")
                                    for idx, el in enumerate(row):
                                        with tag('td', colspan=(len(headers) + 1) - len(row)):
                                            if len(headers) == len(row) and idx == 0:
                                                doc.stag('span', klass="sign")
                                            else:
                                                doc.asis(str(el))
                        with tag('script'):
                            doc.asis(js)

                # filename
                timestr = time.strftime("%Y%m%d-%H%M%S")
                ms = "multi" if args['--multi_enemy'] else "single"
                filename = path.join(path.dirname(__file__), conf['caller']['results_dir'], f"out_{ms}_{timestr}.html")

                # save file
                makedirs(path.join(path.dirname(__file__), conf['caller']['results_dir']), exist_ok=True)
                f = open(filename, 'w')
                f.write(doc.getvalue())
                f.close()

                # PRINT END
                #
                stop = timeit.default_timer()
                l.info(f"Done in {time.strftime('%H:%M:%S', time.gmtime(stop - start))}s, results saved in {filename}")
                if args['--open_result']:
                    webbrowser.open(filename, new=2)

        # register rpc if set
        if args['--rpc_mode']:
            # register simc_dps
            try:
                self.register(do_it, 'de.simc-autobahn.do_it',
                              RegisterOptions(
                                  invoke=u'roundrobin',
                                  concurrency=1
                              ))
                self.log.info(f"procedure de.simc-autobahn.do_it registered")
            except Exception as e:
                self.log.error(f"could not register procedure: {traceback.print_exc()}")
        else:
            await do_it()
            self.leave()

    def onDisconnect(self):
        asyncio.get_event_loop().stop()


print_iter = 1
def print_progress(total, suffix='', decimals=1, bar_length=50):
    """
    Call in a loop to create terminal progress bar
    @params:
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    global print_iter
    prefix = f"{print_iter}/{total}"
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (print_iter / float(total)))
    filled_length = int(round(bar_length * print_iter / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if print_iter == total:
        sys.stdout.write('\n')
    sys.stdout.flush()
    print_iter += 1


if __name__ == '__main__':
    args = docopt(__doc__)
    args['--limit'] = int(args['--limit'])  # we need it as int later on
    runner = ApplicationRunner(url=conf['wamp']['uri'], realm=conf['wamp']['realm'])
    runner.run(MyComponent)

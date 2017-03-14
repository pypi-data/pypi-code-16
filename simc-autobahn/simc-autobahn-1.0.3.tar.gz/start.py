"""Start-Up simc-autobahn

Usage:
    start.py single [--workers=<amount>] [--limit=<amount>] [--remove_cache]
    start.py multi [--workers=<amount>] [--limit=<amount>] [--remove_cache]
    start.py single multi [--workers=<amount>] [--limit=<amount>] [--remove_cache]

Options:
    --workers=<amount>      Number of workers to spawn [default: 2].
    --limit=<amount>        Limit permutations to <amount> [default: 10]. 0 means no limit.
    --remove_cache          If set, cache db will be deleted.
"""
from docopt import docopt
import subprocess
import sys
import os
from time import sleep
import simc_autobahn.py_version_check

args = docopt(__doc__, version='Start 0.1')

def main_func():
    # add our simc_autobahn code dir to PYTHONPATH
    my_env = os.environ.copy()
    my_env["PYTHONPATH"] = os.path.join(os.path.abspath(os.path.dirname(__file__)))

    # remove caching db if switch was set
    if args['--remove_cache']:
        try:
            os.remove('caller/db.sql')
        except Exception:
            # probaby the db.sql is not present, let's ingore this
            pass

    # START UP WORKERS
    #
    procs = []
    for i in range(int(args['--workers'])):
        proc = subprocess.Popen([sys.executable, 'worker/worker.py', 'start', '--log_off'], env=my_env)
        procs.append(proc)
        print(f"Started worker with pid={proc.pid}")

    sleep(1)  # wait for the first worker to register

    # CALL WORKERS
    #
    print("Calling workers ...")
    if args['single']:
        print()
        subprocess.run([sys.executable, 'caller/caller.py', 'start', f"--limit={args['--limit']}", "--debug"], env=my_env)

    if args['multi']:
        print()
        subprocess.run([sys.executable, 'caller/caller.py', 'start', '--non_interactive', '--multi_enemy', f"--limit={args['--limit']}"], env=my_env)

    print("\n... done.")
    # FINISH UP
    #
    for proc in procs:
        proc.terminate()
        print(f"Terminated worker with pid={proc.pid}")

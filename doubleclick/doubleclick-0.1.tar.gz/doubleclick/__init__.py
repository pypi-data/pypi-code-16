import sys


def exit_err(msg, err=True, status=1):
    print(str(msg), file=sys.stderr if err else sys.stdout, flush=True)

    # uses SystemExit instead of sys.exit(), giving callers a chance to catch
    # the exception
    raise SystemExit(status)

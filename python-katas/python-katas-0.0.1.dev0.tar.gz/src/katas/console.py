from code import compile_command
import sys
import traceback

try:
    import readline
except ImportError:
    pass


def interact(locals_, target):
    while True:
        try:
            buffer = []
            line = input('>>> ')

            while True:
                buffer.append(line)
                source = '\n'.join(buffer)
                if run_source(source, locals_):
                    break

                line = input('... ')

            try:
                if eval('_') == target:
                    return True
            except NameError:
                pass

        except EOFError:
            print()
            sys.exit()
        except KeyboardInterrupt:
            if buffer:
                print('\nKeyboardInterrupt')
            else:
                print()
                return False


def run_source(source, locals_):
    try:
        code = compile_command(source, '<console>', 'single')
    except (OverflowError, SyntaxError, ValueError):
        show_syntax_error()
        return True

    if code is None:
        return False

    try:
        exec(code, globals(), locals_)
    except SystemExit:
        raise
    except:
        show_traceback()

    return True


def show_syntax_error():
    etype, value, tb = sys.exc_info()
    lines = traceback.format_exception_only(etype, value)
    print(''.join(lines))


def show_traceback():
    etype, value, tb = sys.exc_info()
    lines = traceback.format_exception(etype, value, tb.tb_next)
    print(''.join(lines))

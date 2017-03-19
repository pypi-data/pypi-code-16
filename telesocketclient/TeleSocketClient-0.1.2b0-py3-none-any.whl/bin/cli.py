import json
import logging
import shlex

from termcolor import colored

from TeleSocketClient.manager import TeleSocket

PREFIX = 'request_'
logging.basicConfig(level=logging.WARNING)


class Shell:
    def __init__(self):
        self.sock = TeleSocket()
        self.sock.add_telegram_handler(self.telegram_handler)

    def call(self, command):
        method = self.get_method(command[0])
        if method:
            try:
                return method(command)
            except Exception as e:
                print(colored(e.__class__.__name__ + ':', 'red', attrs=['bold']), colored(str(e), 'red'))
                return False

        return self.out_system('Unknown command!')

    def telegram_handler(self, data):
        print(colored('TELEGRAM:', 'blue', attrs=['bold']), json.dumps(data))

    def out(self, data):
        print(colored(json.dumps(data, indent=4), 'yellow'))

    def out_system(self, *message):
        print(colored('::\t', 'blue', attrs=['bold']), *message)

    def get_method(self, method):
        return getattr(self, PREFIX + method, None)

    def request_help(self, command):
        if len(command) > 1:
            cmd = self.get_method(command[0])
        else:
            print('Available commands:')
            for cmd in [arg[len(PREFIX):] for arg in dir(self) if arg.startswith(PREFIX)]:
                print('\t -', cmd)

    def request_login(self, command):
        if len(command) == 1:
            raise SyntaxError('Token required!')
        result = self.sock.login(command[1]).deserialize()
        self.out(result)

    def request_register(self, command):
        if len(command) == 1:
            raise SyntaxError('Username required!')
        if len(command) > 2:
            result = self.sock.register(command[1], command[2])
        else:
            result = self.sock.register(command[1])
        self.out(result.deserialize())

    def request_ping(self, command):
        ping = self.sock.ping()
        self.out_system('Pong:', ping, 'ms.')

    def request_webhook(self, command):
        if len(command) > 1 and command[1] == 'start':
            if len(command) <= 2:
                raise SyntaxError('Bot name is required! "webhook start <name>"')
            hook = self.sock.set_webhook(command[2])
            return print(colored('URL:', 'cyan', attrs=['bold']), hook.url)
        elif len(command) > 1 and command[1] == 'stop':
            hook = self.sock.del_webhook()
            return self.out_system('Webhook is unsubscribed!')
        raise SyntaxError('webhook [start|stop]')

    def request_clients_list(self, command):
        clients = self.sock.clients_list()
        self.out_system('Online', len(clients))
        for client in clients:
            # TODO: Make more beautiful output
            print('\t', client)

    def request_generate_codes(self, command):
        if len(command) < 2:
            count = 1
        else:
            count = int(command[1])

        codes = self.sock.generate_codes(count)
        self.out(codes)


def cli():
    shell = Shell()

    try:
        while True:
            cmd = input('> ').strip()
            if not cmd:
                continue
            elif cmd in ['exit', '\q', 'q']:
                break
            command = shlex.split(cmd)
            shell.call(command)
            print()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    cli()

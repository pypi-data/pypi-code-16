# -*- coding: utf-8 -*-

import pendulum
from cleo import Application, Command


class NowCommand(Command):
    """
    Tests the now method.

    now
        {tz?* : The timezone to use}
    """

    def handle(self):
        tz = self.argument('tz')
        if not tz:
            tz = [None]

        self.write_now(tz)

    def write_now(self, tzs):
        now = pendulum.now()
        for tz in tzs:
            in_tz = now.in_tz(tz)
            line = 'Now in <info>{}</> is <fg=yellow>{}</>'.format(in_tz.timezone_name, in_tz.isoformat(' '))

            self.line(line)


class ParseCommand(Command):
    """
    Tests the parse method.

    parse
        {string : The string to parse.}
        {tz? : The timezone to use.}
    """

    def handle(self):
        string = self.argument('string')
        tz = self.argument('tz') or pendulum.UTC
        self.line('<comment>{}</>'.format(pendulum.parse(string, tz).isoformat(' ')))


app = Application('Pendulum')

app.add(NowCommand())
app.add(ParseCommand())


if __name__ == '__main__':
    app.run()

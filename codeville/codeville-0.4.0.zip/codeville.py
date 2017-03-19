from __future__ import print_function
import socket
import json

class CodeVille:
    def __init__(self, solver=None):
        self.sock_file = None
        self.response = None
        self.host = 'codeville-game.buzzcoder.com'
        self.port = 4444
        self.solver = solver

    def connect(self, username, password, gender):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.host, self.port)
        sock.connect(server_address)

        self.sock_file = sock.makefile('rw')

        # welcome message
        self.get_response()

        gender = 'boy' if gender[0].lower() in ('b', 'm') else 'girl'
        self.send_command("login", {'username': username, 'password': password, 'gender': gender})

        # waiting for game to start
        self.get_response()

        # game has started
        self.get_response()

        # player data
        return self.get_response()

    def send_command(self, command, args):
        if args is not None:
            json_args = json.dumps(args)
            request = command + " " + json_args[1:-1]
        else:
            request = command

        print("> ", request)
        request += "\n"
        self.sock_file.write(request)
        self.sock_file.flush()

    def get_response(self):
        while True:
            line = self.sock_file.readline().strip()
            if len(line) == 0:
                return None

            print("< ", line)

            parsed = line.split(" ", 1)

            status = parsed[0].upper()
            if status == "ERROR":
                raise Exception(parsed[1])

            json_args = parsed[1] if len(parsed) >= 2 else ""
            json_args = "{" + json_args + "}"
            response = json.loads(json_args)

            if status != "CHALLENGE":
                response["success"] = (status == "OK")
                self.response = response
                return response

            answer = self.solve(response)

            if answer:
                self.send_command("ANSWER", {"challengeId": response["id"], "value": answer})

    def solve(self, challenge):
        if not self.solver:
            return None

        function_name = '_'.join(challenge['description'].lower().split())
        function = getattr(self.solver, function_name, None)
        arguments = challenge["arguments"]

        if (callable(function)):
            result = function(*arguments)
            return result
        else:
            type_names = [type(a).__name__ for a in arguments]
            function_signature = '%s(self, %s)' % (function_name, ', '.join(type_names))
            print('Warning: method not defined: \x1b[6;30;42m%s\x1b[0m' % function_signature)

    def execute(self, command, args = None):
        if self.response:
            challenges = self.response['balls']
            if challenges:
                if args:
                    args = args.copy()
                else:
                    args = {}

                answer = self.solve(challenges[0])

                if answer:
                    args['answer'] = answer

        self.send_command(command, args)
        return self.get_response()

    def close(self):
        self.sock_file.close()

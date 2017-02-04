from __future__ import print_function
import socket
import json

class CodeVille:
    def __init__(self):
        self.sock_file = None

    def connect(self, username, password, host='codeville-game.buzzcoder.com'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, 4444)
        sock.connect(server_address)

        self.sock_file = sock.makefile('rw')

        # welcome message
        self.get_response()

        self.send_command("login", {'username': username, 'password': password})

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
        line = self.sock_file.readline().strip();
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
        response["success"] = (status == "OK")

        return response

    def execute(self, command, args = None):
        self.send_command(command, args);
        return self.get_response();

    def close(self):
        self.sock_file.close()

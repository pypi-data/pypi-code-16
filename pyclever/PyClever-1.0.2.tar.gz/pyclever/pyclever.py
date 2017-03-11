from subprocess import PIPE, Popen

bot_api_template = \
'''var cleverbot = require("cleverbot.io"),
bot = new cleverbot("{API_USER}", "{API_KEY}");
bot.setNick("{SESSION}");
bot.create(function (err, session) {{
}});

bot.ask("{STRING}", function (err, response) {{
	console.log(response);
}});'''

def read_file(file_name):
    with open(join(dirname(__file__), file_name)) as f:
        return f.read()

class Cleverbot:
    def __init__(self, api_user, api_key, session=''):
        self.api_user = api_user
        self.api_key = api_key
        self.session = session

    def say(self, string):
        js_temp = bot_api_template.replace('\n', ' ')
        js_temp = js_temp.format(API_USER=self.api_user, API_KEY=self.api_key, SESSION=self.session, STRING=string)
        cmd = "echo '{js_temp}' | node".format(js_temp=js_temp)
        response = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
        return response.decode('utf-8')[:-1]

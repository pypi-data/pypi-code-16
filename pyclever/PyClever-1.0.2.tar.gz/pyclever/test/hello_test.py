from pyclever import Cleverbot
import argparse

parser = argparse.ArgumentParser(description='Tests Cleverbot().say()')
parser.add_argument('api_user', help='API_USER')
parser.add_argument('api_key', help='API_KEY')
args = parser.parse_args()

cb = Cleverbot(args.api_user, args.api_key, 'newsession')
cb.say('How was your day?')

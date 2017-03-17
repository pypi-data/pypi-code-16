import requests
from helga.db import db
from helga.plugins import command, match, random_ack


def logic(args, nick):
    if args[0] == 'point':
        if not '--skip-remove' in args:
            db.helga_poker.entries.remove({'item': args[1], 'nick': nick})
        db.helga_poker.entries.insert({'item': args[1], 'value': args[2], 'nick': nick})
    elif args[0] == 'show':
        if len(args) < 2:
            return 'Sorry, you need to designate an item to show status on!'
        queryset = db.helga_poker.entries.find({'item': args[1]})
        if queryset.count() == 0:
            return 'Sorry, there are no votes for ' + args[1]
        query_nicks = ', '.join([query['nick'] + ':' + query['value'] for query in queryset])
        queryset.rewind()
        values = [int(query['value']) for query in queryset]
        mean = float(sum(values)) / max(len(values), 1)
        median = sorted(values)[int(len(values)/2)]
        return 'Median:{} avg:{} votes:{}'.format(median, mean, query_nicks)
    elif args[0] == 'status':
        if len(args) < 2:
            return 'Sorry, you need to designate an item to show status on!'
        queryset = db.helga_poker.entries.find({'item': args[1]})
        if queryset.count() == 0:
            return 'No votes for ' + args[1] + ':('
        query_nicks = ', '.join(query['nick'] for query in queryset)
        return '{} votes from: {} for {}'.format(queryset.count(), query_nicks, args[1])
    elif args[0] == 'dump':
        results = [p['item'] + ' ' + p['value'] + ' ' + p['nick'] for p in db.helga_poker.entries.find()]
        if not results:
            return "Poker database empty"
        payload = {'title': 'helga-pointing-poker dump', 'content': '\n'.join(results)}
        r = requests.post("http://dpaste.com/api/v2/", payload)
        return r.headers['location']
    elif args[0] == 'clear':
        db.helga_poker.entries.drop()
    else:
        return 'Unrecognized poker command: ' + str(args)
    return random_ack()


@command('poker', aliases=['pp', 'pointing-poker'], help='Pointing poker for helga')
def pointing_poker(client, channel, nick, message, cmd, args):
    return logic(args, nick)

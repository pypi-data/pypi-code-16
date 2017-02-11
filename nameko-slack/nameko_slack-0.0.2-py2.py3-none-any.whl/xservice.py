from nameko_slack import rtm


class Service:

    name = 'yoyo'

    slack_client = rtm.SlackClient()

    @rtm.handle_event
    def handle_event(self, event):
        print('--- {}'.format(event))

    '''
    @rtm.handle_event('message')
    def handle_message(self, event):
        print('*** {}'.format(event))

    @rtm.handle_message
    def handle_any_message(self, event, message):
        print(' @@@ {}'.format(event['text']))

    @rtm.handle_message('^yoyo')
    def handle_yoyo_message(self, event, message):
        print(' ... {}'.format(event['text']))
    '''

    @rtm.handle_message('^yoyo tirikam=(?P<tirikam>\w+) (\w*)')
    def handle_yoyo_parsed_message(self, event, messaqge, *args, **kwargs):
        #print(' [[[ {} ||| {}'.format(args, kwargs))
        import ipdb; ipdb.set_trace()  # FIXME
        self.slack_client.api_call(
            "chat.postMessage",
            channel="#salesforce-sync-dev",
            text="Hello from Python! :tada:",
        )
        #self.rtm_send_message('D3LPYKJ6T', 'Yo!')
        #self.rtm_send_message('ondrej', 'Yo!')
        #self.rtm_send_message('salesforce-sync-dev', 'Yo!')

    '''
    @rtm.subscribe('presence_change')
    def handle_presence_change(self, event):
        import eventlet, random
        print(' <<< START {}'.format(event))
        eventlet.sleep(random.randint(60, 120))
        print(' <<< END {}'.format(event))
    '''

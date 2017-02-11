from nameko_slack import rtm


class Service:

    name = 'yoyo'

    @rtm.handle_event
    def handle_event(self, event):
        print(event)

    '''
    @rtm.handle_event('message')
    def handle_message(self, event):
        print('message event: {}'.format(event))

    @rtm.handle_message
    def handle_any_message(self, event, message):
        print('message: {}'.format(event['text']))

    @rtm.handle_message('^yoyo')
    def handle_yoyo_message(self, event, message):
        print('yoyo message: {}'.format(event['text']))
    '''

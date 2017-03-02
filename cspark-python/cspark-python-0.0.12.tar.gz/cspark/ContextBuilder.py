class ContextBuilder:

    def __init__(self, context_engine):
        self.context = {}
        self.__context_engine = context_engine

    def build_context(self, update):
        self.context['user'] = self.__context_engine.get_data(
            _key={
                'type': 'user_context',
                'person': update.get_person_id(),
            }
        )

        if self.context['user'] is None:
            self.context['user'] = {}

        self.context['room'] = self.__context_engine.get_data(
            _key={
                'type': 'room_context',
                'room': update.get_room_id(),
            }
        )

        if self.context['room'] is None:
            self.context['room'] = {}

        self.context['user_room'] = self.__context_engine.get_data(
            _key={
                'type': 'user_room_context',
                'person': update.get_person_id(),
                'room': update.get_room_id(),
            }
        )

        if self.context['user_room'] is None:
            self.context['user_room'] = {}

    def save_context(self, update):

        self.__context_engine.put_data(
            _key={
                'type': 'user_context',
                'person': update.get_person_id(),
            },
            _value=self.context['user']
        )

        self.__context_engine.put_data(
            _key={
                'type': 'room_context',
                'room': update.get_room_id(),
            },
            _value=self.context['room']
        )

        self.__context_engine.put_data(
            _key={
                'type': 'user_room_context',
                'person': update.get_person_id(),
                'room': update.get_room_id(),
            },
            _value=self.context['user_room']
        )

    def get_context_engine(self):
        return self.__context_engine

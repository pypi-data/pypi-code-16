
import random
import copy

class Countries(object):

    def __init__(self, **kwargs):
        self.__kwargs = kwargs
        for k in kwargs:
            setattr(self, k, kwargs[k])

    @property
    def sentence(self):
        return "I am {demonym}, I'm from {name}, I speak {language}. {name} is located in {state}, the capital is {capital}."

    def ask(self):
        random_list = ['name', 'demonym']
        display_list = random.sample(random_list, 1)
        kwargs = copy.deepcopy(self.__kwargs)
        for k in kwargs:
            if k in display_list:
                kwargs[k] = getattr(self, k)
            else:
                kwargs[k] = '____'
        print self.sentence.format(**kwargs)

    @property
    def answer(self):
        return self.sentence.format(**self.__kwargs)

class Questions(object):

    QUESTIONS = [
        {'name': 'China','demonym': 'Chinese','state': 'Asia','language': 'Chinese','currency': 'RMB','capital': 'BeiJing',},
        {
            'name': 'Indonesia',
            'demonym': 'Indonesian',
            'state': 'Asia',
            'language': 'Indonesian',
            'currency': 'rupiah',
            'capital': 'Jakarta',
        },
        {
            'name': 'Germany',
            'state': 'Europe',
            'capital': 'Berlin',
            'language': 'German',
            'demonym': 'German',
            'currency': 'Euro',
        },
        {
            'name': 'Canada',
            'state': 'North America',
            'capital': 'Ottawa',
            'language': 'English and French',
            'demonym': 'Canadian',
            'currency': 'Canadian dollar',
        },
        {
            'name': 'Iran',
            'state': 'Asia',
            'capital': 'Tehran',
            'language': 'Persian',
            'demonym': 'Iranian',
            'currency': 'Rial',
        },
        {'name': 'Thailand','demonym': 'Thai','state': 'Asia','language': 'Thai','currency': 'Baht','capital': 'Bangkok',},
        {'name': 'Chile','demonym': 'Chilean','state': 'South American','language': 'Spanish','currency': 'Peso','capital': 'Santiago',},
        {'name': 'Brazil','demonym': 'Brazilian','state': 'South America','language': 'Portuguese','currency': 'Real','capital': 'Brasília',},
        # {'name': '','demonym': '','state': '','language': '','currency': '','capital': '',},
    ]

    def __init__(self):
        self.ask_questions = []
        for question in self.QUESTIONS:
            self.ask_questions.insert(0, Countries(**question))
        random.shuffle(self.ask_questions)

    def start(self):
        while self.ask_questions:
            country = self.ask_questions.pop()
            country.ask()
            raw_input()
            print country.answer

def start():
    questions = Questions()
    questions.start()

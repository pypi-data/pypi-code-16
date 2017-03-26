from .question import Question
from .exceptions import QuestionNotFound, NoQuestionsError


class Prompt(object):
    """Main entrypoint to establishing a new prompt instance""" 

    def __init__(self):
        self.questions = []
        self.answers = {}

    def get_response(self, name):
        """Get a question's response from a prompt"""
        if not self.questions:
            raise NoQuestionsError
        for answer_key, answer in self.answers.items():
            if answer_key == name:
                return answer
            return None

    @staticmethod
    def make_question(*args, **kwargs):
        """Helper to create a question instance for use with the prompt"""
        return Question.create(*args, **kwargs)

    def add(self, *args, **kwargs):
        """Add a question to a prompt

        You can add a question instance, a dictionary representing a question,
        or args and kwargs satisfying a Question constructor.
        """
        if len(args) == 1 and isinstance(args[0], Question):
            self.questions.append(args[0])
            return args[0]

        new_question = Question.create(*args, **kwargs)
        self.questions.append(new_question)
        return new_question

    def collect(self):
        """Collect the responses"""
        for question in self.questions:
            self.answers[question.name] = question.ask()
            next_question = question.get_next()
            while next_question is not None:
                self.answers[next_question.name] = next_question.ask()
                next_question = next_question.get_next()

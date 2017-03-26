from __future__ import print_function

from .compat import input
from .exceptions import (
    ValidatorIsNotCallable,
    ManipulatorIsNotCalable,
    ValidationError,
    QuestionAlreadyAnswered,
    QuestionNotAnswered,
    ConditionalAlreadyExists,
    CreateQuestionError
)


class Question(object):
    """A question is a piece to be introduced within a prompt""" 

    def __init__(self, name, question):
        self.name = name
        self.question = question
        self.response = None

        # Handle modifiers
        self.validator = None
        self.manipulator = None

        # Handle chained questions
        self.has_followup = False
        self.next_evaluator = None
        self.if_true = None
        self.if_false = None

    def __str__(self):
        """Return a question with its answer"""
        return '%s: %s' % (self.question, self.response)

    def __unicode__(self):
        """Return a question with its answer"""
        return '%s: %s' % (self.question, self.response)

    def __repr__(self):
        """Object representation"""
        return '<Question %s>' % self.name

    @classmethod
    def create(cls, *args, **kwargs):
        """Create a new question instance.

        A new question can be created from an instance of a dictionary or from
        plain keyward arguments like the main constructor.
        """
        if not args and not kwargs:
            raise CreateQuestionError

        if len(args) == 1 and isinstance(args[0], dict):
            return cls(**args[0])

        return cls(*args, **kwargs)

    def was_answered(self):
        """Determine if the question has an attached response"""
        return self.response is not None

    def ask(self):
        """Attempt to ask the the question"""
        if self.was_answered():
            raise QuestionAlreadyAnswered

        self._collect_answer(input('%s: ' % self.question))
        return self.response

    def get_next(self):
        """Get the next question if one depends on this one else None"""
        if not self.was_answered():
            raise QuestionNotAnswered

        if not self.has_followup:
            return None

        if self.next_evaluator(self.response):
            return self.if_true
        return self.if_false


    def _collect_answer(self, response):
        """Attempt to store the answer to the question.
        
        Validate the input and manipulate it if the functions exist.
        """
        resp = response
        if self.validator:
            try:
                self.validator(resp)
            except ValidationError as e:
                print(e)
                self.ask()
                return

        if self.manipulator:
            self.response = self.manipulator(resp)
        else:
            self.response = resp

    def then(self, evaluator, true_question, false_question):
        """Add a chain to a question.

        A question chain needs an evaluator function to choose which question
        to ask next. On either route, a the next question will be returned so
        it can be chanined to as well.
        """
        if self.has_followup:
            raise ConditionalAlreadyExists

        self.has_followup = True
        self.next_evaluator = evaluator
        self.if_true = true_question
        self.if_false = false_question

        return self

    def must(self, validator):
        """Add a validation function for the input"""
        if not callable(validator):
            raise ValidatorIsNotCallable
        self.validator = validator
        return self

    def transform(self, manipulator):
        """Add a manipulation function for the input"""
        if not callable(manipulator):
            raise ManipulatorIsNotCalable
        self.manipulator = manipulator
        return self

class ASKpyException(Exception):
    """There was an exception when handling your input"""


# Prompt Exceptions


class PromptException(ASKpyException):
    """A generic prompt exception occured"""


class NoQuestionsError(PromptException):
    """Your Prompt has no questions in it yet"""


# Question Exceptions


class QuestionException(ASKpyException):
    """A generic question exception occured"""


class QuestionNotFound(QuestionException):
    """The question you are looking for does not exist"""


class QuestionAlreadyAnswered(QuestionException):
    """This question was already answered"""


class QuestionNotAnswered(QuestionException):
    """This question was not answered yet"""


class CreateQuestionError(QuestionException):
    """There was an error when creating your question"""


class ConditionalAlreadyExists(QuestionException):
    """This question already has a conditional statement"""


class ValidatorIsNotCallable(QuestionException):
    """The Validator your specifed must be a function"""


class ManipulatorIsNotCalable(QuestionException):
    """The Validator your specifed must be a function"""


# Validation Exceptions


class ValidationError(ASKpyException):
    """There was a generic validation error"""

from .Response import Response


class MessageResponse(Response):
    def __init__(self, plain_text_message, markdown_message=None):
        self.__markdown_message = markdown_message
        self.__plain_text_message = plain_text_message

        if markdown_message is None:
            self.__markdown_message = self.__plain_text_message

    def get_plain_text(self):
        return self.__plain_text_message

from Core.request import Request


class Command(Request):

    def __init__(self) -> None:
        super().__init__()
    

    @staticmethod
    def is_aCommand() -> bool:
        return True
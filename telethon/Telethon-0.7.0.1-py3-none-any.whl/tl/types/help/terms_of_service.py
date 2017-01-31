from telethon.tl.mtproto_request import MTProtoRequest


class TermsOfService(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    help.termsOfService#f1ee3e90 text:string = help.TermsOfService"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xf1ee3e90

    def __init__(self, text):
        """
        :param text: Telegram type: «string».
        """
        super().__init__()

        self.text = text

    def on_send(self, writer):
        writer.write_int(TermsOfService.constructor_id, signed=False)
        writer.tgwrite_string(self.text)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return TermsOfService(None)

    def on_response(self, reader):
        self.text = reader.tgread_string()

    def __repr__(self):
        return 'help.termsOfService#f1ee3e90 text:string = help.TermsOfService'

    def __str__(self):
        return '(help.termsOfService (ID: 0xf1ee3e90) = (text={}))'.format(str(self.text))

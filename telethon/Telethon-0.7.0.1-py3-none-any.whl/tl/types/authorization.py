from telethon.tl.mtproto_request import MTProtoRequest


class Authorization(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    authorization#7bf2e6f6 hash:long flags:int device_model:string platform:string system_version:string api_id:int app_name:string app_version:string date_created:int date_active:int ip:string country:string region:string = Authorization"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x7bf2e6f6

    def __init__(self, hash, flags, device_model, platform, system_version, api_id, app_name, app_version, date_created, date_active, ip, country, region):
        """
        :param hash: Telegram type: «long».
        :param flags: Telegram type: «int».
        :param device_model: Telegram type: «string».
        :param platform: Telegram type: «string».
        :param system_version: Telegram type: «string».
        :param api_id: Telegram type: «int».
        :param app_name: Telegram type: «string».
        :param app_version: Telegram type: «string».
        :param date_created: Telegram type: «int».
        :param date_active: Telegram type: «int».
        :param ip: Telegram type: «string».
        :param country: Telegram type: «string».
        :param region: Telegram type: «string».
        """
        super().__init__()

        self.hash = hash
        self.flags = flags
        self.device_model = device_model
        self.platform = platform
        self.system_version = system_version
        self.api_id = api_id
        self.app_name = app_name
        self.app_version = app_version
        self.date_created = date_created
        self.date_active = date_active
        self.ip = ip
        self.country = country
        self.region = region

    def on_send(self, writer):
        writer.write_int(Authorization.constructor_id, signed=False)
        writer.write_long(self.hash)
        writer.write_int(self.flags)
        writer.tgwrite_string(self.device_model)
        writer.tgwrite_string(self.platform)
        writer.tgwrite_string(self.system_version)
        writer.write_int(self.api_id)
        writer.tgwrite_string(self.app_name)
        writer.tgwrite_string(self.app_version)
        writer.write_int(self.date_created)
        writer.write_int(self.date_active)
        writer.tgwrite_string(self.ip)
        writer.tgwrite_string(self.country)
        writer.tgwrite_string(self.region)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return Authorization(None, None, None, None, None, None, None, None, None, None, None, None, None)

    def on_response(self, reader):
        self.hash = reader.read_long()
        self.flags = reader.read_int()
        self.device_model = reader.tgread_string()
        self.platform = reader.tgread_string()
        self.system_version = reader.tgread_string()
        self.api_id = reader.read_int()
        self.app_name = reader.tgread_string()
        self.app_version = reader.tgread_string()
        self.date_created = reader.read_int()
        self.date_active = reader.read_int()
        self.ip = reader.tgread_string()
        self.country = reader.tgread_string()
        self.region = reader.tgread_string()

    def __repr__(self):
        return 'authorization#7bf2e6f6 hash:long flags:int device_model:string platform:string system_version:string api_id:int app_name:string app_version:string date_created:int date_active:int ip:string country:string region:string = Authorization'

    def __str__(self):
        return '(authorization (ID: 0x7bf2e6f6) = (hash={}, flags={}, device_model={}, platform={}, system_version={}, api_id={}, app_name={}, app_version={}, date_created={}, date_active={}, ip={}, country={}, region={}))'.format(str(self.hash), str(self.flags), str(self.device_model), str(self.platform), str(self.system_version), str(self.api_id), str(self.app_name), str(self.app_version), str(self.date_created), str(self.date_active), str(self.ip), str(self.country), str(self.region))

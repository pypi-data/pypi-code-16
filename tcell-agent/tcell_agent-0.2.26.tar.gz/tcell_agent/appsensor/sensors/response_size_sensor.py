from tcell_agent.appsensor.sensors import SizeSensor


class ResponseSizeSensor(SizeSensor):
    MAX_NORMAL_RESPONSE_BYTES = 1024 * 1024 * 2
    DP_UNUSUAL_RESPONSE_SIZE = "rspsz"

    def __init__(self, policy_json=None):
        super(ResponseSizeSensor, self).__init__(
            self.MAX_NORMAL_RESPONSE_BYTES,
            self.DP_UNUSUAL_RESPONSE_SIZE,
            policy_json
        )

    def get_size(self, appsensor_meta):
        return appsensor_meta.response_content_bytes_len

from tcell_agent.appsensor.sensors import SizeSensor


class RequestSizeSensor(SizeSensor):
    MAX_NORMAL_REQUEST_BYTES = 1024 * 512
    DP_UNUSUAL_REQUEST_SIZE = "reqsz"

    def __init__(self, policy_json=None):
        super(RequestSizeSensor, self).__init__(
            self.MAX_NORMAL_REQUEST_BYTES,
            self.DP_UNUSUAL_REQUEST_SIZE,
            policy_json
        )

    def get_size(self, appsensor_meta):
        return appsensor_meta.request_content_bytes_len

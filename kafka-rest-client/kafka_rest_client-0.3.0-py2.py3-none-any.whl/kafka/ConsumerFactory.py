from proofpoint.kafka.KafkaRestConsumer import KafkaRestConsumer


class ConsumerFactory:
    def __init__(self):
        pass

    # This is the factory method
    @staticmethod
    def createConsumer(**configs):
        return KafkaRestConsumer(configs)

from amaascore.core.amaas_model import AMaaSModel


class Reference(AMaaSModel):

    def __init__(self, reference_value, active=True, version=1, *args, **kwargs):
        self.reference_value = reference_value
        self.active = active
        self.version = version
        super(Reference, self).__init__(*args, **kwargs)

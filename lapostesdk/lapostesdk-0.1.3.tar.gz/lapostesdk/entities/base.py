class BaseEntity(object):
    def hydrate(self, data):
        for k in data:
            if hasattr(self, k):
                setattr(self, k, data[k])

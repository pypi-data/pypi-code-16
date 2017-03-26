class Data(object):
    def __init__(self):
        raise NotImplementedError()

    def get_train_data_iterator(self):
        raise NotImplementedError()

    def get_test_data_iterator(self):
        raise NotImplementedError()

    def get_inputs_dim(self):
        return self.inputs_dim

    def get_labels_dim(self):
        return self.labels_dim
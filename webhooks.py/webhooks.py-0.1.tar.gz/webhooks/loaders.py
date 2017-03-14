from yaml import load_all


class YamlLoader:
    def __init__(self, yaml_path):
        with open(yaml_path, 'r') as fobj:
            documents = [doc for doc in load_all(fobj)]

            if len(documents) == 1:
                meta, content = None, documents[0]
            elif len(documents) == 2:
                meta, content = documents
            else:
                raise ValueError('File needs to have 2 documents')

            self.meta = meta
            self.data = content

    def rules(self):
        for rule in self.data:
            print(rule)
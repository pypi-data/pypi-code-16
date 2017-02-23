from .vectorizers import DocVectorizer
from sklearn.svm import SVC


class BaseClassifier(object):

    def __init__(self, vectorizer=DocVectorizer()):

        self.vectorizer = vectorizer

    def fit(self, documents):
        """
        :param documents: a dict containing text as keys and label as values
        """

        self.text_vectors = self.vectorizer.fit_transform(list(documents.keys()))

    def predict(self, documents):
        pass


class SVMClassifier(BaseClassifier):

    def fit(self, documents):
        BaseClassifier.fit(self, documents)

        self.sk_model = SVC()

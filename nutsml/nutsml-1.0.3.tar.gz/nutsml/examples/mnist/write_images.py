from keras.datasets import mnist
from nutsflow import Take, Print, Consume
from nutsml import WriteImage


def load_samples():
    (X_train, y_train), (X_test, y_test) = mnist.load_data()
    return zip(X_train, y_train), zip(X_test, y_test)


if __name__ == '__main__':
    train_samples, val_samples = load_samples()
    imagepath = 'images/img_*.png'
    (train_samples >> Take(10) >> Print('label: {1}') >>
     WriteImage(0, imagepath) >> Consume())

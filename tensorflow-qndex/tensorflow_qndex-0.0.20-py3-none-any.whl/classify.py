import argtyp
import extenteten as ex
import tensorflow as tf
import qnd


def def_num_classes():
    qnd.add_required_flag("num_classes", type=int)

    def num_classes():
        return qnd.FLAGS.num_classes

    return num_classes


def def_num_labels():
    qnd.add_flag("num_labels", type=int)

    def num_labels():
        return qnd.FLAGS.num_labels

    return num_labels


def def_classify():
    get_num_classes = def_num_classes()
    get_num_labels = def_num_labels()
    qnd.add_flag("hidden_layer_sizes", type=argtyp.int_list, default=[100])
    qnd.add_flag("dropout_keep_prob", type=float)

    def classify(feature, label=None, *,
                 mode, key=None, regularization_scale=1e-8):
        num_classes = get_num_classes()

        if num_classes <= 1:
            raise ValueError("Number of classes must be greater than 1.")

        num_labels = get_num_labels() or ex.num_labels(label)

        return ex.classify(
            ex.mlp(
                feature,
                layer_sizes=[
                    *qnd.FLAGS.hidden_layer_sizes,
                    ex.num_logits(num_labels, num_classes)],
                dropout_keep_prob=(
                    qnd.FLAGS.dropout_keep_prob
                    if mode == tf.contrib.learn.ModeKeys.TRAIN else
                    None)),
            label,
            num_classes=num_classes,
            num_labels=num_labels,
            key=key,
            regularization_scale=regularization_scale)

    return classify

import tensorflow as tf

def get_predictions(inp, restore_point):
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(restore_point + '.meta')
        saver.restore(sess, restore_point)
        x = tf.get_collection('x')[0]
        prediction = tf.get_collection('prediction')[0]
        return sess.run(prediction, feed_dict={x: inp})
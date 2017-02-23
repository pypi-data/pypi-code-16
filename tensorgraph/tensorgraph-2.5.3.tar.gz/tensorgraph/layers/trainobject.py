


    gpu_options=tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
    with tf.Session(config = tf.ConfigProto(gpu_options = gpu_options)) as sess:
        init = tf.initialize_all_variables()
        sess.run(init)

        max_epoch = 300
        es = tg.EarlyStopper(max_epoch=max_epoch,
                     epoch_look_back=3,
                     percent_decrease=0)
        temp_acc = []
        best_valid_accu = 0
        for epoch in range(max_epoch):
            print 'epoch:', epoch
            train_error = 0
            train_accuracy = 0
            ttl_examples = 0
            pbar = tg.ProgressBar(len(trainset_X))
            for X_batch, wx_batch, ys, seqlen_batch in zip(trainset_X, trainset_WX, trainset_y, train_seqlen):
                feed_dict = {X_ph:X_batch[0]}
                feed_dict[wx_ph] = wx_batch[0]
                feed_dict[seqlen_ph] = seqlen_batch[0]
                for y_ph, y_batch in zip(y_phs, ys):
                    feed_dict[y_ph] = y_batch

                sess.run(optimizer, feed_dict=feed_dict)
                train_outs = sess.run(train_outs_sb, feed_dict=feed_dict)
                train_error += total_mse(train_outs, ys)[0]
                train_accuracy += total_accuracy(train_outs, ys)[0]
                ttl_examples += len(X_batch[0])
                pbar.update(ttl_examples)
            print 'train mse', train_error/float(ttl_examples)
            print 'train accuracy', train_accuracy/float(ttl_examples)


            valid_error = 0
            valid_accuracy = 0
            ttl_examples = 0
            pbar = tg.ProgressBar(len(validset_X))
            for X_batch, wx_batch, ys, seqlen_batch in zip(validset_X, validset_WX, validset_y, valid_seqlen):
                feed_dict = {X_ph:X_batch[0]}
                #dim0 = wx_batch[0].shape(0)
                feed_dict[wx_ph] = wx_batch[0]
                feed_dict[seqlen_ph] = seqlen_batch[0]
                for y_ph, y_batch in zip(y_phs, ys):
                    feed_dict[y_ph] = y_batch

                valid_outs = sess.run(test_outs, feed_dict=feed_dict)
                valid_error += total_mse(valid_outs, ys)[0]
                valid_accuracy += total_accuracy(valid_outs, ys)[0]
                ttl_examples += len(X_batch[0])
                pbar.update(ttl_examples)

            mean_valid_cost = valid_error/float(ttl_examples)
            print 'valid mse', mean_valid_cost
            valid_accuracy /= float(ttl_examples)
            print 'valid accuracy', valid_accuracy
            temp_acc.append(valid_accuracy)
            if best_valid_accu < valid_accuracy:
                best_valid_accu = valid_accuracy

            if es.continue_learning(valid_error=mean_valid_cost):
                print('epoch', epoch)
                # print 'valid error so far:', mean_valid_cost
                print('best epoch last update:', es.best_epoch_last_update)
                print('best valid last update:', es.best_valid_last_update)
                print('best valid accuracy:', best_valid_accu)
            else:
                print('training done!')
                break


        print('average accuracy is:\t', sum(temp_acc)/len(temp_acc))

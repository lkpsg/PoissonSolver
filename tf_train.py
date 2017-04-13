# -*- coding: utf-8 -*-
import tensorflow as tf
import scipy.io as sio
import numpy as np
import random
import matplotlib.pyplot as plt
import input_data
import tf_possion

global_step = tf.Variable(0, trainable=False)
starter_learning_rate = 0.0001
sess = tf.InteractiveSession(config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=False))
#with tf.device('/gpu:2'):
y_predict,rmse,mean_db = tf_possion.model(is_training=True)
#y_predict_test,rmse_test,mean_db_test = tf_possion.model(is_training=False)
#with tf.device('/gpu:1'):
train_step = tf.train.AdamOptimizer(0.001).minimize(rmse)
#train_step = tf.train.GradientDescentOptimizer(0.001).minimize(rmse)

merged_summary_op = tf.summary.merge_all()
summary_writer = tf.summary.FileWriter('./logs', sess.graph)
#tf.reset_default_graph()

sess.run(tf.global_variables_initializer())
x_train,y_train = input_data.input_data(test=False)
x_test,y_test = input_data.input_data(test=True)

epochs = 10000
train_size = x_train.shape[0]
#print(train_size)
global batch
batch = 40
test_size = x_test.shape[0]

train_index = list(range(x_train.shape[0]))
random.shuffle(train_index)
x_train,y_train = x_train[train_index],y_train[train_index]
test_index = list(range(x_test.shape[0]))
random.shuffle(test_index)
x_test,y_test = x_test[test_index],y_test[test_index]
for i in range(epochs):
    global_step = i
    learning_rate = tf.train.exponential_decay(starter_learning_rate, global_step,500, 0.8, staircase=True)
    random.shuffle(train_index)
    random.shuffle(test_index)
    x_train,y_train = x_train[train_index],y_train[train_index]
    x_test,y_test = x_test[test_index],y_test[test_index]

    for j in range(0,train_size,batch):
        train_step.run(feed_dict={tf_possion.x:x_train[j:j+batch],tf_possion.y_actual:y_train[j:j+batch],tf_possion.keep_prob:0.5})
    

    temp = 0
    train_loss=0
#        if (i%30)==0:
    for j in range(0,train_size,batch):
        train_loss = rmse.eval(feed_dict={tf_possion.x:x_train[j:j+batch],tf_possion.y_actual:y_train[j:j+batch],tf_possion.keep_prob: 1.0})
        temp = temp + train_loss
    train_loss = temp/(train_size/batch)

    temp_loss = 0
    temp_db = 0
    meandb = 0
    loss = 0
#        if (i%30)==0:
    for j in range(0,test_size,batch):
        loss = rmse.eval(feed_dict={tf_possion.x:x_test[j:j+batch],tf_possion.y_actual:y_test[j:j+batch],tf_possion.keep_prob: 1.0})
        meandb = mean_db.eval(feed_dict={tf_possion.x:x_test[j:j+batch],tf_possion.y_actual:y_test[j:j+batch],tf_possion.keep_prob: 1.0})
        temp_loss = temp_loss+loss
        temp_db = temp_db+meandb

    loss = temp_loss/(test_size/batch)
    meandb = temp_db/(test_size/batch)

    if i==750:
        y_print = y_predict.eval(feed_dict={tf_possion.x:x_test[0:batch],tf_possion.y_actual:y_test[0:batch],tf_possion.keep_prob: 1.0})
        #result = tf.scalar_summary('y_result',y_print)
        #print 'y_print {0}'.format(y_print)
        with open('y_print.txt','wb') as f:
            np.savetxt(f,y_print,fmt='%s')
        aa=y_test[0].reshape(32,32)
        aa_test=y_print[0].reshape(32,32)
        #plt.figure(1)
        #plt.imshow(aa)
        #plt.figure(2)
        #plt.imshow(aa_test)
        #plt.show()
        sio.savemat('result.mat',{'aa':y_test[0:batch],'aa_test':y_print})
    summary_str = sess.run(merged_summary_op,feed_dict={tf_possion.x:x_test[0:batch],tf_possion.y_actual:y_test[0:batch],tf_possion.keep_prob: 1.0})
    summary_writer.add_summary(summary_str,j)
    print ('epoch {0} done! train_loss:{1} test_loss:{2} db:{3} global_step:{4} learning rate:{5}'.format(i,train_loss, loss, meandb,int(global_step),learning_rate.eval()))
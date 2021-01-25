#coding=utf-8
#训练文件
import paddle
import paddle.fluid as fluid
import os
from paddle.v2.plot import Ploter
import numpy as np

train = './data/train.log'
test  = './data/test.log'

train_title = "Train cost"
test_title = "Test cost"
cost_ploter = Ploter(train_title,test_title)

global params_dirname 
params_dirname = "predict.model"

def train_reader():
    def reader():
        with open(train,'r') as f:
            lines = [line.strip() for line in f]
            for line in lines:
                line = line.split()
                x = line[0:9]
                y = line[9:11]
                yield x,y
    return reader



def test_reader():
    def reader():
        with open(test,'r') as f:
            lines = [line.strip() for line in f]
            for line in lines:
                line = line.split()
                x = line[0:9]
                y = line[9:11]
                yield x,y
    return reader

#定义前向传播
def forward():
    x = fluid.layers.data(name='x',shape=[1,9],dtype='float32')
    hidden = fluid.layers.fc(input=x,size=36,act='relu')
    y_predict = fluid.layers.fc(input=hidden,size=2,act='softmax')
    return y_predict

def train_program():
    y_label = fluid.layers.data(name='y_label',shape=[2],dtype='float32')
    
    #使用前向传播
    predict = forward()
    
    #计算cost
    cost = fluid.layers.square_error_cost(input=predict, label=y_label)
    avg_cost = fluid.layers.mean(cost)
    return avg_cost

#优化方法采用l2正则化
def optimizer_program():
    return fluid.optimizer.Adam(learning_rate=0.001,regularization=fluid.regularizer.L2DecayRegularizer(4e-4))

steps = 0

def main():
    
    #训练数据
    train_buff = paddle.batch(paddle.reader.shuffle(train_reader(),buf_size = 1000),batch_size=100) 
    #测试数据
    test_buff = paddle.batch(paddle.reader.shuffle(test_reader(),buf_size = 1000),batch_size=100) 
    
    
    #是否使用显卡
    use_cuda = False # set to True if training with GPU
    place = fluid.CUDAPlace(0) if use_cuda else fluid.CPUPlace()
    
    #设置trainer
    trainer = fluid.Trainer(train_func=train_program, place=place, optimizer_func=optimizer_program)

    lists = []
   

    #打印训练事件
    def event_handler(event):
        global steps
        if isinstance(event, fluid.EndStepEvent):
            if steps % 1000 == 0:  
                avg_cost= trainer.test(reader = test_buff,feed_order=['x', 'y_label'])
                cost_ploter.append(train_title, steps, event.metrics[0])
                cost_ploter.append(test_title, steps, avg_cost)
                lists.append((steps, event.epoch,event.metrics[0]))
                #生成图像
                #cost_ploter.plot()
                #打印数据
                print "avg_cost: "+str(avg_cost)
        steps = steps + 1
        #print lists
        if isinstance(event, fluid.EndEpochEvent):
            # 保存模型
            trainer.save_params(params_dirname)
       
    
    #训练模型
    trainer.train(
        #较低的学习率匹配较高的迭代轮数
        num_epochs=4000,
        event_handler=event_handler,
        reader=train_buff,
        feed_order=['x', 'y_label'])
    
   

if __name__ == '__main__':
    main()
#coding=utf-8
#预测文件
import paddle
import paddle.fluid as fluid
import os
from paddle.v2.plot import Ploter
import numpy as np

global params_dirname 
params_dirname = "/JIT_WAF/predict/predict.model"#模型位置
data  = '/JIT_WAF/data_log/predict_data.log'#数据位置
data_out = '/JIT_WAF/data_log/ip_out.log'#预测结果文件
#是否使用显卡
use_cuda = False # set to True if training with GPU
place = fluid.CUDAPlace(0) if use_cuda else fluid.CPUPlace()
#记录文件行数
n=0 
def load(data):
    with open(data,'r') as f:
        lines = [line.strip() for line in f]
        lists = []
        global n
        n=0
        for line in lines:
            line = line.split()
            lists.append(line[0:9])  
            n=n+1
        return lists
def loading(data):
    with open(data,'r') as f:
        for line in f.readlines():
            line = line.split()
            yield line[9],line[10]

#定义前向传播
def forward():
    x = fluid.layers.data(name='x',shape=[1,9],dtype='float32')
    hidden = fluid.layers.fc(input=x,size=36,act='relu')
    y_predict = fluid.layers.fc(input=hidden,size=2,act='softmax')
    return y_predict

def main():
    inferencer = fluid.Inferencer(
        infer_func=forward,  
        param_path=params_dirname,
        place=place)
    tensor_x = np.array(load(data)).reshape(n,9).astype(np.float32)
    results = inferencer.infer({'x': tensor_x})
    #输出结果
    lab = np.argsort(results)
    #格式化输出结果
    i=0
    for ip,time in loading(data):
        ip_out = str(ip) +' '+ str(time)+' '
        print ip,time,
        if(i<=n):
            print lab[0][i]
            ip_out+=str(lab[0][i][-1])
            i+=1    
        with open(data_out,'a') as t:
            t.write(ip_out+'\n')
if __name__ == '__main__':
    main()
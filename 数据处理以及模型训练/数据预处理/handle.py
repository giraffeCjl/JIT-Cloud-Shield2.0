#coding=utf-8
#NCSA扩展/组合日志格式：“%h %l %u %t \”%r\” %>s %b \”%{Referer}i\” \”%{User-agent}i\”"
import random
import time
import datetime
import numpy
import re

data_log = 'access.log'
data_out = 'predict_data.log'
#数据预处理，转化为数值类型，并归一化。

max_ip = 4294967295
min_ip = 0

def nor_ip(data):
    data = float(data)
    global max_ip,min_ip
    data = (data-min_ip)/(max_ip-min_ip)
    return data

max_iden_fir = 50
min_iden_fir = 40

max_iden_sec = 50
min_iden_sec = 40

def nor_iden(data):
    data = float(data)
    global max_iden_fir,min_iden_fir
    data = (data-min_iden_fir)/(max_iden_fir-min_iden_fir)
    return data

max_address = 1000
min_address = 0

def nor_address(data):
    data = float(data)
    global max_address,min_address
    data = (data-min_address)/(max_address-min_address)
    return data

max_action = 3000
min_action = 0

def nor_action(data):
    data = float(data)
    global max_action,min_action
    data = (data-min_action)/(max_action-min_action)
    return data

max_status_fir = 5000
min_status_fir = 0

def nor_status_fir(data):
    data = float(data)
    global max_status_fir,min_status_fir
    data = (data-min_status_fir)/(max_status_fir-min_status_fir)
    return data

max_status_sec = 5000
min_status_sec = 0

def nor_status_sec(data):
    data = float(data)
    global max_status_sec,min_status_sec
    data = (data-min_status_sec)/(max_status_sec-min_status_sec)
    return data

max_refer = 5000
min_refer = 0

def nor_refer(data):
    data = float(data)
    global max_refer,min_refer
    data = (data-min_refer)/(max_refer-min_refer)
    return data

max_agent = 10000
min_agent = 0

def nor_agent(data):
    data = float(data)
    global max_agent,min_agent
    data = (data-min_agent)/(max_agent-min_agent)
    return data

#字符串转ASCII
def encode(s):
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

def wash(x):
    x = x.split(',')
    x = str(x)
    x = x.replace("\"","")
    x = x.replace("\\","")
    x = x.replace("\'","")
    x = x.replace("]","")
    x = x.replace("[","")
    x = x.replace("(","")
    x = x.replace(")","")
    x = x.replace(";","")
    x = x.replace("+","")
    x = x.strip()
    return x
#特殊清洗方法
def wash_spe(x):
    x = str(x)
    x = x.replace("\"","")
    x = x.replace("\\","")
    x = x.replace("\'","")
    x = x.replace("]","")
    x = x.replace("[","")
    x = x.replace("(","")
    x = x.replace(")","")
    x = x.replace(";","")
    x = x.replace("+","")
    x = x.replace(",","")
    x = x.strip()
    return x

def wash_ip(ip_str):
    ip_long = 0
    for index,value in enumerate(reversed([int(x) for x in ip_str.split('.')])):
        ip_long += value<<(8*index)
    return ip_long
#对iden_fir 和 iden_sec 数值化
def wash_many(data):
    data = encode(data)
    data = data.split()
    lenth = len(data)
    x = 0
    for i in range(lenth):
        x = int(data[i],2)+ x
    return x

def wash_time(data):
    #%d/%b/%Y:%H:%M:%S
    # string转化结构化时间
    time_array = time.strptime(data, "%d/%b/%Y:%H:%M:%S")
    # 结构化时间转时间戳
    timestamp = time.mktime(time_array)
    return timestamp

def wash_address(data):
    data = data.replace("+",'')
    data = int(data)
    return data

def wash_action(data):
    data = encode(data)
    data = data.split()
    lenth = len(data)
    x = 0
    for i in range(lenth):
        x = int(data[i],2)+ x
    return x

def after(data_log,data_out):
    with open(data_log,'r') as f:
        for line in f.readlines():
            #切割字符串
            lines = line
            line = line.split()
            #对应字段
            ip = line[0]
            iden_fir = line[1]
            iden_sec = line[2]
            time = wash(line[3])
            address = wash(line[4])
            #开始匹配引号后面的数据
            p= re.compile(r'(?<=").*?(?=")')
            x = p.findall(lines)
            action = x[0]
            status = str(x[1])
            status = status.split()
            status_fir = status[0]
            status_sec = status[1]
            refer = x[2]
            agent = x[4]

            
            #转为数值类型
            ip = str(wash_ip(ip))
            iden_fir = str(wash_many(iden_fir))
            iden_sec = str(wash_many(iden_sec))
            address = str(wash_address(address))
            action = str(wash_action(action))
            status_fir = str(wash_many(status_fir))
            status_sec = str(wash_many(status_sec))
            refer = str(wash_many(refer))
            agent = str(wash_many(agent))
            
            #不作为训练数据
            time = str(time)
            #归一化处理使数值在【0，1】之间
            ip = str(nor_ip(ip))
            iden_fir = str(nor_iden(iden_fir))
            iden_sec = str(nor_iden(iden_sec))
            address = str(nor_address(address))
            action = str(nor_action(action))
            status_fir = str(nor_status_fir(status_fir))
            status_sec = str(nor_status_sec(status_sec))
            refer = str(nor_refer(refer))
            agent = str(nor_agent(agent))
            
            #共记9个纬度
            #对每一维数据做出针对的清洗转化为数值格式
            #将处理过的数据输出到文件
            log = ''
            log = ip+' '+iden_fir+' '+iden_sec+' '+address+' '+action+' '+status_fir+' '+status_sec+' '+refer+' '+agent+' '+line[0]+' '+time
            with open(data_out,'a') as t:
                t.write(log+'\n')
            
                        
after(data_log,data_out)
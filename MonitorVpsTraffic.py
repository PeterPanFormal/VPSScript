# encoding: utf-8
# 用于监控vps的流量, 在超限时执行对应操作
# It is used to monitor the traffic of vps and perform the corresponding operation when exceeding the limit

from __future__ import division

import os
import re
import time
import calendar
import datetime

# 流量数据写入到文件中, 这里自己指定网卡，一般是 eth0，阿里云是 eth1, ovz的机器是venet0
# Flow data is written to the file, where you specify the network card, usually eth0, Ali cloud is eth1, ovz the machine is venet0
os.system("vnstat -m -i eth0 > /root/FlowControl/tx.txt")
# 保险起见延迟1秒，给予命令执行时间
# Delay for 1 second, give the order execution time
time.sleep(1) 

# 获取当前月份
# Get the current month
def get_now_month():
    now_month_num = time.strftime("%m")
    # 月份数字转英文, 中文环境下应该改为 : num_to_en = {'01':'1月','02':'2月','03':'3月','04':'4月','05':'5月','06':'6月','07':'7月','08':'8月','09':'9月','10':'10月','11':'11月','12':'12月'}
    # Month figures turn English, Chinese environment should be changed to: num_to_en = {'01':'1月','02':'2月','03':'3月','04':'4月','05':'5月','06':'6月','07':'7月','08':'8月','09':'9月','10':'10月','11':'11月','12':'12月'}
    num_to_en = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}
    return num_to_en[now_month_num]

# 读取文件
# Read the file
f = []
for line in open("/root/FlowControl/tx.txt"):
    f.append(line),

# 定位到本月所在行
# Locate this month's line
def ftext():
    for i in range(0,len(f)):
        if re.search(get_now_month(),f[i]):
            return f[i]

# 提取"tx"所在的字符位置,同时提取一下"rx"(即服务器收到的流量 在用作代理的情况下, rx>tx)
# Extracts the character position where "tx" is located and extracts "rx" (that is, rx> tx when the traffic received by the server is used as a proxy)
tx = re.findall(r"\|(.*?)\|", ftext())[0]
subIndex = ftext().index('GiB') - 9
rx = re.findall(r"\s(.*?)\|", ftext()[subIndex:])[0]
# rx或者tx达到GB级别,才进入判断
# rx or tx reached the GB level before entering the judge
if re.search(r"GiB",tx) or re.search(r"GiB",rx):
    if re.search(r"MiB",tx):
         tx = rx
    elif re.search(r"MiB",rx):
         rx = tx
    # 处理字符串得到具体的流量数值
    # Processing string to get the specific value of the flow
    tx_data =  float(re.sub(r"\s","",tx)[:-3])
    rx_data =  float(re.sub(r"\s","",rx)[:-3])
    if rx_data > tx_data:
        tx_data = rx_data
    # 大于490G关闭443 80端口
    # Greater than 490G close the 443 80 port
    if tx_data > 490:
        os.system("firewall-cmd --permanent --zone=public --remove-port=443/tcp")
        os.system("firewall-cmd --permanent --zone=public --remove-port=80/tcp")
        os.system("firewall-cmd --reload")
        os.system("date=`date +%Y-%m-%d_%H:%M:%S` && echo ${date}' 服务器流量已超过490G，自动关闭443 80端口' >> /root/FlowControl/stopss.log")
    elif tx_data > 499:
        os.system("firewall-cmd --permanent --zone=public --remove-port=80/tcp")
        os.system("firewall-cmd --permanent --zone=public --remove-port=443/tcp")
        os.system("firewall-cmd --reload")
        os.system("date=`date +%Y-%m-%d_%H:%M:%S` && echo ${date}' 服务器流量已超过499G，自动关闭80 443端口' >> /root/FlowControl/stopss.log")
    else:
        today = datetime.date.today()
        _, last_day_num = calendar.monthrange(today.year, today.month)
        if tx_data >= today.day/last_day_num * 500:
            os.system("firewall-cmd --permanent --zone=public --remove-port=8888/tcp")
            os.system("firewall-cmd --permanent --zone=public --remove-port=8899/tcp")
            os.system("firewall-cmd --permanent --zone=public --remove-port=8888/udp")
            os.system("firewall-cmd --permanent --zone=public --remove-port=8899/udp")
            os.system("firewall-cmd --permanent --zone=public --remove-port=24/tcp")
            os.system("firewall-cmd --permanent --zone=public --remove-port=24/udp")
            os.system("firewall-cmd --reload")
            os.system("date=`date +%Y-%m-%d_%H:%M:%S` && echo ${date}' 服务器流量当前已超限，自动关闭8888 8899 24端口' >> /root/FlowControl/stopss.log")
        else:
            os.system("firewall-cmd --permanent --zone=public --add-port=8888/tcp")
            os.system("firewall-cmd --permanent --zone=public --add-port=8899/tcp")
            os.system("firewall-cmd --permanent --zone=public --add-port=8888/udp")
            os.system("firewall-cmd --permanent --zone=public --add-port=8899/udp")
            os.system("firewall-cmd --permanent --zone=public --add-port=24/tcp")
            os.system("firewall-cmd --permanent --zone=public --add-port=24/udp")
            os.system("firewall-cmd --reload")
            os.system("date=`date +%Y-%m-%d_%H:%M:%S` && echo ${date}' 服务器流量当前未超限，自动开启8888 8899 24端口' >> /root/FlowControl/stopss.log")
    cmd = "date=`date +%Y-%m-%d_%H:%M:%S` && echo ${date}' 服务器当前已使用流量 "+str(tx_data)+" GiB' >> /root/FlowControl/stopss.log"
    os.system(cmd)
elif re.search(r"MiB",tx) and re.search(r"MiB",rx):
    tx_data =  float(re.sub(r"\s","",tx)[:-3])
    rx_data =  float(re.sub(r"\s","",rx)[:-3])
    if rx_data > tx_data:
        tx_data = rx_data
    cmd = "date=`date +%Y-%m-%d_%H:%M:%S` && echo ${date}' 服务器当前已使用流量 "+str(tx_data)+" MiB' >> /root/FlowControl/stopss.log"
    os.system(cmd)
else:pass


# VPS服务器脚本 VPSScript

<br/>功能
<br/>Features
<br/>监控vps的流量, 并在流程超过限制的时候自动关闭对应的端口, 主要在使用有限流量的服务器翻墙的情况下使用
<br/>Monitoring vps traffic, and automatically shut down the corresponding port when the process exceeds the limit, mainly in the case of cross GFW with server using a limited amount of traffic
<br/>
<br/>适用环境
<br/>Applicable environment
<br/>CentOS 7 x64
<br/>
<br/>使用方式
<br/>How to use
<br/>1 yum -y install vnstat
<br/>2 vnstat -u -i eth0
<br/>3 添加定时任务 Add a timed task
<br/>(crontab -e) 1,21,41 * * * * python /root/FlowControl/txss.py

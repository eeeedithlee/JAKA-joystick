#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket

ip_port = ('172.30.0.8', 20000)

s = socket.socket()     # 创建套接字

s.connect(ip_port)      # 连接服务器

while True:     # 通过一个死循环不断接收用户输入，并发送给服务器
    server_reply = s.recv(1024).decode()
    print(server_reply)
    if server_reply =="wave":
        break

s.close()       # 关闭连接
print("success!")

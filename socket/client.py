# -*- coding: utf-8 -*-

import socket

# remote host name and port
HOST = 'localhost'
PORT = 1234
ADDR = (HOST, PORT)
BUF_SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
while 1:
    input = raw_input('please input:')
    client.send(input)
    data = client.recv(BUF_SIZE)
    if data:
        print 'client----', data
    # client.close()

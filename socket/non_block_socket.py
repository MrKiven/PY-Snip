# -*- coding: utf-8 -*-

import socket
import select
import threading
import os

HOST = 'localhost'
PORT = 1234
ADDR = (HOST, PORT)
BUF_SIZE = 1024
THREAD_NUM = 0


def process_request(request, addr):
    print 'server connected by: ', addr
    while 1:
        data = request.recv(BUF_SIZE)
        if not data:
            break
        print 'server recv: ', data
        request.send('server received success')
    request.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server.setblocking(False)
server.bind(ADDR)
server.listen(1)
print 'server ready pid: ', os.getpid()

while 1:
    r, w, e = select.select([server, ], [], [], 0)
    if server in r:
        conn, addr = server.accept()
        # conn.setblocking(False)
        THREAD_NUM += 1
        print 'thread count: ', THREAD_NUM
        t = threading.Thread(target=process_request,
                             name='server process thread' + str(THREAD_NUM),
                             args=(conn, addr))
        t.start()

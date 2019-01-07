#!/usr/bin/env python
import sys
import os
import errno
import socket
import traceback
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 42642        # Port to listen on (non-privileged ports are > 1023)
import time
#We have to define an output function a placeholder here.
def output(data):
    print data

#A function to shutdown an existing processes
def closeSocket():
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.connect((HOST, PORT))
    sc.sendall(b'close server')
    sc.close()
end_trans = '###END-TRANS###'
#This is a wrapper for the client sockets
class socketWrapper(object):

    def __init__(self, skt):
        self._socket = skt

    def read(self):
        cmd = ''
        while end_trans not in cmd:
            data = self._socket.recv(1024)
            if not data:
                cmd = '###BROKEN###'
                break
            cmd += data
        if cmd == '###BROKEN###':
            return ''
        return cmd.replace(end_trans, '')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Put in a try/except in case there is an orphaned process. We can shut it down first and start afresh
try:
    s.bind((HOST, PORT))
except socket.error as serr:
    if serr.errno == errno.EADDRINUSE:
        closeSocket()
        s.bind((HOST, PORT))
s.listen(1024)
while True:
    conn, addr = s.accept()
    sock = socketWrapper(conn)
    cmd = sock.read()
    #Here we define the output method to just send the output of the diracCommand wrapper.
    def output(data):
        conn.sendall(repr(data))

    if cmd=='close-server':
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        break
    try:
        print(eval(cmd))
    except:
        try:
            exec(cmd)
        except:
            print("Exception raised executing command (cmd) '%s'\n" % cmd)
            print(traceback.format_exc())

    conn.sendall('###END-TRANS###')

s.shutdown(socket.SHUT_RDWR)
s.close()

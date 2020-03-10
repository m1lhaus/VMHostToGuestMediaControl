#!/usr/bin/env python

import socket
import time

import key_enums

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65433        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    for i in range(5):
        s.sendall(str(key_enums.Keys.PLAYPAUSE_DOWN).encode())
        s.sendall(str(key_enums.Keys.PLAYPAUSE_UP).encode())
        time.sleep(2)
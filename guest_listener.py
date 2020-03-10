#!/usr/bin/env python

import socket
import guest_press_key

HOST = '127.0.0.1'
PORT = 65433


def listen():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(F"Binded and listening on {(HOST, PORT)}")

        while True:
            conn, addr = s.accept()
            with conn:
                with guest_press_key.KeySender() as key_sender:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(2)
                        if not data:
                            break
                        print("Received", data)
                        key_sender.press_key(int(data))
            print(addr, "disconnected")


if __name__ == '__main__':
    listen()

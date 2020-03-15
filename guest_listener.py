#!/usr/bin/env python

import socket
import evdev

from key_enums import Keys


class KeySender(evdev.uinput.UInput):

    def __init__(self):
        super(KeySender, self).__init__()

        self.key_mapping = {
            Keys.STOP: self.press_stop,
            Keys.PLAYPAUSE: self.press_playpause,
            Keys.PREV: self.press_prev,
            Keys.NEXT: self.press_next
        }

    def __press_key(self, key_id):
        print(F"Sending key id {key_id} to uinput")
        self.write(evdev.ecodes.EV_KEY, key_id, 1)
        self.write(evdev.ecodes.EV_KEY, key_id, 0)
        self.syn()

    def press_playpause(self):
        self.__press_key(evdev.ecodes.KEY_PLAYPAUSE)

    def press_stop(self):
        self.__press_key(evdev.ecodes.KEY_STOPCD)

    def press_next(self):
        self.__press_key(evdev.ecodes.KEY_NEXTSONG)

    def press_prev(self):
        self.__press_key(evdev.ecodes.KEY_PREVIOUSSONG)

    def press_key(self, enum):
        handler_method = self.key_mapping[enum]
        handler_method()


class KeyListener:
    def __init__(self, host_ip, port):
        self.host_ip = host_ip
        self.port = port

    def start_listening(self):
        print(f"Started, will try to bind to {(self.host_ip, self.port)}...")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host_ip, self.port))
            s.listen()

            print(F"Binded and listening on {(self.host_ip, self.port)}")

            while True:
                print("Waiting for connection")

                conn, addr = s.accept()
                with conn:
                    with KeySender() as key_sender:
                        print('Connected client from', addr)
                        while True:
                            try:
                                data = conn.recv(64)
                            except ConnectionResetError:
                                print("Connection terminated by client the hard way!")
                                break

                            if data:
                                self.process_data(key_sender, data)
                            else:
                                break

                print(addr, "Client disconnected")

    @staticmethod
    def process_data(key_sender, data):
        data = data.decode()
        for str_id in data:
            print("Received key num id", str_id)
            key_sender.press_key(int(str_id))


if __name__ == '__main__':
    HOST = '192.168.192.128'        # default vmware NAT address
    PORT = 65433

    incoming_listener = KeyListener(HOST, PORT)
    incoming_listener.start_listening()

#!/usr/bin/env python

import socket
import time
import threading
import queue

import ctypes
import ctypes.wintypes

import key_enums


class _MediaKeyListener:

    def __init__(self, msg_queue: queue.Queue):
        self.stop_flag = threading.Event()
        self.is_registered = threading.Event()

        self.message_queue = msg_queue
        self.retryTimerInterval = 5.0       # sec

        self.WM_HOTKEY = 0x0312
        self.WM_TIMER = 0x0113
        self.WM_HOTKEYS = {
            1: (0xB3, 'VK_MEDIA_PLAY_PAUSE'),
            2: (0xB2, 'VK_MEDIA_STOP'),
            3: (0xB0, 'VK_MEDIA_NEXT_TRACK'),
            4: (0xB1, 'VK_MEDIA_PREV_TRACK'),
        }
        self.WM_HOTKEYS_mapping = {
            1: key_enums.Keys.PLAYPAUSE,
            2: key_enums.Keys.STOP,
            3: key_enums.Keys.NEXT,
            4: key_enums.Keys.PREV,
        }

    def start_listening(self):
        """
        Thread worker. Called when thread is executed.
        Listens for all system-wide messages. Method makes thread busy, unresponsive!
        """
        self.register_hotkeys()
        self.is_registered.wait()
        if self.stop_flag.is_set():          # in case thread is being stopped
            return

        print("Starting windows key-down hook (listener) loop.")
        try:
            msg = ctypes.wintypes.MSG()

            # GetMessageA() is blocking function - it waits until some message is received
            # so timer posts its WM_TIMER every 100ms and wakes GetMessageA() function
            timer_id = ctypes.windll.user32.SetTimer(None, None, 100, None)

            # handles the WM_HOTKEY messages and pass everything else along.
            while not self.stop_flag.is_set() and ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == self.WM_HOTKEY:
                    # process -> call handler
                    print("Message:", msg.wParam)
                    hotkey_enum = self.WM_HOTKEYS_mapping[msg.wParam]
                    self.message_queue.put(hotkey_enum)         # send a message to sender

            print("Killing win32 listen timer...")
            ctypes.windll.user32.KillTimer(None, timer_id)
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))

        finally:
            self.unregister_hotkeys()

    def schedule_registration_retry(self):
        if not self.stop_flag.is_set():
            threading.Timer(self.retryTimerInterval, self.register_hotkeys).start()

    def register_hotkeys(self):
        """
        Call Win32 API to register global shortcut (hotkey) for current thread id.
        Only this (worker) thread is then notified when shortcut is executed.
        """
        success = True
        for hk_id, (vk, vk_name) in list(self.WM_HOTKEYS.items()):
            if not ctypes.windll.user32.RegisterHotKey(None, hk_id, 0, vk):
                success = False
                break

        if success:
            self.is_registered.set()
        else:
            print("Registration of keys failed, scheduling retry...")
            self.is_registered.clear()
            self.schedule_registration_retry()

    def unregister_hotkeys(self):
        """
        Call Win32 API to unregister global shortcut (hotkey) for current thread id.
        """
        for hk_id in list(self.WM_HOTKEYS.keys()):
            ctypes.windll.user32.UnregisterHotKey(None, hk_id)

        self.is_registered.clear()

    def stop_listening(self):
        self.stop_flag.set()
        self.is_registered.set()        # to not get stuck on wait() in worker

    def reset(self):
        self.stop_flag.clear()
        self.is_registered.clear()


class MediaKeyListener:

    def __init__(self):
        self.listener = _MediaKeyListener()
        self.listener_thread = threading.Thread(target=self.listener.start_listening, name="HotkeyListenerThread")

    def start(self):
        print("Starting...")
        self.listener.reset()
        self.listener_thread.start()

    def stop(self):
        self.listener.stop_listening()
        self.listener_thread.join()
        print("Stopped")


class _Sender:
    def __init__(self, ip, port, msg_queue: queue.Queue):
        self.stop_flag = threading.Event()

        self.ip = ip
        self.port = port
        self.msg_queue = msg_queue

    def start_sending(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # s.connect((self.ip, self.port))

            while not self.stop_flag.is_set():
                key_enum = self.msg_queue.get(block=True)
                print(key_enum)

            # for i in range(5):
            #     s.sendall(str(key_enums.Keys.PLAYPAUSE_DOWN).encode())
            #     s.sendall(str(key_enums.Keys.PLAYPAUSE_UP).encode())
            #     time.sleep(2)

    def stop_sending(self):
        self.stop_flag.set()
        self.msg_queue.put(None)        # just to wakeup worker

    def reset(self):
        self.stop_flag.clear()
        if not self.msg_queue.empty():
            self.msg_queue.task_done()


class Sender:
    def __init__(self, ip, port, msg_queue: queue.Queue):
        self.sender = _Sender(ip, port, msg_queue)
        self.sender_thread = threading.Thread(target=self.sender.start_sending, name="SenderThread")

    def start(self):
        self.sender.reset()
        self.sender_thread.start()

    def stop(self):
        self.sender.stop_sending()
        self.sender_thread.join()


if __name__ == '__main__':
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65433        # Port to listen on (non-privileged ports are > 1023)
    QUEUE = queue.Queue(1024)

    # m = MediaKeyListener()
    # m.start()
    # time.sleep(10)
    # m.stop()

    sender = Sender(HOST, PORT, QUEUE)
    sender.start()
    time.sleep(10)
    sender.stop()

from key_enums import Keys

from evdev import uinput, ecodes as e


class KeySender(uinput.UInput):

    def __init__(self):
        super(KeySender, self).__init__()

        self.key_mapping = {
            Keys.STOP: self.press_stop,
            Keys.PLAYPAUSE: self.press_playpause,
            Keys.PREV: self.press_prev,
            Keys.NEXT: self.press_next
        }

    def __press_key(self, key_id):
        print(F"Pressing key {key_id} down")
        self.write(e.EV_KEY, key_id, 1)
        self.write(e.EV_KEY, key_id, 0)
        self.syn()

    def press_playpause(self):
        self.__press_key(e.KEY_PLAYPAUSE)

    def press_stop(self):
        self.__press_key(e.KEY_STOPCD)

    def press_next(self):
        self.__press_key(e.KEY_NEXTSONG)

    def press_prev(self):
        self.__press_key(e.KEY_PREVIOUSSONG)

    def press_key(self, enum):
        handler_method = self.key_mapping[enum]
        handler_method()


# if __name__ == '__main__':
#     press_play_pause()
#     press_stop()
#     press_prev()
#     press_next()

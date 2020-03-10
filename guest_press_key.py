from key_enums import Keys

from evdev import uinput, ecodes as e


class KeySender(uinput.UInput):

    def __init__(self):
        super(KeySender, self).__init__()

        self.key_mapping = {
            Keys.STOP_UP: self.press_stop_up,
            Keys.STOP_DOWN: self.press_stop_down,
            Keys.PLAYPAUSE_UP: self.press_playpause_up,
            Keys.PLAYPAUSE_DOWN: self.press_playpause_down,
            Keys.PREV_UP: self.press_prev_up,
            Keys.PREV_DOWN: self.press_prev_down,
            Keys.NEXT_UP: self.press_next_up,
            Keys.NEXT_DOWN: self.press_next_down
        }

    def __press_key_down(self, key_id):
        print(F"Pressing key {key_id} down")
        self.write(e.EV_KEY, key_id, 1)
        self.syn()

    def __press_key_up(self, key_id):
        print(F"Pressing key {key_id} up")
        self.write(e.EV_KEY, key_id, 0)
        self.syn()

    def press_playpause_down(self):
        self.__press_key_down(e.KEY_PLAYPAUSE)

    def press_playpause_up(self):
        self.__press_key_up(e.KEY_PLAYPAUSE)

    def press_stop_down(self):
        self.__press_key_down(e.KEY_STOPCD)

    def press_stop_up(self):
        self.__press_key_up(e.KEY_STOPCD)

    def press_next_down(self):
        self.__press_key_down(e.KEY_NEXTSONG)

    def press_next_up(self):
        self.__press_key_up(e.KEY_NEXTSONG)

    def press_prev_down(self):
        self.__press_key_down(e.KEY_PREVIOUSSONG)

    def press_prev_up(self):
        self.__press_key_up(e.KEY_PREVIOUSSONG)

    def press_key(self, enum):
        handler_method = self.key_mapping[enum]
        handler_method()


# if __name__ == '__main__':
#     press_play_pause()
#     press_stop()
#     press_prev()
#     press_next()

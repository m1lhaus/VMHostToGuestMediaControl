from evdev import uinput, ecodes as e


def __press_key(key_id):
    with uinput.UInput() as ui:
        ui.write(e.EV_KEY, key_id, 1)
        ui.write(e.EV_KEY, key_id, 0)
        ui.syn()


def press_play_pause():
    __press_key(e.KEY_PLAYPAUSE)


def press_stop():
    __press_key(e.KEY_STOPCD)


def press_next():
    __press_key(e.KEY_NEXTSONG)


def press_prev():
    __press_key(e.KEY_PREVIOUSSONG)


# if __name__ == '__main__':
#     press_play_pause()
#     press_stop()
#     press_prev()
#     press_next()

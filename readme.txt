Dependencies:
-------------
- python 3+
- evdev (https://python-evdev.readthedocs.io/en/latest/index.html)

Setup:
-------
- unable user to access udev
    e.g. sudo echo 'KERNEL=="uinput", TAG+="uaccess' > /etc/udev/rules.d/50-uinput.rules

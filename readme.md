# VMHostToGuestMediaControl

This project was created to implement ability to control media playback on Linux guest virtual machine from host Windows machine. 

**Example usecase:**

You are running virtual machine based on usual Linux distro on your Windows machine. You are playing some music inside that VM (e.g. your Spotify i playing inside Ubuntu VM) and you want to control media playback (play/pause, etc.) same way you do it on your host (local) machine.

As far as I know, there is no supported way how to send global hotkey keypress from host machine to inside your guest virtual machine. Only way is to have focus on your VM window. This might get really annoying searching for the window every time you need to pause/skip the song. That why I implemented this two part Python tool.

## Host script

Made from two functional parts connected between each other via Python queue since each part is running in its own thread. 

**Global hotkey listener**

- using ctypes and win32 API
- rather than running as dirty keyhook, it registers global hotkey via win32 
    - drawback - registration might fail if other app already registered this shortcut => retry until success
    - benefit - it won't read and mess with any other keypresses like regular keyhook (safe with regards to special keyboard layouts, dead keys, etc.)
- puts received hotkey to Python queue for sending

**Sender**

- connects to server running on guest
- listens for a key put to the queue
- send stuff from queue to guest

## Guest script

Also made from two parts. One reads incoming messages and second emits those message as keypresses using `uinput`.

**Listener**

- nothing special, just receives incoming TCP/IP messages

**Keypress sender**

- uses [evdev](https://python-evdev.readthedocs.io/en/latest/index.html) wrapper to send key_dow/key_up presses to `uinput`

## Dependencies:

Most importantly you need to figure out your communication between host and guest. Scripts are using TCP/IP so in theory you are not limited to just local communication. However using port forwarding in VMWare it can be pure local-only (see example on bottom).

### Windows
- Python 3+
- ctypes

### Linux host
- [udev](https://linux.die.net/man/8/udev)
- Python 3+
- [evdev](https://python-evdev.readthedocs.io/en/latest/index.html)

#### Setup udev for evdev:

You need to allow `evdev` package to interact with `udev`. Enable user to access `udev` by writting 
```
KERNEL=="uinput", TAG+="uaccess"
```
to
```bash
$ sudo nano /etc/udev/rules.d/50-uinput.rules
```

## Example localhost-only communication with VMWare

Following shows how to configure host/guest for local communication only using VMWare. Benefit is that you can avoid messing with firewall setting on host machine under which you do not have full control (e.g. company pc). It also works under corporate conditions since it avoid proxy and VPN tunnel.

1. Set NAT for your container
2. Get guest IP address 
3. Use Virtual Network Editor to set port forwarding (VMWare Workstation only) or edit manually `c:\ProgramData\VMware\vmnetnat.conf`
    ```
    [incomingtcp]
    
    # assuming that 192.168.192.128 is IP address of running VM container
    65433 = 192.168.192.128:65433
    ```
4. If NAT edited manually, restart NAT service (cmd):
    ```
    > net stop "VMWare NAT Service"
    > net start "VMWare NAT Service"
    ```

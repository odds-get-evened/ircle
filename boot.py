import binascii
import datetime
import random
import secrets

import socket
import string
import time
from hashlib import sha256
from threading import Thread

import chardet

FUNCS = [
    ["a", "b", "0", "1", "#"],
    [">", "<", "|", "^", "*"]
]


def heartbeat():
    now = datetime.datetime.now()
    hrtbt_s = secrets.choice(FUNCS[0]) + secrets.choice(FUNCS[1]) + " @" + now.strftime("%Y-%m-%d %H:%M:%S")
    hrtbt_h = sha256(hrtbt_s.encode()).hexdigest()

    return f"{hrtbt_s}; checksum: {hrtbt_h}"


class IRC:
    irc_socket = socket.socket()
    encoding = None
    channel = None

    def __init__(self):
        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, chan, msg):
        self.irc_socket.send(("PRIVMSG " + chan + " :" + msg + "\r\n").encode(self.encoding))

    def connect(self, server, chan, nick):
        self.channel = chan
        print("connecting to " + server)
        self.irc_socket.connect((server, 6667))
        init_txt = self.irc_socket.recv(1024)
        self.encoding = chardet.detect(init_txt)['encoding']

        self.irc_socket.send(
            bytes("USER " + nick + " " + nick + " " + nick + " :keeping things a'tickin...\r\n", self.encoding))
        self.irc_socket.send(bytes("NICK " + nick + "\r\n", self.encoding))
        self.irc_socket.send(bytes("JOIN " + self.channel + "\r\n", self.encoding))

        self.start_loop()

    def start_loop(self):
        self.loop = Thread(target=self.loop)
        self.loop.start()

    def loop(self):
        """
        background process that triggers heartbeats
        every n seconds.
        """
        now = datetime.datetime.now()
        s = now.timestamp()
        while True:
            e = datetime.datetime.now().timestamp() - s

            if e >= 300: # every 5 minutes
                hrtbt = heartbeat()

                self.send(self.channel, hrtbt)
                s = datetime.datetime.now().timestamp()  # reset timer

            time.sleep(1)  # interrupt thread so IRC server messages can come through

    def get_text(self):
        txt = self.irc_socket.recv(2048)

        if txt.find(b"PING") != -1:
            print("we got pinged, so PONG!")
            pong = bytes(f"PONG :{str(txt.split(b':')[1].strip())}\r\n", self.encoding)
            self.irc_socket.send(pong)

        return txt


def initialize():
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))

    server = 'irc.efnet.org'  # set this to desired server name
    channel = '#archivr'  # set to desired channel name
    ''' bot nick with random hash string appended '''
    b_tnick = 'hrtb_' + hex(binascii.crc32(rand_str.encode('utf8')))[2:]

    irc = IRC()
    irc.connect(server, channel, b_tnick)

    while True:
        txt = irc.get_text()
        enc = chardet.detect(txt)['encoding']
        print(txt.decode(enc))

        if b"PRIVMSG" in txt and channel.encode(enc) in txt and b"!hello" in txt:
            irc.send(channel, "well, hello there!")

        ''' if a chat user requests an impulse, present it to chat! '''
        if b"PRIVMSG" in txt and channel.encode(enc) in txt and b"!impulse" in txt:
            irc.send(channel, heartbeat())

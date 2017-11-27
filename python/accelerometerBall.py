import sys
import random
import signal
import time
import binascii
import numpy as np

from bluepy import btle

from demo_opts import get_device

import luma.core.render
from luma.core.sprite_system import framerate_regulator

class Ball(object):
    def __init__(self, w, h, radius, color):
        self._w = w
        self._h = h
        self._radius = radius
        self._color = color
        self._x_pos = self._w / 2.0
        self._y_pos = self._h / 2.0

    def update_pos(self, x, y):
        self._x_pos += x
        self._y_pos += y
        if self._x_pos > self._w:
            self._x_pos = self._w
        elif self._x_pos <= 0:
            self._x_pos = 0
        if self._y_pos > self._h:
            self._y_pos = self._h
        elif self._y_pos <= 0:
            self._y_pos=0

    def draw(self, canvas):
        print(self._x_pos - self._radius, self._y_pos - self._radius,
                       self._x_pos + self._radius, self._y_pos + self._radius)
        canvas.ellipse((self._x_pos - self._radius, self._y_pos - self._radius,
                       self._x_pos + self._radius, self._y_pos + self._radius), fill=self._color)
    def getpos(self):
        pos=[int(round(self._x_pos - self._radius)), int(round(self._y_pos - self._radius)), int(round(self._x_pos + self._radius)), int(round(self._y_pos + self._radius))]
        return pos

def translate(value, min, max):
    return value * min / max

def main(num_iterations=sys.maxsize):

    p = btle.Peripheral("XX:XX:XX:XX:XX:XX", btle.ADDR_TYPE_RANDOM)

    p.setSecurityLevel("medium")

    svc = p.getServiceByUUID("e95d0753-251d-470a-a062-fa1922dfa9a8")
    ch = svc.getCharacteristics("e95dca4b-251d-470a-a062-fa1922dfa9a8")[0]
    chper = svc.getCharacteristics("e95dfb24-251d-470a-a062-fa1922dfa9a8")[0]
   
    print(ch)
    CCCD_UUID = 0x2902

    ch_cccd=ch.getDescriptors(forUUID=CCCD_UUID)[0]
    print(ch_cccd)
    ch_cccd.write(b"\x00\x00", False)
    
    ball = Ball(device.width, device.height, 2, "white")

    frame_count = 0
    fps = ""
    canvas = luma.core.render.canvas(device)

    regulator = framerate_regulator(fps=25)

    points=0

    while True:
            with canvas as c:
                c.rectangle(device.bounding_box, outline="black", fill="black")
                c.ellipse((58.0, 26.0, 70.0, 38.0), outline="white", fill="black")
                
                coord = np.fromstring(ch.read(), dtype=np.int16, count=3)

                x = translate(coord[0],32,1040)
                y = translate(coord[1],32,980)
                ball.update_pos(x,y)
                ball.draw(c)
                pos=ball.getpos()
                if (pos[0] > 58 and pos[1] > 26 and pos[2] < 70 and pos[3] < 38):
                    text="!!!"
                    points+=1
                else:
                    text=""
                c.text((2, 0), str(points)+" "+text, fill="white")

if __name__ == '__main__':
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass

import spidev
import random
from colorsys import hsv_to_rgb
import itertools

def fuzzy_equals(a, b, margin):
    return abs(a - b) < margin

class Pixel(object):
    def next_color(self):
        return (0, 0, 0)

class RandomPixel(Pixel):
    def __init__(self, step):
        self.step = step
        self.target = random.random()
        self.hue = self.target
    def next_color(self):
        if fuzzy_equals(self.hue, self.target, self.step):
            self.target = random.random()
        elif self.hue < self.target:
            self.hue += self.step
        else:
            self.hue -= self.step
        return tuple([int(v * 255) for v in hsv_to_rgb(self.hue, 1, 1)])

class LedString(object):
    def __init__(self, length):
        self.pixels = []
        self.buffer = [0] * length * 3
    def animate(self):
        colors = list([p.next_color() for p in self.pixels])
        for i, color in enumerate(itertools.cycle(colors)):
            if i*3 >= len(self.buffer):
                break
            self.buffer[i*3:(i+1)*3] = color
        return self.buffer

def main():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 400000
    spi.mode = 0b01

    leds = LedString(50)
    leds.pixels = list([RandomPixel(0.002) for _ in range(0, 2)])

    while True:
        spi.xfer(leds.animate())

if __name__ == '__main__':
    main()


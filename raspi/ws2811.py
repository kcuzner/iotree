import spidev
import random
from colorsys import hsv_to_rgb
import itertools

def fuzzy_equals(a, b, margin):
    return abs(a - b) < margin

class Pixel(object):
    """
    Defines a single LED pixel which has color changing capabilities
    """
    def next_color(self):
        return (0, 0, 0)

class RandomHuePixel(Pixel):
    """
    Pixel which smoothly transitions to random hues
    """
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

class Keyframe(object):
    """
    Handles transitioning between color keyframes. This is simply a hard
    transition
    """
    def __init__(self, color):
        self.color = color
    def interpolate(self, other, cursor):
        if cursor < 0.5:
            return self.color
        else:
            return other.color

class LinearKeyframe(Keyframe):
    """
    Transitions linearly between this color and the next
    """
    def __init__(self, color):
        super(Keyframe, self).__init__(color)
    def interpolate(self, other, cursor):
        m = self.other - self.color
        return m * cursor + self.color

class KeyframePixel(Pixel):
    """
    Pixel which follows a series of keyframes, repeating them over and over
    """
    def __init__(self, keys, step):
        self.keys = keys
        self.step = step
        self.index = 0
    def next_color(self):
        index = int(self.index)
        cursor = self.index - index
        next_index = int((self.index + 1) % len(self.keys))
        color = self.keys[index].interpolate(self.keys[next_index], cursor)
        self.index += self.step
        return color

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

    keys = [Keyframe((255, 255, 0)), Keyframe((0, 0, 255))]

    leds = LedString(50)
    leds.pixels = list([RandomHuePixel(0.002) for _ in range(0, 10)])

    while True:
        spi.xfer(leds.animate())

if __name__ == '__main__':
    main()


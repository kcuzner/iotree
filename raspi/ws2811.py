from __future__ import print_function
import spidev
import random, sched, time, math, argparse, json, queue
from colorsys import hsv_to_rgb, rgb_to_hsv
import itertools
import redis

import common

def fuzzy_equals(a, b, margin):
    return abs(a - b) < margin

class Pixel(object):
    """
    Defines a single LED pixel which has color changing capabilities.

    The pixel color sequence is exposed as an iterator
    """
    def __iter__(self):
        return self
    def __next__(self):
        return (0, 0, 0)
    def next(self):
        return self.__next__()

class RandomHuePixel(Pixel):
    """
    Pixel which smoothly transitions to random hues
    """
    def __init__(self, step):
        self.step = step
        self.target = random.random()
        self.hue = self.target
    def __next__(self):
        if fuzzy_equals(self.hue, self.target, self.step):
            self.target = random.random()
        elif self.hue < self.target:
            self.hue += self.step
        else:
            self.hue -= self.step
        return tuple([int(v * 255) for v in hsv_to_rgb(self.hue, 1, 1)])

class Keyframe(object):
    """
    Handles transitioning between color keyframes. This implementation is
    simply a hard transition.
    """
    def __init__(self, color, steps=None, max_steps=50):
        self.steps = steps
        self.max_steps = max_steps
        self.color = color

    def interpolate(self, other):
        if not self.steps:
            steps = int(random.random() * self.max_steps) + 1
        else:
            steps = self.steps
        for i in range(0, steps+1):
            cursor = float(i) / float(steps)
            yield self.interpolate_step(other, cursor)

    def interpolate_step(self, other, cursor):
        if cursor < 0.5:
            return self.color
        else:
            return other.color

class LinearKeyframe(Keyframe):
    """
    Transitions linearly between this color and the next
    """
    def interpolate_step(self, other, cursor):
        return tuple([int((oc - sc) * cursor) + sc for oc, sc in
            zip(other.color, self.color)])

class SineKeyframe(LinearKeyframe):
    """
    Uses a sine wave to transition between colors
    """
    def interpolate_step(self, other, cursor):
        modcursor = math.sin(cursor * math.pi / 2)
        return super(SineKeyframe, self).interpolate_step(other, modcursor)

class KeyframePixel(Pixel):
    """
    Pixel which follows a series of keyframes, repeating them over and over
    """
    def __init__(self, keys):
        self.keys = keys

    def __iter__(self):
        keylen = len(self.keys)
        while True:
            for i, k in enumerate(self.keys):
                for pix in k.interpolate(self.keys[(i+1) % keylen]):
                    yield pix

class LedString(object):
    def __init__(self, length):
        self.__pixeliters = []
        self.buffer = [0] * length * 3
    def set_pixels(self, pixels):
        self.__pixeliters = list([iter(p) for p in pixels])
    def animate(self):
        colors = list([next(p) for p in self.__pixeliters])
        for i, color in enumerate(itertools.cycle(colors)):
            if i*3 >= len(self.buffer):
                break
            self.buffer[i*3:(i+1)*3] = color
        return self.buffer

def load_pixels(doc):
    for d in doc:
        if d['type'] == 'random-hue':
            yield RandomHuePixel(float(d['step']))
        elif d['type'] == 'keyframe':
            keys = []
            for k in d['keys']:
                color = (int(k['r']), int(k['g']), int(k['b']))
                steps = int(k['steps']) if 'steps' in k else None
                max_steps = int(k['max_steps']) if 'max-steps' in k else None
                if k['type'] == 'linear':
                    keys.append(LinearKeyframe(color, steps, max_steps))
                elif k['type'] == 'sine':
                    keys.append(SineKeyframe(color, steps, max_steps))
                elif k['type'] == 'wall':
                    keys.append(Keyframe(color, steps, max_steps))
            yield KeyframePixel(keys)

def deserialize_pixels(serialized):
    try:
        doc = json.loads(serialized)
        pixels = list(load_pixels(doc))
        return pixels
    except TypeError:
        return []
    except KeyError:
        return []

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi WS2811 SPI Controller')
    parser.add_argument('--settings', default='./settings.json')

    args = parser.parse_args()
    settings = common.read_settings(args.settings)

    db = common.open_redis(settings)
    p = db.pubsub()
    p.subscribe('pixels')

    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 400000
    spi.mode = 0b01

    pixels = list(load_pixels(settings['initial-pattern']))
    leds = LedString(50)
    leds.set_pixels(pixels)

    s = sched.scheduler(time.time, time.sleep)

    def run_leds():
        s.enter(0.03, 0, run_leds, ())
        spi.xfer(leds.animate())

    def handle_requests():
        s.enter(0.01, 1, handle_requests, ())
        while True:
            msg = p.get_message()
            if msg and msg['type'] == 'message':
                pixels = list(deserialize_pixels(msg['data']))
                if len(pixels):
                    leds.set_pixels(pixels)
            elif not msg:
                break

    run_leds()
    handle_requests()
    s.run()

if __name__ == '__main__':
    main()


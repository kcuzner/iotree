import spidev
import random
from colorsys import hsv_to_rgb

def main():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 400000
    spi.mode = 0b01

    targets = list([random.random() for _ in range(0, 50)])
    hues = list(targets)

    while True:
        rgb = list([hsv_to_rgb(h, 1, 1) for h in hues])
        buf = [int(v * 255) for v in sum(rgb, ())]
        spi.xfer(buf)

if __name__ == '__main__':
    main()


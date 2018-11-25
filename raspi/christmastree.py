from __future__ import print_function
import json, argparse, os, logging, fcntl, errno
import redis, v4l2

def read_settings(filename):
    with open(filename) as f:
        return json.load(f)

def xioctl(fd, req, arg):
    while True:
        try:
            r = fcntl.ioctl(fd, req, arg)
        except IOError as e:
            if e.errno != errno.EINTR:
                raise
        else:
            break

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi Christmas Tree Controller')
    parser.add_argument('--settings', default='./settings.json')

    args = parser.parse_args()
    settings = read_settings(args.settings)

    r = redis.StrictRedis(host=settings['redis-hostname'], port=settings['redis-port'])

    # Open V4L2 device and query its capabilities
    with open(settings['video'], 'rw') as vd:
        cp = v4l2.v4l2_capability()
        xioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)
        print(cp.card)
        print(hex(cp.capabilities))

if __name__ == '__main__':
    main()


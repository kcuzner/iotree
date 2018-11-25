import json, argparse, os, logging
import redis, cv2
import numpy as np

LOCAL_REDIS_HOST = '127.0.0.1'
LOCAL_REDIS_PORT = 6379

def read_settings(filename):
    with open(filename) as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi Christmas Tree Controller')
    parser.add_argument('--settings', default='./settings.json')

    args = parser.parse_args()
    settings = read_settings(args.settings)

    r = redis.StrictRedis(host=LOCAL_REDIS_HOST, port=LOCAL_REDIS_PORT)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise ValueError('Unable to open video capture')
    try:
        while True:
            ret, frame = cap.read()
    except:
        print("releasing capture")
        cap.release()
        raise

if __name__ == '__main__':
    main()


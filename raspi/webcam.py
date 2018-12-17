from __future__ import print_function
import json, argparse, os, logging, fcntl, errno, mmap, select, time
from ctypes import addressof, c_long
import redis, v4l2

IMAGE_KEY = 'image'
IMAGETIME_KEY = 'image:time'

def read_settings(filename):
    with open(filename) as f:
        return json.load(f)

def xioctl(fd, req, arg):
    """
    Wrapper around ioctl that polls it until it no longer returns EINTR
    """
    while True:
        try:
            r = fcntl.ioctl(fd, req, arg)
        except IOError as e:
            if e.errno != errno.EINTR:
                raise
            print("Waiting...")
        else:
            return r

def get_video_formats(fd):
    """
    Enumerates the video formats supported by the device
    """
    i = 0
    while True:
        desc = v4l2.v4l2_fmtdesc()
        desc.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        desc.index = i
        try:
            xioctl(fd, v4l2.VIDIOC_ENUM_FMT, desc)
            yield desc
        except IOError as e:
            # This ioctl will return EINVAL when the end of the sequence is
            # reached.
            if i > 0 and e.errno == errno.EINVAL:
                return
            raise
        i += 1

def get_framesizes(fd, pixfmt):
    """
    Enumerates the frame sizes supported by the device

    pixfmt: u32 describing the pixel format
    """
    i = 0
    while True:
        fs = v4l2.v4l2_frmsizeenum()
        fs.pixel_format = pixfmt
        fs.index = i
        try:
            xioctl(fd, v4l2.VIDIOC_ENUM_FRAMESIZES, fs)
            yield fs
        except IOError as e:
            if i > 0 and e.errno == errno.EINVAL:
                return
            raise
        i += 1

class VideoBuffer(object):
    """
    Holds a set of buffers and returns bytes
    """
    def __init__(self, vd, count):
        breq = v4l2.v4l2_requestbuffers()
        breq.count = count
        breq.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        breq.memory = v4l2.V4L2_MEMORY_MMAP
        xioctl(vd, v4l2.VIDIOC_REQBUFS, breq)
        print('Requested {} buffers. Received {} buffers.'\
                .format(count, breq.count))
        self.vd = vd
        self.mmaps = []
        for i in range(count):
            buf = v4l2.v4l2_buffer()
            buf.index = i
            buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = v4l2.V4L2_MEMORY_MMAP
            xioctl(vd, v4l2.VIDIOC_QUERYBUF, buf)
            self.mmaps.append(mmap.mmap(vd.fileno(), buf.length,
                flags=mmap.MAP_SHARED, prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=buf.m.offset))
            # Add the buffer to the incoming queue
            xioctl(vd, v4l2.VIDIOC_QBUF, buf)
            print("Allocated buffer {}".format(i))

    def run(self):
        self.stop = False
        while not self.stop:
            # Remove the buffer from the outgoing queue
            buf = v4l2.v4l2_buffer()
            buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = v4l2.V4L2_MEMORY_MMAP
            buf.reserved2 = 0
            # This blocks when there is no buffer in the outgoing queue
            xioctl(self.vd, v4l2.VIDIOC_DQBUF, buf)
            self.mmaps[buf.index].seek(0)
            yield (self.mmaps[buf.index].read(buf.bytesused), \
                    float(buf.timestamp.secs) + float(buf.timestamp.usecs) * 1e-6)
            # Add the buffer back to the incoming queue
            buf.flags = 0
            buf.reserved2 = 0
            xioctl(self.vd, v4l2.VIDIOC_QBUF, buf)

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi Webcam Streaming Controller')
    parser.add_argument('--settings', default='./settings.json')

    args = parser.parse_args()
    settings = read_settings(args.settings)


    password = settings['redis-password'] if settings['redis-auth'] else None
    db = redis.StrictRedis(host=settings['redis-hostname'], port=settings['redis-port'], password=password)

    # Open V4L2 device
    with open(settings['video'], 'r+') as vd:
        # Start by querying its capabilities
        cp = v4l2.v4l2_capability()
        xioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)
        if cp.capabilities & v4l2.V4L2_CAP_VIDEO_CAPTURE == 0:
            raise ValueError('Device {} does not support video capture'.format(settings['video']))
        # Find a suitable format the camera supports.
        # Right now I only want to support MJPG since I can throw this directly
        # to clients and it can be shown in the browser with minimal serverside
        # computation.
        formats = [f for f in get_video_formats(vd) if f.pixelformat == v4l2.V4L2_PIX_FMT_MJPEG]
        if len(formats) == 0:
            raise ValueError('Device {} does not support the M-JPEG format directly'.format(settings['video']))
        # Find the largest size. For ease of use, I'm only supporting discrete sizing.
        sizes = list(reversed(sorted([s for s in get_framesizes(vd, v4l2.V4L2_PIX_FMT_MJPEG) if
            s.type == v4l2.V4L2_FRMSIZE_TYPE_DISCRETE and
            s.discrete.width * s.discrete.height < settings['pixels']], key=lambda s: s.discrete.width * s.discrete.height)))
        if len(list(sizes)) == 0:
            raise ValueError('Device {} does not support discrete step sizes'.format(settings['video']))
        framesize = sizes[0]
        # Select the camera format
        vidfmt = v4l2.v4l2_format()
        vidfmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        vidfmt.fmt.pix.width = framesize.discrete.width
        vidfmt.fmt.pix.height = framesize.discrete.height
        vidfmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_MJPEG # well that naming's inconsistent...
        vidfmt.fmt.field = v4l2.V4L2_FIELD_NONE
        xioctl(vd, v4l2.VIDIOC_S_FMT, vidfmt)
        print('Video format selected.')
        print('  Resolution: {} x {}'.format(vidfmt.fmt.pix.width,
            vidfmt.fmt.pix.height))
        print('  Format: {:X}'.format(vidfmt.fmt.pix.pixelformat))
        # Request video buffer allocation
        buffers = VideoBuffer(vd, 4)
        # Begin capture
        print('Begin capture.')
        buftype = c_long(v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE)
        xioctl(vd, v4l2.VIDIOC_STREAMON, addressof(buftype))
        start = time.time()
        end = start
        count = 1
        for frame, timestamp in buffers.run():
            #print ('Frame: {}'.format(time.time() - end))
            s = time.time()
            db.set(IMAGE_KEY, frame, px=1000)
            db.set(IMAGETIME_KEY, timestamp)
            #print ('Upload: {}'.format(time.time() - s))
            end = time.time()
            if end - start > 1.0:
                print('FPS: {}'.format(count / (end-start)))
                start = end
                count = 1
            else:
                count += 1
        xioctl(vd, v4l2.VIDIOC_STREAMOFF, addressof(buftype))


if __name__ == '__main__':
    main()


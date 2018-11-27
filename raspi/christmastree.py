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

def main():
    parser = argparse.ArgumentParser(description='Raspberry Pi Christmas Tree Controller')
    parser.add_argument('--settings', default='./settings.json')

    args = parser.parse_args()
    settings = read_settings(args.settings)

    db = redis.StrictRedis(host=settings['redis-hostname'], port=settings['redis-port'])

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
            s.type == v4l2.V4L2_FRMSIZE_TYPE_DISCRETE], key=lambda s: s.discrete.width * s.discrete.height)))
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
        breq = v4l2.v4l2_requestbuffers()
        breq.count = 1
        breq.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        breq.memory = v4l2.V4L2_MEMORY_MMAP
        xioctl(vd, v4l2.VIDIOC_REQBUFS, breq)
        buf = v4l2.v4l2_buffer()
        buf.index = 0
        buf.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
        buf.memory = v4l2.V4L2_MEMORY_MMAP
        xioctl(vd, v4l2.VIDIOC_QUERYBUF, buf)
        bufmap = mmap.mmap(vd.fileno(), buf.length,
                flags=mmap.MAP_SHARED, prot=mmap.PROT_READ | mmap.PROT_WRITE,
                offset=buf.m.offset)
        # Begin capture
        buftype = c_long(buf.type)
        print('Begin capture.')
        xioctl(vd, v4l2.VIDIOC_STREAMON, addressof(buftype))
        r, w, x = select.select((vd,), (), ())
        if len(r) == 0:
            raise ValueError('No frame was grabbed.')
        start = time.time()
        count = 1
        while True:
            xioctl(vd, v4l2.VIDIOC_QBUF, buf)
            xioctl(vd, v4l2.VIDIOC_DQBUF, buf)
            bufmap.seek(0)
            db.set(IMAGE_KEY, bufmap.read(buf.bytesused), px=1000)
            db.set(IMAGETIME_KEY, float(buf.timestamp.secs) + float(buf.timestamp.usecs) * 1e-6)
            end = time.time()
            if end - start > 1.0:
                print('FPS: {}'.format(count / (end-start)))
                start = end
                count = 1
            else:
                count += 1
        xioctl(vd, v4l2.VIDIOC_STREAMOFF, addressof(buftype))
        bufmap.close()


if __name__ == '__main__':
    main()


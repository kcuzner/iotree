# Raspberry Pi Hosted Christmas Tree

This has a few considerations for using archlinuxarm on a Raspberry Pi B:

 - OpenCV appears to be broken (even through pacman)
 - v4l2 is required, so python2 is required rather than python3 (v4l2 appears to
   be broken with python3)


### Notes

 - Useful reference: https://jayrambhia.com/blog/capture-v4l2
 - V4L2 function reference:
   https://linuxtv.org/downloads/v4l-dvb-apis/uapi/v4l/user-func.html

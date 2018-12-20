# The IoTree

This is an internet controlled tree that uses my
[kl2-dev](https://github.com/kcuzner/kl2-dev) Kinetis microcontroller board to
operate a string of WS2811 LEDs in response to requests from a server.

## Overall Plan

The application will have three parts:

 - The Raspberry Pi controlling the Christmas Tree and serving up the webcam.
 - A Redis instance living in the cloud which distributes the webcam image and
   also handles funneling requests back down to the Raspberry Pi.
 - A Flask application which handles the passthrough to Redis, maybe doing
   some processing.

The main idea is that there will be a web app living in a subdirectory on my
server which users can use to interact with my christmas tree. All communication
proceeds through a Redis instance living on my cloud server. The Raspberry Pi
will be allowed to connect to the Redis instance on that server.

For the images, the Raspberry Pi will periodically publish a JPEG to a value
which is a frame of data from the camera. The data is published raw. The
Raspberry Pi application will also subscribe to a channel which has user
requests coming down from it. The requests are JSON-formatted lists of LED
patterns to display.

On the cloud side, the Flask-hosted application will serve up a simple HTML page
which displays the camera image and provides a LED editor interface. This
application connects to the Redis server and subscribes to value change
requests. When a value change is detected, the image is read from Redis and sent
to the user page using a `Content-Type: multipart/x-mixed-replace` (sorry IE).
When the user wants to publish a new LED pattern, it is published to the channel
that the Raspberry Pi is listening to.


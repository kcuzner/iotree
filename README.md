# Christmas Tree Controller

This uses my WS281x USB dongle to control a Christmas Tree through the internet,
negotiating requests from the unruly masses to make my tree many colors, while
providing visual feedback through a webcam stream.

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
will be given a key to the server and establish a connection to the cloud Redis
instance via SSH port forwarding.

For the images, the Raspberry Pi will periodically publish *something* on a
channel which is a frame of data from the camera. Whether this is straight up
binary (a JPEG) or something Base64 encoded I have not determined yet. The
Raspberry Pi application will also subscribe to a channel which has user
requests coming down from it. The exact nature of the requests I have not yet
determined beyond saying that they'll have the ability to change the color or
behavior of the LEDs on the tree.

On the cloud side, the Flask-hosted application will serve up a simple HTML page
which establishes a WebSocket connection back to the server. This connection is
then used to receive new webcam image data as it arrives (through a subscription
to the appropriate channel) and will publish LED requests from users on the
appropriate channel. Ideally it should be a simple pass-through with maybe some
sanitizing.


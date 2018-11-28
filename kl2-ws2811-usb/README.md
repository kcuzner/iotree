# WS2811 USB Dongle

This is USB dongle firmware specifically built for the christmas tree project. I
originally was going to make a nice general dongle, but both my motivation and
time ran out. Instead, I am going to use my
[kl2-dev](https://github.com/kcuzner/kl2-dev) board with this firmware. The
raspberry pi will be used to flash it, although I cannot actually compile the
program on the raspberry pi with archlinuxarm, since the package is missing and
I don't feel like waiting hours and hours to compile arm-none-eabi-gcc.

## Hardware Specifics

The kl2-dev dongle has the following hardware:

 - MKL26Z32VRM4 Kinetis KL26 microcontroller
 - A USB port (micro usb)
 - Every I/O broken out into a pin

## Feature List

 - USB Driver ported from my STM32 adventures.
 - USB Descriptor Generation ported from the midi-fader project (WIP)
 - Custom protocol (for use with libusb) (WIP)

## Building

### Environment

This project should live on the raspberry pi. The raspberry pi needs to have NFS
or some other file sharing set up to a standard x86 desktop.

### Prerequisites - Raspberry Pi

 - `make`
 - `openocd`

### Prerequisites - Desktop PC

 - `arm-none-eabi-gcc`
 - `arm-none-eabi-binutils`
 - `python3`

### Build

On the desktop PC, execute the following to build the firmware:

```
$ make
```

### Installation

On the raspberry pi, execute the following to install the firmware

```
$ make install
```

This will start an openocd server which will persist. To shut down this server,
run:

```
$ make stop
```

### Debug

After installation, an openocd server will be running. The makefile should be
configured with the hostname of the raspberry pi. The following command should
be executed on the desktop PC. Unlike my other projects, it will not
automatically start the openocd server.

```
$ make gdb
```

## Theory of Operation

This is meant to be a very simple device. It essentially provides a buffer that
will be dumped into the WS2811 chain as bytes are received. The device has no
knowledge of the topology of the LEDs and will blindly dump data into the chain.

Data is received over USB and dumped into the chain as soon as it is received.
Once a transfer ends or if there is a data underflow, the device will cease
dumping data into the buffer until the next transfer begins.

The performance goal of this project is that I can dump enough data for 50 LEDs
into the device every 16ms or so.

## Protocol

The protocol is very simple. There are no additional setup requests beyond the
standard USB ones and there are no additional descriptors.

In order to change the color of the LEDs (including turning them off), the host
PC should initiate a bulk write to Endpoint 1. The data shall have the following
format:

```
Byte 0: Red value for the first LED in the chain
Byte 1: Green value for the first LED in the chain
Byte 2: Blue value for the first LED in the chain
Byte 3: Red value for the second LED in the chain
Byte 4: Blue value for the second LED in the chain
Byte 5: Green value for the second LED in the chain
Byte 6: Red for ...
...
```

Each byte triple is for one LED, starting with the LED nearest to the
microcontroller. The number of bytes written must be a multiple of three. If the
bulk transfer has a length which is not a multiple of three, a STALL condition
results although the data up to the last byte triple will be pushed out to the
LEDs.

In the interest of keeping things simple, there is no reporting of whether or
not there is a data underflow.


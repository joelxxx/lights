#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from neopixel import *
import argparse
import sys
import socket
import fcntl, os
import errno
from time import sleep
import signal


# LED strip configuration:
LED_COUNT      = 4      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

SK6812_STRIP_RGBW =                       0x18100800
SK6812_STRIP_RBGW =                       0x18100008
SK6812_STRIP_GRBW =                       0x18081000
SK6812_STRIP_GBRW =                       0x18080010
SK6812_STRIP_BRGW =                       0x18001008
SK6812_STRIP_BGRW =                       0x18000810

scolor = SK6812_STRIP_GRBW
server = None


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print("-" * 20)
    print("Shutting down...")
    server.close()
    os.remove("/tmp/python_unix_sockets_example")
    print("Done")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def init(socket_path):
    if os.path.exists(socket_path):
        os.remove(socket_path)
    print("Opening socket...")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind(socket_path)
    fcntl.fcntl(server, fcntl.F_SETFL, os.O_NONBLOCK)
    return server

def get_data(server):
    try:
        datagram = server.recv(1024)
    except socket.error, e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            sleep(1)
            #print 'No data available'
            return 0,''
        else:
            # a "real" error occurred
            print e
            sys.exit(1)
    else:
        if not datagram:
            return -1, ''
        else:
            strback = datagram.decode('utf-8')
            #print(strback)
            if "DONE" == strback:
                return -1, ''
            return len(strback),strback


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, scolor)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    server = init('/tmp/python_unix_sockets_example')


    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            print ('Color wipe animations, SK6812_STRIP_RGBW. RED then BLUE then GREEN')
            colorWipe(strip, Color(255, 0, 0),2000)  # Red wipe
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            colorWipe(strip, Color(0, 255, 0), 2000)  # Blue wipe
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            colorWipe(strip, Color(0, 0, 255),2000)  # Green wipe
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            print ('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            print ('Rainbow animations.')
            rainbow(strip)
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            rainbowCycle(strip)
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break
            theaterChaseRainbow(strip)
            succode, strback = get_data(server)
            if (succode == 0):
                print ('no data')
            if (succode > 0):
                print("-" * 20)
                print (strback.rstrip())
            if succode < 0:
                break

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0,0,0), 10)

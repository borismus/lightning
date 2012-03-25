Prototyping with Wii Remotes in Python
======================================
categories: [physical]
posted: 2010-05-28
snip: A how-to about getting access to a wii remote using Python.



I've been working on a couple of researchy projects involving gait
recognition and running foot strike analysis. For my proof of concept, I
turned to the wiimote, everyone's favorite physical interaction
prototyping input device. Wiimotes are portable and rugged, and thus
well suited to high-intensity activities like running. They attach
easily to legs with a physio band, although the elastic tension tends to
cut off circulation. No big deal, though... it's For Science! 

This article is not about attaching Wiis to legs (more on that at a
later date!), but about communicating with the Wii remote using python.
I started out by writing a Cocoa application to harvest accelerometer
data using the WiiRemote framework provided by the [DarwiinRemote][]
project.  After some objective-c iterations of my initial gait
recognizer algorithm, I decided to port to python, an environment better
suited for light prototyping. There's a few packages explicitly
developed to integrate with the wiimote. [Pywiiuse][] provides a
lightweight wrapper around the [wiiuse][] library and does not work on
OS X. An alternative, [pywiimote][] claims to be multiplatform but
pointedly isn't. Here's the start of their code: 

    from ctypes import *
    kernel = windll.kernel32

Having found no existing wiimote-specific python libraries that would
work on my platform, I had no choice but to dig a little into the
bluetooth-based protocol that the wiimote uses. I found all the details
in all their gory glory on the [wiibrew wiki][]. The communication
protocol involves two open L2CAP sockets between the host and wiimote:
one for reading and one for writing. After an initialization string is
sent over the write socket, the wiimote springs into life and sends a
stream of data on the read socket. In this data are accelerometer values
and button presses. Here's a simple python snippet using the
[lightblue][] library:

    import sys, lightblue, hexbyte
     
    WIIMOTE_DEVICE_NAME = 'Nintendo RVL-CNT-01'
     
    # auto-discover nearby bluetooth devices
    devs = lightblue.finddevices(getnames=True, length=5)
    # find the one with the correct name
    wiimote = [d for d in devs if d[1] == WIIMOTE_DEVICE_NAME] and d[0] or None
    if not wiimote:
        print "No wiimotes found!"
        sys.exit(1)
     
    # create a socket for writing control data
    write_socket = lightblue.socket(lightblue.L2CAP)
    write_socket.connect((wiimote, 0x11))
     
    # create a socket for reading accelerometer data
    read_socket = lightblue.socket(lightblue.L2CAP)
    read_socket.connect((wiimote, 0x13))
     
    # initialize the socket to the right mode
    write_socket.send(hexbyte.HexToByte('52 12 00 33'))
     
    # start reading data from it
    while 1:
        byte = read_socket.recv(256 * 7)
        data = hexbyte.ByteToHex(byte)
        # do something interesting with the data
        print data


You'll need [hexbyte.py][] to run the above snippet. I hope
you (the wii remote wielding python fan) find this snippet useful. As a
side note, if you've figured how to pair a wiimote with an android phone
and released the code into the public domain, please let me know. Since
Android 2.2 still doesn't ship with L2CAP APIs, I hit the wall.

  [DarwiinRemote]: http://darwiin-remote.sourceforge.net/
  [Pywiiuse]: http://stackoverflow.com/questions/481943/python-with-wiimote-using-pywiiuse-module
  [wiiuse]: http://www.wiiuse.net/
  [pywiimote]: http://code.google.com/p/pywiimote/
  [wiibrew wiki]: http://wiibrew.org/wiki/Wiimote#Accelerometer
  [lightblue]: http://lightblue.sourceforge.net/
  [hexbyte.py]: https://github.com/borismus/Running-Gestures/blob/master/hexbyte.py


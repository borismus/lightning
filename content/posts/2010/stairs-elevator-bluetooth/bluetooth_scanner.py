#!/usr/bin/env python
# program runs in the background, scanning for bluetooth devices 
# at a regular interval. 

# uses the following shell utility
# hcitool inq --flush outputs:
# Inquiring...
# 60:FB:42:82:2E:7B clock offset: 0x5129    class: 0x38010c
# 60:FB:42:82:2E:7B clock offset: 0x5129    class: 0x38010c
# ...

import os, time, platform
from datetime import datetime
from urllib import urlencode
from urllib2 import urlopen, URLError

# get the name of this scanner
scanner_id = os.popen('uname -n').readline().strip()

# devices in the area
devices_here = {}

AWAY_HEURISTIC = 20


def get_bt_ids():
    """Get all nearby IDs"""
    sys = platform.system()
    ids = []
    if sys == 'Darwin':
        # we're on mac. use lightblue
        import lightblue
        # do some stuff
        devs = lightblue.finddevices(getnames=False, length=5)
        ids = [dev[0] for dev in devs]
    elif sys == 'Linux':
        # launch the scanner
        f = os.popen('hcitool inq --flush')
        # get the output from the scanner utility
        unparsed_data = f.readlines()[1:]
        for u in unparsed_data:
            # get the ID of the bluetooth devices
            id = u.split()[0]
            ids.append(id)
            
    return ids

def scan():
    """Scan the area for bluetooth devices. If a new device is seen, notify the database."""
    # note the current time
    time = datetime.now()
    # get all of the bluetooth devices nearby
    ids = get_bt_ids()
    for id in ids:
        # only record if the device is new
        if not devices_here.has_key(id):
            # if the device is not here, it must have just entered the area.
            # this is a significant event. upload it to the server.
            upload_to_db({'time': time, 'device_id': id, 
                          'scanner_id': scanner_id, 'event_type': 'ENTER'})
            
        # note the devices that are here
        devices_here[id] = time

def cleanup():
    """Clean up the list of nearby devices"""
    # keys to delete
    del_keys = []
    # get the current time
    time = datetime.now()
    # if any of the devices are stale, remove them from the list
    for device in devices_here:
        # get the last time the device was seen
        last_seen = devices_here[device]
        # if this device was last seen too long ago
        if (time - last_seen).seconds > AWAY_HEURISTIC:
            # flag it for removal to avoid
            # RuntimeError: dictionary changed size during iteration
            del_keys.append(device)
            # and notify the server that the device left
            upload_to_db({'time': time, 'device_id': device, 
                          'scanner_id': scanner_id, 'event_type': 'EXIT'})

    # remove flagged ids from the list of devices
    for k in del_keys:
        del devices_here[k]

def upload_to_db(params):
    """Upload data about an event to the server"""
    print '%s: device %s at time %s' % (params['event_type'], params['device_id'], params['time'])
    # massage the params to be right
    params['time'] = params['time'].strftime('%Y-%m-%d %H:%M:%S')
    # encode some parameters
    data = urlencode(params.items())
    try: 
        # post data to http://dev.hci.uma.pt/~boris/visits.php
        # going by IP is faster than doing a DNS lookup
        urlopen('http://dev.hci.uma.pt/~boris/visits.php', data)
    except URLError:
        print "...failed to upload data for event"
    
if __name__ == '__main__':
    while True:
        print 'Scanning...'
        # continuously scan the world for new devices 
        scan()
        # and clean up the list of devices that are present
        cleanup()
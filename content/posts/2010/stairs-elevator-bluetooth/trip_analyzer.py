#!/usr/bin/env python
# script to comb the database of entries and exits and create data of 
# trips from one destination to another on one of two pathes.

# mysql command line: echo "select * from visits" | mysql boris -pyeltsin89 -sr

import os

def analyze_database():
    analysis = []
    # get all of the trips via the two pathes
    for path in paths.keys():
        pathSQL = paths[path]
        f = os.popen('echo \'%s\' | mysql boris -pyeltsin89 -sr' % pathSQL)
        for tripData in f.readlines():
            tripData = tripData.split()
            data = {
                'datetime': '%s %s' %(tripData[2], tripData[3]),
                'device': tripData[0],
                'source': tripData[1],
                'destination': tripData[5],
                'duration': tripData[-1],
                'path': path
            }
            analysis.append(data)
        
    return analysis
        
SPREADSHEET_KEY = 'tHLe_qt8_iq7-oZHAd2BsSQ'
WORKSHEET_ID = 'od6'
EMAIL = 'miraage@gmail.com'
PASSWORD = 'fire04'

def upload_to_gdocs(analyzed):
    import gdata.spreadsheet
    import gdata.spreadsheet.service
    
    # authenticate with the gdoc
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.email = EMAIL
    client.password = PASSWORD
    client.ProgrammaticLogin()
    
    # create a row for each analyzed requester
    for data in analyzed:
        print data
        entry = client.InsertRow(data, SPREADSHEET_KEY, WORKSHEET_ID)


paths = {
    '1': """select source_device_id, source_scanner_id, source_time, source_event_type, destination_scanner_id, destination_device_id, destination_time, destination_event_type, trip_length from
(
select source.scanner_id as source_scanner_id, source.device_id as source_device_id, source.time as source_time, source.event_type as source_event_type,
      destination.scanner_id as destination_scanner_id, destination.device_id as destination_device_id, destination.time as destination_time, destination.event_type as destination_event_type,
      timediff(destination.time, source.time) as trip_length
from
(select * from visits where scanner_id = "floor0" and event_type = "exit") as source,
(select * from visits where scanner_id = "floor2" and event_type = "entry") as destination
where source.device_id = destination.device_id and source.time < destination.time
) as trips, visits
where trips.source_device_id = visits.device_id and trips.source_time < visits.time and trips.destination_time > visits.time and visits.scanner_id="floor1" and visits.event_type = "exit"
""",
    '2': """select source_device_id, source_scanner_id, source_time, source_event_type, destination_scanner_id, destination_device_id, destination_time, destination_event_type, trip_length from
(select source.device_id as source_device_id, source.scanner_id as source_scanner_id,  source.time as source_time, source.event_type as source_event_type,
      destination.scanner_id as destination_scanner_id, destination.device_id as destination_device_id, destination.time as destination_time, destination.event_type as destination_event_type,
      timediff(destination.time, source.time) as trip_length
from
(select * from visits where scanner_id = "floor0" and event_type = "exit") as source,
(select * from visits where scanner_id = "floor2" and event_type = "entry") as destination
where source.device_id = destination.device_id and source.time < destination.time
) as t1
where (source_device_id, source_scanner_id, source_time, source_event_type, destination_scanner_id, destination_device_id, destination_time, destination_event_type, trip_length) NOT IN
(
select source_device_id, source_scanner_id, source_time, source_event_type, destination_scanner_id, destination_device_id, destination_time, destination_event_type, trip_length from (
select trips.source_device_id, trips.source_scanner_id, trips.source_time, trips.destination_scanner_id, trips.destination_time, trips.trip_length from
(
select source.scanner_id as source_scanner_id, source.device_id as source_device_id, source.time as source_time, source.event_type as source_event_type,
      destination.scanner_id as destination_scanner_id, destination.device_id as destination_device_id, destination.time as destination_time, destination.event_type as destination_event_type,
      timediff(destination.time, source.time) as trip_length
from
(select * from visits where scanner_id = "floor0" and event_type = "exit") as source,
(select * from visits where scanner_id = "floor2" and event_type = "entry") as destination
where source.device_id = destination.device_id and source.time < destination.time
) as trips, visits
where trips.source_device_id = visits.device_id and trips.source_time < visits.time and trips.destination_time > visits.time and visits.scanner_id="floor1" and visits.event_type = "exit"
) as t2)"""
}

if __name__ == '__main__':
    analysis = analyze_database()
    upload_to_gdocs(analysis)
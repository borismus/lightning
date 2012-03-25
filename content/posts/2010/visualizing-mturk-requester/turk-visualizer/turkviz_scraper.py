#!/usr/bin/env python
# scrape all of turk, get some interesting analysis results
# then, throw the results into a google spreadsheet

from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen

import sys
import time, datetime
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

SEARCH_URL = "https://www.mturk.com/mturk/viewhits?searchWords=&selectedSearchType=hitgroups&sortType=LastUpdatedTime:1&searchSpec=HITGroupSearch%23T%231%2310%23-1%23T%23!%23!LastUpdatedTime!1!%23!&pageNumber="
HIT_URL = "https://www.mturk.com/mturk/preview?groupId="

def scrape_turk():
    # indexed by groupID
    data = {}
    # the current page number in the search results
    pageNumber = 1
    # compute one timestamp for the whole scraping session
    now = datetime.datetime.now()
    
    # for each page of HITs on mechanical turk,
    while True:
        logging.info('scraping page ' + `pageNumber`)
        # download the page contents
        url = SEARCH_URL + `pageNumber`
        try:
            soup = BeautifulSoup(urlopen(url))
        except:
            logging.info("failed to load page " + `pageNumber`)
        # get a list of tasks stored in body/div/table[3] in the markup
        hitTable = soup.body.find('div', recursive=False).findAll('table', recursive=False)[2]
        # now hitTable is an HTML table with each row corresponding to a HIT
        hits = hitTable.findAll('tr', recursive=False)
    
        # if there are no tasks on this page, we're done
        if len(hits) == 0:
            break
        
        # otherwise, go through the tasks
        for hit in hits:
            # extract the interesting parts of each task:
        
            # unique identifier (groupID)
            groupID = None
            viewText = hit.find(text="View a HIT in this group")
            if hasattr(viewText, 'parent'):
                # if the "View a HIT in this group"" is a hyperlink,
                groupID = viewText.parent['href'].split('&')[0].split('=')[1]
            else:
                # TODO: fix this
                # don't extract groupID for tasks that we don't qualify for.
                continue
            
            # the following fields all have the same CSS class
            fields = hit.findAll('td', {'class':'capsule_field_text'})
            # hits available
            hitsAvailable = fields[4].string
            # name -- found through capsulelink CSS class
            name = hit.find('a', {'class': 'capsulelink'}).string.strip()
            # requester
            requester = fields[0].a.string
            # expiration date
            expirationDate = fields[1].string.strip()
            # time alotted
            timeAlotted = fields[2].string.strip()
            # reward
            reward = fields[3].string
            # description of the task
            description = fields[5].string
            # keywords
            keywords = " ".join([kw.string for kw in fields[6].findAll('a', recursive=False)])
            # qualification requirement
            qualifications = None
            
            hitInfo = {
                'groupID': groupID, 'name': name, 'requester': requester, 'expirationDate': expirationDate,
                'timeAlotted': timeAlotted, 'reward': reward, 'description': description, 'keywords': keywords,
                'hitsAvailable': hitsAvailable, 'timestamp': now
            }
    
            # append this to the list
            data[groupID] = hitInfo
        
            logging.info("scraped data for " + groupID)
        
        pageNumber += 1
    return data
    
class RequesterProfile(object):
    def __init__(self, hitInfo):
        """
        create requester information out of a single hit
        """
        self.requester = hitInfo['requester']
        self.hitsAvailable = int(hitInfo['hitsAvailable'])
        self.timeAlotted = self.parseTime(hitInfo['timeAlotted'])
        self.keywords = self.parseKeywords(hitInfo['keywords'])
        self.reward = self.parseReward(hitInfo['reward'])
        self.samples = 1
        
    def add(self, hitInfo):
        """
        add another hit into this one
        """
        assert hitInfo['requester'] == self.requester
        
        self.hitsAvailable += int(hitInfo['hitsAvailable'])
        self.timeAlotted = self.adjustAverage(self.timeAlotted, self.parseTime(hitInfo['timeAlotted']))
        self.reward = self.adjustAverage(self.reward, self.parseReward(hitInfo['reward']))
        
        self.addKeywords(self.parseKeywords(hitInfo['keywords']))
        
        self.samples += 1
        
    def addKeywords(self, keywords):
        for k in keywords.keys():
            if self.keywords.has_key(k):
                self.keywords[k] += 1
            else:
                self.keywords[k] = 1
        
    def adjustAverage(self, average, newValue):
        return (average * self.samples + newValue) / (self.samples + 1)
    
    def parseReward(self, s):
        """
        Converts strings like "$2.56" into number of cents
        """
        return int(float(s[1:]) * 100)

    def parseKeywords(self, s):
        """
        Converts strings like "reddit digg foo bar" into one with 
        frequency counts.
        """
        split = s.split(' ')
        return dict(zip(split, [1]*len(split)))

    def parseTime(self, s):
        """
        Converts phrases like "1 day 3 hours" into number of minutes
        """
        out = 0
        split = s.split(' ')
        for i in range(0, len(split), 2):
            val = int(split[i])
            unit = split[i+1]
            if unit.startswith('week'):
                out += val * 10080
            elif unit.startswith('day'):
                out += val * 1440
            elif unit.startswith('hour'):
                out += val * 60
            elif unit.startswith('minute'):
                out += val
            elif unit.startswith('second'):
                pass
            else:
                # print "ERROR: unknown time unit encountered: " + unit
                pass
        return out
    
    def topKeywords(self):
        MAX_KEYWORDS = 1
        l = self.keywords.items()
        l.sort(lambda a, b: a[1] < b[1] and 1 or -1)
        return " ".join(dict(l[:MAX_KEYWORDS]).keys())
        
    def __str__(self):
        return str(self.dict())
    
    def dict(self):
        return {
            'requester': self.requester, 
            'hits': unicode(self.hitsAvailable),
            'time': unicode(self.timeAlotted),
            'keywords': self.topKeywords(),
            'reward': unicode(self.reward),
        }
        
    def isValid(self):
        return self.reward != 0

def analyze_data(data):
    results = {}
    # for each active requester, parse out the following:
    # - requester name
    # - average duration of HITs
    # - average payment per HIT
    # - total number of HITs
    # - top 3 keywords
    for groupID in data:
        d = data[groupID]
        reqName = d['requester']
        if results.has_key(reqName):
            # if this requester has already been encountered, add more data
            requester = results[reqName]
            requester.add(d)
        else:
            # if this requester hasn't been seen yet, create data
            results[reqName] = RequesterProfile(d)
    
    
    # get the top N requesters by number of HITs
    MAX_REQUESTERS = 50
    l = results.items()
    l.sort(lambda a, b: a[1].hitsAvailable < b[1].hitsAvailable and 1 or -1)
    results = dict(l[:MAX_REQUESTERS])
    return results


SPREADSHEET_KEY = '0Ah0QcIUeNxmPdDZGdVlJZzVTeWotM05IN1RSZjA3R1E'
WORKSHEET_ID = 'od6'
EMAIL = 'miraage@gmail.com'
PASSWORD = 'fire04'

def gdoc_publish(analysis):
    import gdata.spreadsheet
    import gdata.spreadsheet.service
    
    pubtime = unicode(minutes_since_2010())
    
    # authenticate with the gdoc
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.email = EMAIL
    client.password = PASSWORD
    client.ProgrammaticLogin()
    
    # create a row for each analyzed requester
    for req in analysis:
        r = analysis[req]
        if not r.isValid():
            continue
        d = r.dict()
        # make sure it's timestamped
        d['datetime'] = pubtime
        # create a row in the spreadsheet
        entry = client.InsertRow(d, SPREADSHEET_KEY, WORKSHEET_ID)
        logging.info('added row to spreadsheet: ' + req)
        
def minutes_since_2010():
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime.now()
    delta = end - start
    return delta.days * 1440 + delta.seconds/60

if __name__ == '__main__':
    logging.info('launching')
    raw = scrape_turk()
    logging.info('scraped turk')
    analysis = analyze_data(raw)
    logging.info('analyzed data')
    gdoc_publish(analysis)
    logging.info('published to google docs')

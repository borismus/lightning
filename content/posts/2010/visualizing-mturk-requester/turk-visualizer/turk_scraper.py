#!/usr/bin/env python
# This script grabs a snapshot of the mechanical turk system as of right now
# The snapshot is timestamped and stored in a database. 
# 
# Known limitations: 
# -- if a HIT requires qualifications, the groupID is not placed in the HTML but generated via JavaScript.
#    as a result, such HITs don't get placed in the database.
# -- in some cases, the HTML body of the HIT cannot be parsed. 

from BeautifulSoup import BeautifulSoup, Comment
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlparse

import sqlite3
import sys
import datetime
import logging
logging.basicConfig(level=logging.DEBUG)

SEARCH_URL = "https://www.mturk.com/mturk/viewhits?searchWords=&selectedSearchType=hitgroups&sortType=LastUpdatedTime:1&searchSpec=HITGroupSearch%23T%231%2310%23-1%23T%23!%23!LastUpdatedTime!1!%23!&pageNumber="
HIT_URL = "https://www.mturk.com/mturk/preview?groupId="
DB_PATH = 'turkdb'

def scrape_turk():
    # compute one timestamp for the whole scraping session
    now = datetime.datetime.now()
    # are we done scraping yet?
    isScrapingFinished = False
    # the current page number in the search results
    pageNumber = 1
    
    # for each page of HITs on mechanical turk,
    while True:
        # download the page contents
        url = SEARCH_URL + `pageNumber`
        soup = BeautifulSoup(urlopen(url))
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
            
            # check for an existing entry with the same groupID. 
            # if it exists, only add the data that can possibly change: hits available
            cur = c.execute('select * from hits where groupID==?', (groupID,))
            if cur.fetchone():
                # this groupID already exists in the database.
                # only create a row with an updated number of hitsAvailable
                
                hitInfo = {'groupID': groupID, 'hitsAvailable': hitsAvailable}
                c.execute("""insert into hits values(?, NULL, NULL, NULL, NULL, NULL, ?, NULL, NULL, NULL, NULL, ?)""", 
                    (groupID, hitsAvailable, now))
                c.commit()
                
                logging.info("updated hitsAvailable for " + groupID)
                
            else:
                # this groupID doesn't exist yet
                # so also fetch the body from mturk and put the entirety of the HIT in the database
            
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
                # scrape the body
                body = fetch_HIT_body(groupID)
        
                # add these bits to an sqlite database
                c.execute("""insert into hits values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                    (groupID, name, requester, expirationDate, timeAlotted, reward, hitsAvailable, 
                    description, keywords, qualifications, body, now))
                c.commit()
            
                logging.info("scraped data for " + groupID)
        
        pageNumber += 1

def fetch_HIT_body(groupID):
    # get the HTML for the body of the HIT
    url = HIT_URL + groupID
    logging.debug("fetching HIT body " + url)
    soup = BeautifulSoup(urlopen(url))
    # it might be regular HTML body or an embedded iframe 
    output = soup.find('div', {'id': 'hit-wrapper'})
    if not output:
        # find the iframe URL from the HTML document
        iframe = soup.find('iframe')
        if not iframe:
            logging.error('HIT body neither inline nor in iframe')
            return
        
        # and get the contents of the referenced page
        output = "\n".join(urlopen(iframe['src']).readlines())
    
    try:
        return unicode(output)
    except:
        logging.error("could not parse HIT body")
        return None
    
if __name__ == '__main__':
    # create a sqlite3 database and table if it doesn't yet exist
    try: 
        open(DB_PATH)
        c = sqlite3.connect(DB_PATH)
    except:
        c = sqlite3.connect(DB_PATH)
        logging.info("creating new database")
        c.execute('''create table hits
        (groupID text, name text, requester text, expiration date,
        time string, reward real, hitsAvailable real, description text,
        keywords text, qualifications text, ts timestamp, body text)''')
        c.commit()
    
    # scrape mechanical turk
    scrape_turk()

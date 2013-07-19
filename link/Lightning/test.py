from oauth2client.client import OAuth2WebServerFlow

from urllib import urlencode
import httplib2
import webbrowser
import json

import logging
logging.basicConfig()

client_id = '930206334662.apps.googleusercontent.com'
client_secret = 'r2aq6CJDRAA3Dd5ODlUwHibk'
scope = 'https://www.googleapis.com/auth/plus.stream.write ' + \
        'https://www.googleapis.com/auth/plus.me'
flow = OAuth2WebServerFlow(client_id=client_id,
                           client_secret=client_secret,
                           scope=scope,
                           redirect_uri='urn:ietf:wg:oauth:2.0:oob')

auth_uri = flow.step1_get_authorize_url()
webbrowser.open(auth_uri)

code = raw_input("Code: ")
credentials = flow.step2_exchange(code)

print 'Got credentials: ' + str(credentials.access_token)

# Create a new authorized API client.
http = httplib2.Http()
http = credentials.authorize(http)


# POST https://www.googleapis.com/plus/v1whitelisted/people/{userId}/activities
headers = {'Content-Type': 'application/json'}
print 'Request headers: ' + str(headers)

content_text = 'hello world'
content_url = 'http://onstartups.com/tabid/3339/bid/33111/7-Reasons-Why-You-Need-To-Work-For-A-Big-Company.aspx'

url = 'https://www.googleapis.com/plus/v1whitelisted/people/me/activities'
attachments = [dict(url=content_url)]
object = dict(originalContent=content_text, attachments=attachments)
access = dict(items=dict(type='public'))
data = dict(object=object, access=access)
body = json.dumps(data)

print 'Created request body: ' + body
resp, content = http.request(url,
        method='POST',
        headers=headers,
        body=body)

print content

from os.path import expanduser
import os
import pickle
import webbrowser
import string

# TODO: Separate TwitterSyndicator and GPlusSyndicator into own files.
# For twitter
import tweepy

# For G+
from oauth2client.client import OAuth2WebServerFlow
from urllib import urlencode
import httplib2
import json
import logging
logging.basicConfig()

class Syndicator:
    """
    Publishes a link to a service (eg. Twitter, G+).
    """
    # TODO: Set the service name.
    service_name = None
    prefs_path = '~/.lightning'

    def __init__(self):
        self.load_prefs()

    def load_prefs(self):
        """
        Loads the access token from a preference file.
        """
        path = expanduser(self.prefs_path)
        if os.path.exists(path):
            prefs_file = open(path, 'r')
            self.prefs = pickle.load(prefs_file)
            if not self.service_name in self.prefs:
                self.prefs[self.service_name] = {}
        else:
            self.prefs = {}
            self.prefs[self.service_name] = {}

    def save_prefs(self):
        """
        Sets the access token and saves it to the pickle.
        """
        prefs_file = open(expanduser(self.prefs_path), 'w')
        pickle.dump(self.prefs, prefs_file)

    def get(self, key):
        service = self.prefs[self.service_name]
        if key in service:
            return service[key]
        return None

    def set(self, key, value):
        self.prefs[self.service_name][key] = value
        self.save_prefs()

    def clear_all(self):
        # Clears all stored prefs.
        self.prefs[self.service_name] = {}
        self.save_prefs()


    def set_info(self, link_url, blog_url, title, body):
        """
        Publishes the link to the service.
        """
        self.title = title
        self.body = body
        self.blog_url = blog_url
        self.link_url = link_url


    def is_authenticated(self):
        # TODO: Implementation-specific.
        return False

    def publish(self):
        # TODO: Provide implementations in each syndicator.
        pass

    def markdown_to_plaintext(self, markdown_string):
        """
        Utility function to convert markdown to plaintext.
        """
        from BeautifulSoup import BeautifulSoup
        from markdown import markdown

        html = markdown(markdown_string)
        return ''.join(BeautifulSoup(html).findAll(text=True))

class TwitterSyndicator(Syndicator):
    """
    Shortens the text and URL to fit within 140 characters and publishes to
    Twitter.
    """
    service_name = 'Twitter'
    consumer_token = 'VNypXiSafjLkvMgk7eXLGQ'
    consumer_secret = 'UruEouAfvaVwmlcW32bzJ4mcuqmgfW4N3Ze3daouCI'
    auth = tweepy.OAuthHandler(consumer_token, consumer_secret)

    def publish(self):
        # If the title is too long, truncate it, leaving room for a URL.
        status = self.truncate_words(self.title, 110) + ' ' + self.blog_url

        api = tweepy.API(self.auth)
        api.update_status(status)
        print "Published to Twitter."

    def truncate_words(self, text, char_limit):
        words = text.split(' ')
        buf = ''
        count = 0
        for word in words:
            count += len(word) + 1
            if count > char_limit:
                return buf.strip(string.punctuation + ' ') + '...'
            buf += word + ' '
        return buf.strip()

    def is_authenticated(self):
        key = self.get('key')
        secret = self.get('secret')
        return bool(key and secret)

    def login(self):
        # First, try getting the access token.
        if not self.is_authenticated():
            # If there's no token, start verification.
            self.verify()
            # At this point, wait for a callback to confirm_verifier with the
            # verification code.
        self.finish_login()

    def finish_login(self):
        key = self.get('key')
        secret = self.get('secret')
        self.auth.set_access_token(key, secret)

    def verify(self):
        try:
            redirect_url = self.auth.get_authorization_url()
            webbrowser.open(redirect_url)
        except tweepy.TweepError:
            print 'Error! Failed to get request token.'

    def confirm_verifier(self, verifier):
        try:
            self.auth.get_access_token(verifier)
        except tweepy.TweepError:
            print 'Error! Failed to get access token.'

        self.set('key', self.auth.access_token.key)
        self.set('secret', self.auth.access_token.secret)
        self.finish_login()



class GPlusSyndicator(Syndicator):
    """
    Publishes to Google Plus.
    """
    service_name = 'G+'
    client_id = '930206334662.apps.googleusercontent.com'
    client_secret = 'r2aq6CJDRAA3Dd5ODlUwHibk'
    scope = 'https://www.googleapis.com/auth/plus.stream.write ' + \
            'https://www.googleapis.com/auth/plus.me'
    flow = OAuth2WebServerFlow(client_id=client_id,
                               client_secret=client_secret,
                               scope=scope,
                               redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    post_url = 'https://www.googleapis.com/plus/v1whitelisted/people/me/activities'

    def publish(self):
        credentials = self.get('credentials')
        # Create a new authorized API client.
        http = httplib2.Http()
        http = credentials.authorize(http)

        headers = {'Content-Type': 'application/json'}

        # TODO(smus): Actually we want to format as much as possible. Perhaps a
        # custom Markdown to G+ formatter would fit the bill here.  For
        # example, converting quotes (> foo) to "foo", and more obvious
        # formatting.
        plainbody = self.markdown_to_plaintext(self.body)
        attachments = [dict(url=self.link_url)]
        object = dict(originalContent=plainbody, attachments=attachments)
        access = dict(items=[dict(type='public')])
        data = dict(object=object, access=access)
        body = json.dumps(data)

        resp, content = http.request(self.post_url,
                method='POST',
                headers=headers,
                body=body)

        print "Published to G+."

    def is_authenticated(self):
        credentials = self.get('credentials')
        return bool(credentials)

    def login(self):
        # First, try getting the access token.
        if not self.is_authenticated():
            # If there's no token, start verification.
            self.verify()
            # At this point, wait for a callback to confirm_verifier with the
            # verification code.
        self.finish_login()

    def finish_login(self):
        credentials = self.get('credentials')

    def verify(self):
        auth_uri = self.flow.step1_get_authorize_url()
        webbrowser.open(auth_uri)


    def confirm_verifier(self, verifier):
        credentials = self.flow.step2_exchange(verifier)
        self.set('credentials', credentials)
        self.finish_login()


if __name__ == '__main__':
    """
    # Make a G+ syndicator.
    synd = GPlusSyndicator()
    synd.clear_all()
    synd.login()
    code = raw_input("Code: ")
    synd.confirm_verifier(code)
    print 'authenticated: ' + str(synd.is_authenticated())
    synd.set_info(
            link_url='http://pythonhosted.org/tweepy/html/auth_tutorial.html',
            blog_url='http://smus.com/link/foo',
            title='Authenticating',
            body='Testing 1.')
    synd.publish()
    """

    B = '''Read Scott Jenson's webapp UX paper. First part goes into a native app replacement, along the lines of [my previous blog post](http://smus.com/installable-webapps/). 

Next, a plea for an open web integrated wireless discovery service, ideally supporting multiple protocols including Bluetooth Low Energy. Fundamentally,

> This ability to 'summon' a web page without typing anything at all needs to be explored in future W3C standards and not be left solely to handset makers. 

Lastly, with some cross-device link in place, we can enter a world of multi-device interactions, which is, in my opinion, the key UX area to streamline in the near future.
'''

    synd = GPlusSyndicator()
    synd.login()
    synd.set_info(
            link_url='https://docs.google.com/document/d/1wcXubh-yUtViwtUG4o43v3jeO6P1T63EWTh4iw2iHy8/edit',
            blog_url='http://smus.com/link/2013/web-apps-position-paper/',
            title='Web Apps Position paper',
            body=B)
    synd.publish()

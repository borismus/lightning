#-*- coding: utf-8 -*-
#
#  LinkTextProcessor.py
#  Lightning
#
#  Created by Boris Smus on 7/13/13.
#  Copyright (c) 2013 Boris Smus. All rights reserved.
#

from __future__ import print_function
from Syndicator import *

import re
import os
import datetime
import codecs
import subprocess

import unidecode

class LinkTextProcessor:
    """
    Given the text of a link entry, does the following:

    Previewing:
    - Extracts URL from the text.
    - Creates a link entry in the lightning directory structure.
    - Previews how this looks locally.

    Publishing:
    - Publishes the lightning blog to S3.
    - Gets the published URL.
    - For each sharing service, decides what to share.

    Cleaning up:
    - Removes the newly added link.

    Naming:
    - Generates a unique slug for the link.
    - Based on that slug, gets the URL to the content.
    - If the slug changes, renames directory.
    """

    PREVIEW_URL = 'http://localhost/'
    BLOG_URL = 'http://smus.com/link/'
    BLOG_ROOT = '/Users/smus/Projects/smus.com/'
    LINK_ROOT = os.path.join(BLOG_ROOT, 'content/links')

    def __init__(self, syndicators=[]):
        self.is_first_run = True
        # The syndication services which to publish to.
        self.syndicators = syndicators


    def set_content(self, url, title, body):
        """
        Called when the preview changes.
        """
        # First clean any existing links.
        if self.is_first_run:
            self.is_first_run = False
        else:
            self.clean()

        self.url = url
        self.title = title
        self.body = body
        print('set_content %s %s %s' % (url, title, body))
        # Get a simple slug out of the title.
        self.slug = self.generate_slug(self.title)
        # Create a link file.
        return self.create_link_file(self.slug, self.url, self.title, self.body)


    def preview(self):
        """
        Preview the link to see how it would look locally.
        """
        # Rebuild the blog locally.
        self.build_blog()
        # Open a browser to see the local preview.
        from Foundation import NSBundle
        bundle = NSBundle.mainBundle()
        script_path = bundle.pathForResource_ofType_('open-chrome-tab', 'scpt')
        self.run_command('osascript %s %s' % (script_path, self.PREVIEW_URL))


    def publish(self):
        """
        Called when the publish button is clicked.
        """
        # Rebuild the blog locally.
        self.build_blog()
        # Get the URL of the published link.
        blog_url = self.get_published_url(self.slug)
        # Publish the blog to S3.
        self.publish_blog()
        print('Published new link to: ' + blog_url)
        for syn in self.syndicators:
            syn.set_info(self.url, blog_url, self.title, self.body)
            syn.publish()


    def clean(self):
        """
        Called to clean up the link entry.
        """
        if not hasattr(self, 'slug'):
            return
        # Remove the link directory and rebuild the blog.
        link_path = self.get_link_path(self.slug)
        if os.path.exists(link_path):
            os.remove(link_path)
            self.build_blog()

    #####
    ##### Private methods
    #####

    def generate_slug(self, title):
        """
        Called to generate a short unique slug from the link text.
        """
        slug = unidecode.unidecode(title).lower()
        return re.sub(r'\W+','-', slug)


    def get_link_path(self, slug):
        return os.path.join(self.LINK_ROOT, slug + '.txt')


    def create_link_file(self, slug, url, title, body):
        """
        Creates a link index file in the link directory. Format:

        Title of Link
        =============
        posted: 2013-07-14

        Body of link goes here (markdown).
        """
        path = self.get_link_path(slug)
        print('Got link path: ' + path)
        # Ensure that the path is unique.
        if os.path.exists(path):
            raise Exception('Link already exists at specified path: %s.' % path)
            return False

        # Create a file and start writing things to it.
        #f = open(path, 'w')
        f = codecs.open(path, 'w', encoding='utf-8')
        # First write the title.
        print(title, file=f)
        # Next a separator.
        print('=' * len(title), file=f)
        # Post the date in YAML.
        now = datetime.datetime.now()
        print('posted: %s' % now.strftime('%Y-%m-%d'), file=f)
        # Add a link.
        print('link: %s' % url, file=f)
        # Lastly, write the body of the link.
        print('\n' + body, file=f)
        print('Printed to file')
        f.close()
        return True


    def build_blog(self):
        self.run_command('cd %s && ./lightning/lightning build' % self.BLOG_ROOT)


    def publish_blog(self):
        self.run_command('cd %s && ./lightning/lightning deploy' % self.BLOG_ROOT)


    def get_published_url(self, slug):
        # TODO(smus): Make this actually respect the blog configuration.
        path = os.path.join(str(datetime.datetime.now().year), slug)
        return os.path.join(self.BLOG_URL, path)

    def run_command(self, cmd):
        process = subprocess.Popen(cmd, shell=True, env={},
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        # Wait for the process to terminate.
        out, err = process.communicate()
        errcode = process.returncode
        # Debug only: output results of the command.
        from Foundation import NSLog
        NSLog("Ran command: %s. Output: %s." % (cmd, out))
 


if __name__ == '__main__':
    test_url = 'http://procrastineering.blogspot.com/2012/04/projects-at-google-x.html'
    test_title = 'Projects at Google X'
    test_title2 = 'Cool Projects at X'
    test_body = '''> These past couple weeks, there have been a few videos released from
> the group I work in at Google. Congratulations to the many people in X
> who's hard work has gone into each of these.

Google X released a few concept videos of projects in their pipeline.
Very exciting stuff to see this great work slowly trickle out to the
public.'''
    # Run some tests.
    ltp = LinkTextProcessor()
    ltp.set_content(test_url, test_title, test_body)
    ltp.preview()
    ltp.set_content(test_url, test_title2, test_body)
    ltp.preview()
    ltp.clean()

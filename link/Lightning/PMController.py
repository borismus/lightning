#-*- coding: utf-8 -*-
#
#  MyWindowController.py
#  Lightning
#
#  Created by Boris Smus on 7/12/13.
#  Copyright (c) 2013 Boris Smus. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from AppKit import *

from LinkTextProcessor import *

class PMController(NSWindowController):

    titleField = IBOutlet()
    urlField = IBOutlet()
    bodyField = IBOutlet()
    charCountLabel = IBOutlet()
    actionButton = IBOutlet()

    ltp = LinkTextProcessor()

    def awakeFromNib(self):
        NSLog("Awake from nib.")
        self.setPreviewMode(True)
        self.bodyField.setDelegate_(self)
        self.urlField.setDelegate_(self)
        self.titleField.setDelegate_(self)

        # Style the bodyField.
        self.bodyField.setFont_(NSFont.fontWithName_size_("Monaco", 13))
        self.bodyField.setRichText_(NO)
        self.bodyField.setUsesFontPanel_(NO)

    @IBAction
    def post_(self, sender):
        url = unicode(self.urlField.stringValue())
        title = unicode(self.titleField.stringValue())
        body = unicode(self.bodyField.string())
        NSLog(u"Post: %s" % body)
        # TODO(smus): Validate all fields.

        if self.isPreview:
            # Relinquish control to the link text processor for a preview.
            self.ltp.set_content(url, title, body)
            # Show the preview in a browser window.
            self.ltp.preview()
            # Go into publish mode.
            self.setPreviewMode(False)
        else:
            # If in publish mode, push to S3, publish to twitter & G+.
            self.ltp.publish()

    @IBAction
    def cancel_(self, sender):
        NSLog(u"Cancel")
        # Remove the link if one was created.
        self.ltp.clean()
        # Exit the application.
        self.quit()

    def setPreviewMode(self, isPreview):
        self.isPreview = isPreview
        # Update the UI.
        self.actionButton.setTitle_(isPreview and "Preview" or "Publish")

    def controlTextDidChange_(self, notification):
        # If any of the text changes, go into preview mode.
        self.setPreviewMode(True)
        self.enableButtonIfValid()

        changedField = notification.object()
        if changedField == self.urlField:
            # If the URL field, try to infer the title.
            url = self.urlField.stringValue()
            title = self.inferTitleFromURL(url)
            if title:
                NSLog("Setting title to be: " + title)
                self.titleField.setStringValue_(title)

    def textDidChange_(self, notification):
        # Go back to preview mode.
        self.setPreviewMode(True)
        self.enableButtonIfValid()
        # If the body text changes, update the count.
        text = self.bodyField.string()
        self.charCountLabel.setStringValue_(len(text))
        NSLog(u"Length: %d" % len(text))


    def inferTitleFromURL(self, url):
        from mechanize import Browser
        from urlparse import urlparse
        try:
            result = urlparse(url)
            if result.scheme not in ['http', 'https']:
                return None
            br = Browser()
            br.open(url)
            return br.title()
        except Exception as e:
            NSLog("Exception: " + str(e))
            return None

    def quit(self):
        NSApp.performSelector_withObject_afterDelay_("terminate:", None, 0);

    def enableButtonIfValid(self):
        # If all of the text fields have content in them, enable the button.
        # Otherwise, disable it.
        url = unicode(self.urlField.stringValue())
        title = unicode(self.titleField.stringValue())
        body = unicode(self.bodyField.string())
        isEnabled = url and title and body

        self.actionButton.setEnabled_(isEnabled and YES or NO)


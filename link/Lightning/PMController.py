#-*- coding: utf-8 -*-
#
#  MyWindowController.py
#  Lightning
#
#  Created by Boris Smus on 7/12/13.
#  Copyright (c) 2013 Boris Smus. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
#from Foundation import *
from Foundation import NSLog
#from AppKit import *
from AppKit import NSWindowController, NSFont, NSOnState, NSApp, NSNotificationCenter, NSApplicationWillTerminateNotification

from LinkTextProcessor import *
from Syndicator import *

class PMController(NSWindowController):

    titleField = IBOutlet()
    urlField = IBOutlet()
    bodyField = IBOutlet()
    charCountLabel = IBOutlet()
    actionButton = IBOutlet()
    twitterCheckbox = IBOutlet()
    gplusCheckbox = IBOutlet()
    confirmTokenSheet = IBOutlet()
    confirmTokenField = IBOutlet()

    twitter = TwitterSyndicator()
    gplus = GPlusSyndicator()
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
    
        # Authenticate to twitter if we can.
        if self.twitter.is_authenticated():
            self.twitter.login()
            self.twitterCheckbox.setState_(NSOnState)
            self.ltp.syndicators.append(self.twitter)
        
        # Authenticate to G+ if we can.
        if self.gplus.is_authenticated():
            self.gplus.login()
            self.gplusCheckbox.setState_(NSOnState)
            self.ltp.syndicators.append(self.gplus)

        # Listen to the NSApplicationWillTerminateNotification.
        center = NSNotificationCenter.defaultCenter()
        center.addObserver_selector_name_object_(self, "applicationWillTerminateNotification:", NSApplicationWillTerminateNotification, None)

        self.didPublish = False

    def applicationWillTerminateNotification_(self, notification):
        # Cleanup if the app did not publish.
        if not self.didPublish:
            self.ltp.clean()
        NSLog("applicationWillTerminateNotification_")


    @IBAction
    def post_(self, sender):
        url = self.urlField.stringValue()
        title = self.titleField.stringValue()
        body = self.bodyField.string()
        NSLog(u"Title: %s" % title)
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
            print 'Syndicators: ' + str(self.ltp.syndicators)
            self.ltp.publish()
            self.didPublish = True
            self.quit()

    @IBAction
    def cancel_(self, sender):
        NSLog(u"Cancel")
        # Remove the link if one was created.
        self.ltp.clean()
        # Exit the application.
        self.quit()
    
    @IBAction
    def twitterChecked_(self, sender):
        if self.twitterCheckbox.state() == NSOnState:
            self.twitter.login()
            if not self.twitter.is_authenticated():
                self.currentService = self.twitter
                self.showTheSheet_(sender)

        isTwitterEnabled = bool(self.twitterCheckbox.state() == NSOnState)
        if isTwitterEnabled:
            self.ltp.syndicators.append(self.twitter)
        else:
            self.ltp.syndicators.remove(self.twitter)

    @IBAction
    def gplusChecked_(self, sender):
        if self.gplusCheckbox.state() == NSOnState:
            self.gplus.login()
            print self.gplus.is_authenticated()
            if not self.gplus.is_authenticated():
                self.currentService = self.gplus
                self.showTheSheet_(sender)
        
        isGPlusEnabled = bool(self.gplusCheckbox.state() == NSOnState)
        if isGPlusEnabled:
            self.ltp.syndicators.append(self.gplus)
        else:
            self.ltp.syndicators.remove(self.gplus)

    @IBAction
    def confirmToken_(self, sender):
        NSLog("Confirmed token")
        verifier = self.confirmTokenField.stringValue()

        if self.currentService == self.twitter:
            self.twitter.confirm_verifier(verifier)
        elif self.currentService == self.gplus:
            self.gplus.confirm_verifier(verifier)
                
        self.endTheSheet_(sender)

    @IBAction
    def cancelToken_(self, sender):
        self.endTheSheet_(sender)


    def showTheSheet_(self, sender):
        NSApp.beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
                self.confirmTokenSheet, NSApp.mainWindow(), self, None, None)

    def endTheSheet_(self, sender):
        NSApp.endSheet_(self.confirmTokenSheet)
        self.confirmTokenSheet.orderOut_(sender)

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


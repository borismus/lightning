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

# Required for status bar stuff.
from AppKit import NSStatusBar, NSSquareStatusItemLength, NSVariableStatusItemLength, NSImage, NSMenu, NSMenuItem, NSShiftKeyMask, NSCommandKeyMask, NSStatusWindowLevel


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
    
    # Confirm token sheet.
    confirmTokenSheet = IBOutlet()
    confirmTokenField = IBOutlet()
    
    # Publish log sheet.
    publishLogWindow = IBOutlet()
    publishLogField = IBOutlet()
    publishCancelButton = IBOutlet()

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
                
        self.setupStatusBar()

        self.didPublish = False
        self.didPreview = False


    def applicationWillTerminateNotification_(self, notification):
        NSLog("applicationWillTerminateNotification_")


    @IBAction
    def post_(self, sender):
        url = self.urlField.stringValue()
        title = self.titleField.stringValue()
        body = self.bodyField.string()
        # TODO(smus): Validate all fields.

        if self.isPreview:
            # Relinquish control to the link text processor for a preview.
            self.ltp.set_content(url, title, body)
            # Show the preview in a browser window.
            self.ltp.preview_content()
            # Go into publish mode.
            self.setPreviewMode(False)
            self.didPreview = True
        else:
            # If in publish mode, push to S3, publish to twitter & G+.
            print 'Syndicators: ' + str(self.ltp.syndicators)
            self.ltp.publish_syndicate()
            self.didPublish = True
            self.hideWindow()

    @IBAction
    def cancel_(self, sender):
        NSLog(u"Cancel")
        # Remove the link if one was created.
        self.ltp.clean()
        # Exit the application.
        self.hideWindow()
    
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

    def doPreview_(self, sender):
        NSLog("Doing a preview.")
        self.ltp.preview()

    def doPublish_(self, sender):
        NSLog("Doing a publish.")
        self.ltp.publish()
    
    def doLink_(self, sender):
        NSLog("Doing a link.")
        self.showWindow()


    def showTheSheet_(self, sender):
        NSApp.beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
                self.confirmTokenSheet, NSApp.mainWindow(), self, None, None)

    def endTheSheet_(self, sender):
        NSApp.endSheet_(self.confirmTokenSheet)
        self.confirmTokenSheet.orderOut_(sender)
    
    def hideWindow(self):
        # Hide the window.
        self.window().orderOut_(self)
        
        # Cleanup if the app did not publish (to keep state consistent).
        if not self.didPublish:
            self.ltp.clean()

        # Reset the internal state.
        self.didPreview = False
        self.didPublish = False
        
        # Clear all of the UI elements.
        self.titleField.setStringValue_('')
        self.urlField.setStringValue_('')
        self.bodyField.setString_('')
    
    def showWindow(self):
        self.window().makeKeyAndOrderFront_(self)
        self.window().setLevel_(NSStatusWindowLevel)
        # Give the window focus.
        NSApp.activateIgnoringOtherApps_(YES)

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
            browser = Browser()
            browser.open(url)
            return unicode(browser.title(), 'utf8')
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

    def setupStatusBar(self):
        statusbar = NSStatusBar.systemStatusBar()
        statusitem = statusbar.statusItemWithLength_(20).retain()
        
        icon = NSImage.imageNamed_('status')
        icon.setSize_((20, 20))
        statusitem.setImage_(icon)
        
        iconHighlight = NSImage.imageNamed_('status-hi')
        iconHighlight.setSize_((20, 20))
        statusitem.setAlternateImage_(iconHighlight)
        
        statusitem.setHighlightMode_(1)
        
        # TODO: Put this whole menu creation stuff into interface builder!
        menu = NSMenu.alloc().init()
        
        linkMenu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Post a Link', 'doLink:', '')
        linkMenu.setTarget_(self);
        # Make it possible to invoke the link menu via a keyboard shortcut.
        linkMenu.setKeyEquivalentModifierMask_(NSShiftKeyMask | NSCommandKeyMask)
        linkMenu.setKeyEquivalent_('l')
        menu.addItem_(linkMenu)
        
        
        menu.addItem_(NSMenuItem.separatorItem())
        
        previewMenu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Update Preview', 'doPreview:', '')
        previewMenu.setTarget_(self);
        menu.addItem_(previewMenu)
        
        publishMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Publish', None, '')
        publishMenu = NSMenu.alloc().init();
        s3MenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('S3', 'doPublish:', '')
        s3MenuItem.setTarget_(self);
        publishMenu.addItem_(s3MenuItem)
        publishMenuItem.setSubmenu_(publishMenu)
        menu.addItem_(publishMenuItem)
        
        menu.addItem_(NSMenuItem.separatorItem())

        quitMenu = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')
        menu.addItem_(quitMenu)
        
        statusitem.setMenu_(menu)
        menu.release();
    
    @IBAction
    def hidePublishLog_(self, sender):
        self.publishLogWindow.orderOut_(self);

    def showPublishLog(self):
        self.publishLogWindow.makeKeyAndOrderFront_(self);

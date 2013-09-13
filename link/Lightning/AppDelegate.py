#-*- coding: utf-8 -*-
#
#  LightningAppDelegate.py
#  Lightning
#
#  Created by Boris Smus on 7/12/13.
#  Copyright Boris Smus 2013. All rights reserved.
#

#from Foundation import *
from Foundation import NSObject, NSLog
from Cocoa import NSWindowController


class AppDelegate(NSObject):

    def applicationWillTerminate_(self,sender):
        NSLog("Application will terminate.")

    def applicationShouldTerminateAfterLastWindowClosed_(self, sender):
        return False
    
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
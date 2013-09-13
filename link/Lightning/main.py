#-*- coding: utf-8 -*-
#
#  main.py
#  Lightning
#
#  Created by Boris Smus on 7/12/13.
#  Copyright Boris Smus 2013. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import AppDelegate
import PMController

if __name__ == "__main__":
    # pass control to AppKit
    AppHelper.runEventLoop()

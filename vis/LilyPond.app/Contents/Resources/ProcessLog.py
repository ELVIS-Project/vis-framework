import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

import subprocess
import os
import signal

debug = 1

# class defined in ProcessLog.nib
class ProcessLog(NSObject):
    
    def init(self):
        self = super(ProcessLog, self).init()

        self.process = None
        self.out_str = '' 
        
        return self

    # the actual base class is NSObject
    def setProcess (self, process):
        self.out_str = ''
        if self.isLive():
           self.killProcess ()
           
        self.process = process

    def getNewOutput (self):
        out = self.process.stdout
        fd = out.fileno()
        size = 1024
        str = ''
        while True:
            s = unicode(os.read (fd, size), "utf-8")
            str += s
            if (len (s) == size):
                size *= 2
            else:
                break

        self.out_str += str
        return str

    def killProcess (self):
        if self.process:
            os.kill (self.process.pid, signal.SIGINT)

    def isLive (self):
        if not self.process:
            return False
        
        return self.process.poll() == None
 
# class defined in ProcessLog.nib
class ProcessLogWindowController(NSWindowController):
    # the actual base class is NSWindowController
    # The following outlets are added to the class:
    
    # window
    # textView
    # processLog
    # cancelButton
    # throbber
    textView = objc.IBOutlet()
    cancelButton = objc.IBOutlet()
    throbber = objc.IBOutlet()

    def __new__(cls):
        # "Pythonic" constructor
        return cls.alloc().initEmpty()

    def initEmpty(self):
        self = self.initWithWindowNibName_("ProcessLog")
        self.setWindowTitle_('Process')
        self.close_callback = None
        self.processLog = ProcessLog.alloc().init()
        self.window().makeFirstResponder_(self.textView)
        self.showWindow_(self)
        
        # The window controller doesn't need to be retained (referenced)
        # anywhere, so we pretend to have a reference to ourselves to avoid
        # being garbage collected before the window is closed. The extra
        # reference will be released in self.windowWillClose_()
        self.retain()
        return self

    def windowWillClose_(self, notification):

        ## UGH.
        if self.close_callback:
            self.close_callback (self)
        self.cancelProcess_ (self)
        self.suicide()
        
    def suicide (self):
        # see comment in self.initWithObject_()
        self.autorelease()

    def setWindowTitle_(self, title):
        self.window().setTitle_(title)

    def cancelProcess_(self, sender):
        if self.processLog.isLive ():
            self.processLog.killProcess ()
            # rest is handled by timer.
            
    def runProcessWithCallback (self, process, finish_callback):
        self.finish_callback = finish_callback
        self.processLog.setProcess (process)
                    
        self.cancelButton.setEnabled_ (True)
        self.throbber.setUsesThreadedAnimation_ (True)
        self.throbber.startAnimation_ (self)
        self.setTimer ()
    
    def setTimer (self):
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_  \
                     (1.0/10.0, self, "timerCallback:", 0, 0)

    def timerCallback_ (self, userinfo):
        self.updateLog_ (None)
        
        if self.processLog.isLive ():
            self.setTimer ()
        else:
            self.finish ()


    def finish (self):
        self.updateLog_(None)
        self.cancelButton.setEnabled_ (False)
        self.throbber.stopAnimation_ (self)

        cb = self.finish_callback
        if cb <> None:
            cb (self)

        
    def clearLog_ (self, sender):
        tv = self.textView
        ts_len = tv.textStorage().length ()
        range = NSRange()
        range.location = 0
        range.length = ts_len
        tv.replaceCharactersInRange_withString_ (range, '')
        
    def addText (self, str):
        tv = self.textView
        ts_len = tv.textStorage().length ()
        
        range = NSRange()
        range.location = ts_len
        range.length = 0
        tv.replaceCharactersInRange_withString_ (range, str)
        range.length = len (str)
        tv.scrollRangeToVisible_ (range)
        
    def updateLog_ (self, sender):
        str = self.processLog.getNewOutput ()
        self.addText (str)


if __name__ == "__main__":
    AppHelper.runEventLoop()


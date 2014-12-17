from Cocoa import *
from Foundation import *
from PyObjCTools import AppHelper
from time import sleep
import Quartz.CoreGraphics as CG
import struct
import os
import keycode
import string
import sys

class ScreenPixel(object):
    
    def capture(self, region = None):
        if region is None:
            region = CG.CGRectInfinite
        else:
            if region.size.width % 2 > 0:
                emsg = "Capture region width should be even (was %s)" % (
                    region.size.width)
                raise ValueError(emsg)
        
        image = CG.CGWindowListCreateImage(
            region,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageDefault)
            
        prov = CG.CGImageGetDataProvider(image)
                                           
        self._data = CG.CGDataProviderCopyData(prov)
                                               
        self.width = CG.CGImageGetWidth(image)
        self.height = CG.CGImageGetHeight(image)
                                               
    def pixel(self, x, y):
        data_format = "BBBB"
                
        offset = 4 * ((self.width*int(round(y))) + int(round(x)))
        b, g, r, a = struct.unpack_from(data_format, self._data, offset=offset)
        return (r, g, b)

class AppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, aNotification):
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(NSKeyDownMask, handler)

cmd = "osascript -e 'tell application \"System Events\" to keystroke \"%s\"'"


def isEmpty(rgb):
	return rgb[0] == rgb[1]

def getNextPiece(rgb):
	#TODO: write this function. Return number corresponding to piece

topLeftCenterx = 159
topLeftCentery = 82
squareWidth = 36
nextBoxx = 576
nextBoxy = 165

def handler(event):
    try:
	activeApps = NSWorkspace.sharedWorkspace().runningApplications()
	for app in activeApps:
		if app.isActive() and app.localizedName() != "Google Chrome":
			return
	if event.type() == NSKeyDown and keycode.tostring(event.keyCode()) in string.printable:
		if event.keyCode() == 36:
			sp = ScreenPixel()
			region = CG.CGRectMake(242, 200, 400, 432)
			sp.capture(region=region)
			grid = [[False for i in range(10)] for i in range(20)]
			for i in range(10):
				centerx = topLeftCenterx + i * squareWidth
				for j in range(20):
					centery = topLeftCentery + (19 - j) * squareWidth
					if(not(isEmpty(sp.pixel(centerx, centery)))):
						grid[19 - j][i] = True
			

    except ( KeyboardInterrupt ) as e:
        print 'Ending', e
        AppHelper.stopEventLoop()

def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    NSApp().setDelegate_(delegate)
    AppHelper.runEventLoop()


if __name__ == '__main__':
   main()

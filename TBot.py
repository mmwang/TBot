from Cocoa import *
from Foundation import *
from PyObjCTools import AppHelper
from time import sleep
import Quartz.CoreGraphics as CG
import Quartz
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

cmd = "osascript -e 'tell application \"System Events\" to key code %s'"
topLeftCenterx = 159
topLeftCentery = 82
squareWidth = 36
nextBoxx = 576
nextBoxy = 165
sColor = (148, 238, 58)
tColor = (231, 75, 200)
jColor = (67, 123, 254)
squareColor = (254, 216, 58)
zColor = (254, 66, 91)
lColor = (254, 155, 34)
eyeColor = (43, 208, 254)
delay = 0.035
sp = ScreenPixel()
region = CG.CGRectMake(242, 440, 400, 400)


def norm(v1, v2):
	return (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2 + (v1[2] - v2[2]) ** 2

def isEmpty(rgb):
	return rgb[0] == rgb[1]

def getPiece(rgb):
	colors = [0 for i in range(7)]
	colors[0] = norm(sColor, rgb)
	colors[1] = norm(tColor, rgb)
	colors[2] = norm(jColor, rgb)
	colors[3] = norm(squareColor, rgb)
	colors[4] = norm(zColor, rgb)
	colors[5] = norm(lColor, rgb)
	colors[6] = norm(eyeColor, rgb)
	return colors.index(min(colors))

def calculateScore(colSums):
	"""calculate score here
		factors:
		1) bumpiness
	"""
	sum = 0
	for i in range(1, 9):
		sum += (colSums[i] - colSums[i - 1]) ** 2
	return sum

def scoreBoard(piece, pos, orient, colSums):
	"""orient:
		0 for original
		1 for 90 clockwise (press up)
		2 for 180 (up twice)
		3 for -90 (press z)
	"""
	if piece == 0:
		if orient == 0:
			if colSums[pos] != colSums[pos + 1] or colSums[pos] != colSums[pos + 2] - 1:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 2
			colSums[pos + 2] += 1
		elif orient == 1:
			if colSums[pos] != colSums[pos + 1] + 1:
				return sys.maxint
			colSums[pos] += 2
			colSums[pos + 1] += 2
	elif piece == 1:
		if orient == 0:
			if colSums[pos] != colSums[pos + 1] or colSums[pos] != colSums[pos + 2]:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 2
			colSums[pos + 2] += 1
		elif orient == 1:
			if colSums[pos] != colSums[pos + 1] - 1:
				return sys.maxint
			colSums[pos] += 3
			colSums[pos + 1] += 1
		elif orient == 2:
			if colSums[pos] != colSums[pos + 2] or colSums[pos] != colSums[pos + 1] + 1:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 2
			colSums[pos + 2] += 1
		elif orient == 3:
			if colSums[pos] != colSums[pos + 1] + 1:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 3
	elif piece == 2:
		if orient == 0:
			if colSums[pos] != colSums[pos + 1] or colSums[pos] != colSums[pos + 2]:
				return sys.maxint
			colSums[pos] += 2
			colSums[pos + 1] += 1
			colSums[pos + 2] += 1
		elif orient == 1:
			if colSums[pos] != colSums[pos + 1] - 2:
				return sys.maxint
			colSums[pos] += 3
			colSums[pos + 1] += 1
		elif orient == 2:
			if colSums[pos] != colSums[pos + 1] or colSums[pos] != colSums[pos + 2] + 1:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 1
			colSums[pos + 2] += 2
		elif orient == 3:
			if colSums[pos] != colSums[pos + 1]:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 3
	elif piece == 3:
		if colSums[pos] != colSums[pos + 1]:
			return sys.maxint
		colSums[pos] += 2
		colSums[pos + 1] += 2
	elif piece == 4:
		if orient == 0:
			if colSums[pos] != colSums[pos + 1] + 1 or colSums[pos] != colSums[pos + 2] + 1:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 2
			colSums[pos + 2] += 1
		elif orient == 1:
			if colSums[pos] != colSums[pos + 1] - 1:
				return sys.maxint
			colSums[pos] += 2
			colSums[pos + 1] += 2
	elif piece == 5:
		if orient == 0:
			if colSums[pos] != colSums[pos + 1] or colSums[pos] != colSums[pos + 2]:
                        	return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 1
			colSums[pos + 2] += 2
		elif orient == 1:
			if colSums[pos] != colSums[pos + 1]:
                        	return sys.maxint
			colSums[pos] += 3
			colSums[pos + 1] += 1
		elif orient == 2:
			if colSums[pos] != colSums[pos + 1] - 1 or colSums[pos] != colSums[pos + 2] - 1:
                        	return sys.maxint
			colSums[pos] += 2
			colSums[pos + 1] += 1
			colSums[pos + 2] += 1
		elif orient == 3:
			if colSums[pos] != colSums[pos + 1] + 2:
                       		return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 3
	elif piece == 6:
		if orient == 0:
			if colSums[pos] != colSums[pos + 1] or colSums[pos] != colSums[pos + 2] or colSums[pos] != colSums[pos + 3]:
				return sys.maxint
			colSums[pos] += 1
			colSums[pos + 1] += 1
			colSums[pos + 2] += 1
			colSums[pos + 3] += 1
		elif orient == 1:
			colSums[pos] += 4
	
	return calculateScore(colSums)
	
def calculateBestPlacement(piece, grid):
	"""for each orient
		for each pos
			calculate board value
	"""
	colSums = [0 for i in range(9)]
	for i in range(9):
		colSums[i] = sum(grid[i])
	if min(colSums) >= 4 and piece == 6:
		return (9, 1, 0)
	orange = 4
	prange = [0, 0]
	prange[0] = 7
	prange[1] = 8
	if piece == 0 or piece == 4:
		orange = 2
	if piece == 3:
		orange = 1
		prange[0] = 8
	elif piece == 6:
		orange = 2
		prange[0] = 6
		prange[1] = 9
	bestInfo = (0, 0, sys.maxint) # pos, orient, score
	for orient in range(orange):
		for pos in range(prange[orient % 2]):
			temp = [colSums[i] for i in range(9)]
			currScore = scoreBoard(piece, pos, orient, temp)
			if(currScore < bestInfo[2]):
				bestInfo = (pos, orient, currScore)
	return bestInfo

def pressNTimes(which, N):
	kCode = 123
	if which == "right":
		kCode = 124
	elif which == "up":
		kCode = 126
	elif which == "down":
		kCode = 125
	elif which == "space":
		kCode = 49
	elif which == "z":
		kCode = 6
	elif which == "c":
		kCode = 8
	for i in range(N):
		keyDownEvt = Quartz.CGEventCreateKeyboardEvent(None, kCode, True)
		keyUpEvt = Quartz.CGEventCreateKeyboardEvent(None, kCode, False)
		Quartz.CGEventPost(Quartz.kCGHIDEventTap, keyDownEvt)
		sleep(0.045)
		Quartz.CGEventPost(Quartz.kCGHIDEventTap, keyUpEvt)
		sleep(0.05)

def executeMovement(piece, pos, orient):
	if orient != 1:
		if piece == 3:
			pos -= 4
		else:
			pos -= 3
	else:
		if piece == 6:
			pos -= 5
		else:
			pos -= 4
	if orient > 0:
		whichOrient = "up"
		N = 1
		if orient == 2:
			N = 2
		if orient == 3:
			whichOrient = "z"
		pressNTimes(whichOrient, N)
	if pos > 0:
		pressNTimes("right", pos)
	elif pos < 0:
		pressNTimes("left", -pos)
	pressNTimes("space", 1)
	if pos == 4 and piece == 6:
		sleep(0.3)
	else:
		sleep(0.07)

def printPiece(piece):
	if piece == 0:
		print "S-piece"
	elif piece == 1:
		print "T-piece"
	elif piece == 2:
		print "J-piece"
	elif piece == 3:
		print "Square-piece"
	elif piece == 4:
		print "Z-piece"
	elif piece == 5:
		print "L-piece"
	else:
		print "Eyepiece"

def handler(event):
    try:
	activeApps = NSWorkspace.sharedWorkspace().runningApplications()
	for app in activeApps:
		if app.isActive() and app.localizedName() != "Google Chrome":
			return
	if event.type() == NSKeyDown and keycode.tostring(event.keyCode()) in string.printable:
		if event.keyCode() == 48:
			sp.capture(region=region)
			currPiece = getPiece(sp.pixel(topLeftCenterx + 4 * squareWidth, topLeftCentery))
			holdPiece = None
			isFirstHold = True
			for i in range(15):
				grid = [[False for i in range(19)] for i in range(9)]
				for i in range(9):
					centerx = topLeftCenterx + i * squareWidth
					for j in range(19):
						centery = topLeftCentery + (19 - j) * squareWidth
						if(not(isEmpty(sp.pixel(centerx, centery)))):
							grid[i][j] = True
				nextPiece = getPiece(sp.pixel(nextBoxx, nextBoxy))
				if isFirstHold:
					holdPiece = nextPiece
				currMovementInfo = calculateBestPlacement(currPiece, grid)
				holdMovementInfo = calculateBestPlacement(holdPiece, grid)
				if currMovementInfo[2] <= holdMovementInfo[2]:
					executeMovement(currPiece, currMovementInfo[0], currMovementInfo[1])
				else:
					pressNTimes("c", 1)
					if isFirstHold:
						sleep(0.07)
						sp.capture(region=region)
						nextPiece = getPiece(sp.pixel(nextBoxx, nextBoxy))
						isFirstHold = False
					executeMovement(holdPiece, holdMovementInfo[0], holdMovementInfo[1])
					holdPiece = currPiece
				sp.capture(region=region)
				currPiece = nextPiece

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

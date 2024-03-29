#!/usr/bin/env python
# -*- coding: utf-8  -*-
# © 04.03.2019 Georgy Litvinov
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

defaultScoringOffset = 8

try:
    import scribus
    import re
except ImportError:
    print("Unable to import the 'scribus' module. This script will only run within")
    print("the Python interpreter embedded in Scribus. Try Script->Execute Script.")
    sys.exit(1)

hasSpineBackground = False
hasLeftTopMark = False
hasRightTopMark = False
leftSpineMarker = None
rightSpineMarker = None
pageItems = scribus.getPageItems()
for item in pageItems:
	if item[0].startswith('left_top_mark'):
		hasLeftTopMark = True
		leftSpineMarker = item[0]
	if item[0].startswith('right_top_mark'):
		hasRightTopMark = True
		rightSpineMarker = item[0]

leftOffset = defaultScoringOffset
rightOffset = defaultScoringOffset
if leftSpineMarker.startswith('left_top_mark_offset_'):
	leftOffsetString = leftSpineMarker[len('left_top_mark_offset_'):]
	if leftOffsetString.endswith('mm'):
		leftOffsetString = leftOffsetString[:-2]
	if re.match("\d+(\.\d+)?", leftOffsetString):
		leftOffset = float(leftOffsetString)
if rightSpineMarker.startswith('right_top_mark_offset_'):
	rightOffsetString = rightSpineMarker[len('right_top_mark_offset_'):]
	if rightOffsetString.endswith('mm'):
		rightOffsetString = rightOffsetString[:-2]
	if re.match("\d+(\.\d+)?", rightOffsetString):
		rightOffset = float(rightOffsetString)

if not hasLeftTopMark or not hasRightTopMark:
	scribus.messageBox('Error', "Document should have left_top_mark and right_top_mark or starts with left_top_mark_offset_ and right_top_mark_offset_ with suffix in mm to measure current spine width. Read more at https://litvinovg.pro/scribus-spine-width.html",  scribus.ICON_WARNING, scribus.BUTTON_OK)
	sys.exit(1)

newSpineWidth = scribus.valueDialog('Spine width','Set spine width in mm.')
if newSpineWidth == "0":
	scribus.messageBox('Error', "Spine width could not be zero.",  scribus.ICON_WARNING, scribus.BUTTON_OK)
	sys.exit(1)
newWidth = float(newSpineWidth.replace(',','.'))
if newWidth < 0:
	scribus.messageBox('Error', "Spine width could not be negative",  scribus.ICON_WARNING, scribus.BUTTON_OK)
	sys.exit(1)

#set units to mm
scribus.setUnit(1)
PageX,PageY = scribus.getPageSize()
leftX, leftY = scribus.getPosition(leftSpineMarker)
rightX, rightY = scribus.getPosition(rightSpineMarker)
curSpineWidth = rightX - leftX - leftOffset - rightOffset

spineWidthDiff = newWidth - curSpineWidth
halfWidthDiff = spineWidthDiff / 2 

vGuides = [(PageX/2), (PageX/2 + newWidth/2), (PageX/2 - newWidth/2)]
hGuides = []

for item in pageItems:
	if item[0].startswith('spine_background'):
		X,Y = scribus.getPosition(item[0])
		hasSpineBackground = True
		Xsize,Ysize = scribus.getSize(item[0])
		scribus.sizeObject(newWidth, Ysize, item[0])
		scribus.moveObjectAbs(PageX/2 - newWidth/2, Y ,item[0])
	
for item in pageItems:
	X,Y = scribus.getPosition(item[0])
	if item[0].startswith('background'):
		scribus.moveObject(-halfWidthDiff, 0 , item[0])
		Xsize,Ysize = scribus.getSize(item[0])
		backgroundSize = Xsize + spineWidthDiff 
		scribus.sizeObject(backgroundSize, Ysize, item[0])
	if item[0].startswith('left_'):
		scribus.moveObject(-halfWidthDiff, 0 , item[0])
		if item[0].startswith('left_background'):
			Xsize,Ysize = scribus.getSize(item[0])
			leftBackgroundSize = PageX/2 - X + halfWidthDiff + 0.05 
			if hasSpineBackground:
				leftBackgroundSize -=  newWidth/2
			scribus.sizeObject(leftBackgroundSize, Ysize, item[0])
		if item[0].startswith('left_top_crop'):
			newX,newY = scribus.getPosition(item[0])
			Xsize,Ysize = scribus.getSize(item[0])
			vGuides.append(newX+Xsize)
	if item[0].startswith('right_'):
		if item[0].startswith('right_background'):
			Xsize,Ysize = scribus.getSize(item[0])
			rightBackgroundSize = Xsize + halfWidthDiff
			if hasSpineBackground:
				rightBackgroundSize -=  halfWidthDiff
			scribus.sizeObject(rightBackgroundSize, Ysize, item[0])
			rightBackgroundX = PageX/2 -0.05
# Start after spine ends
			if hasSpineBackground:
				rightBackgroundX +=  newWidth/2	
			scribus.moveObjectAbs(rightBackgroundX, Y ,item[0])
		else:
			scribus.moveObject(halfWidthDiff, 0 , item[0])
		if item[0].startswith('right_top_crop'):
			newX,newY = scribus.getPosition(item[0])
			Xsize,Ysize = scribus.getSize(item[0])
			vGuides.append(newX)
			hGuides.append(newY+Ysize)
		if item[0].startswith('right_bottom_crop'):
			newX,newY = scribus.getPosition(item[0])
			hGuides.append(newY)
	if item[0].startswith('spine_logo'):
		Xsize,Ysize = scribus.getSize(item[0])
		newBookX = newWidth		
		if newWidth - 2.6 > 2:
			newBookX = newWidth - 2.6
		multiplier = newBookX/Xsize
		newBooKY = Ysize * multiplier
		scribus.sizeObject(newBookX, newBooKY, item[0])
		scribus.moveObjectAbs(PageX/2 - newBookX/2 , Y ,item[0])

scribus.setVGuides(vGuides)
scribus.setHGuides(hGuides)

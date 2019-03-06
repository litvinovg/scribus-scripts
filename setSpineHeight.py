#!/usr/bin/env python
# -*- coding: utf-8  -*-
# © 04.03.2019 Georgy Litvinov
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
try:
    import scribus
except ImportError:
    print "Unable to import the 'scribus' module. This script will only run within"
    print "the Python interpreter embedded in Scribus. Try Script->Execute Script."
    sys.exit(1)
newSpineHeight = scribus.valueDialog('Задание высоты корешка','Введите новую высоту корешка')

#set units to mm
scribus.setUnit(1)
PageX,PageY = scribus.getPageSize()
leftX, leftY = scribus.getPosition("left_top_mark")
rightX, rightY = scribus.getPosition("right_top_mark")
curSpineHeight = rightX - leftX - 16
newHeight = float(newSpineHeight)
spineHeightDiff = newHeight - curSpineHeight
halfHeightDiff = spineHeightDiff / 2 

pageItems = scribus.getPageItems()
for item in pageItems:
	X,Y = scribus.getPosition(item[0])
	if item[0].startswith('left_'):
		scribus.moveObject(-halfHeightDiff, 0 , item[0])
		if item[0].startswith('left_background'):
			Xsize,Ysize = scribus.getSize(item[0])
			scribus.sizeObject(PageX/2 - X + halfHeightDiff + 0.1 , Ysize, item[0])
	if item[0].startswith('right_'):
		if item[0].startswith('right_background'):
			Xsize,Ysize = scribus.getSize(item[0])
			scribus.sizeObject(Xsize + halfHeightDiff, Ysize, item[0])
			scribus.moveObjectAbs(PageX/2 -0.1, Y ,item[0])
		else:
			scribus.moveObject(halfHeightDiff, 0 , item[0])
	if item[0].startswith('spine_logo'):
		Xsize,Ysize = scribus.getSize(item[0])
		newBookX = newHeight - newHeight * 0.2
		multiplier = newBookX/Xsize
		newBooKY = Ysize * multiplier
		scribus.sizeObject(newBookX, newBooKY, item[0])
		scribus.moveObjectAbs(PageX/2 - newBookX/2 , Y ,item[0])
scribus.setVGuides([(PageX/2), (PageX/2 + newHeight/2), (PageX/2 - newHeight/2)])



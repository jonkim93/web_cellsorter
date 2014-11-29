#!/usr/bin/python

import math

class Blob(object):
	def __init__(self, blobType=None, center=None, boundingBox=None, area=None, color=None, roi=None):
		self.blobType = blobType
		self.center = center
		self.boundingBox = boundingBox
		self.area = area
		self.color = color
		self.roi = roi

	def __str__(self):
		return "BlobType: %s \n\tCenter: %s \n\tBounding Box: %s \n\tArea: %d \n\tColor: %s \n\t" % (str(self.blobType), str(self.center), str(self.boundingBox), self.area, str(self.color))

	def getBlobType(self):
		return self.blobType

	def getCenter(self):
		return self.center

	def getBoundingBox(self):
		return self.boundingBox

	def getArea(self):
		return self.area

	def calculateColor(self):
		imageValues = []
		for x in xrange(0, self.roi.shape[1]): 
			for y in xrange(0, self.roi.shape[0]):
				imageValues.append(self.roi[y,x])
		self.color = [sum(a)/len(a) for a in zip(*imageValues)]
		if len(self.color) == 0:
			self.color = [300,300,300] # INVALID COLOR VALUES		


	def calculateDistance(self, other):
		if other.getCenter() != None and self.getCenter() != None:
			return math.sqrt((other.getCenter()[0] - self.getCenter()[0])**2 + (other.getCenter()[1] - self.getCenter()[1])**2 )
		else:
			raise Exception("does not have a valid center")

	def getColor(self):
		if self.color == None:
			self.calculateColor()
		return self.color
			

	def getROI(self):
		return self.roi

	def setBlobType(self, blobType):
		self.blobType = blobType

	def setCenter(self, center):
		self.center = center

	def setBoundingBox(self, boundingBox):
		self.boundingBox = boundingBox

	def setArea(self, area):
		self.area = area

	def setColor(self, color):
		self.color = color

	def setROI(self, roi):
		self.roi = roi


#!/usr/bin/python

import cv2
import math
import sys
import numpy as np
from constants import *
from blob import *

# SUPER CLASS

class Operation(object):
	def __init__(self, pipeline=None, function=None, staticParameters=None, parameterNames=None):
		self.function=function
		self.staticParameters = staticParameters
		self.parameterNames = parameterNames
		self.pipeline = pipeline

	def execute(self):
		self.parameters = self.getParameters()

	def getParameters(self):
		parameters = {}
		for parameterName in self.parameterNames:
			if self.staticParameters != None and parameterName in self.staticParameters.keys():
				parameters[parameterName] = self.staticParameters[parameterName]
			elif self.pipeline != None and parameterName in self.pipeline.values.keys():
				parameters[parameterName] = self.pipeline.values[parameterName]
			#elif parameterName not in parameters.keys():
			#	raise Exception("parameter %s not provided!" % parameterName)
		return parameters

	def getBounds(self, img, x0, x1, y0, y1):
		if x0 < 0:
			x0 = 0
		if x1 > img.shape[1]:
			x1 = img.shape[1]
		if y0 < 0:
			y0 = 0
		if y1 > img.shape[0]:
			y1 = img.shape[0]
		return x0, x1, y0, y1

	def drawCircles(self, img, circles):
		if circles != None and img != None:
			circles = np.uint16(np.around(circles))
	        for circle in circles:
	            for i in circles[0,:]:
	                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
	                cv2.circle(img,(i[0],i[1]),2,(0,0,255),3)


# SUB CLASSES

class CannyOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(CannyOp, self).__init__(pipeline, cv2.Canny, staticParameters, ["img", "minValue", "maxValue"])

	def execute(self):
		super(CannyOp, self).execute()
		self.pipeline.values["img"] = self.function(self.parameters["img"], self.parameters["minValue"], self.parameters["maxValue"])

class ErodeOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(ErodeOp, self).__init__(pipeline, cv2.erode, staticParameters, ["img", "kernelSize"])

	def execute(self):
		super(ErodeOp, self).execute()
		element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.parameters["kernelSize"], self.parameters["kernelSize"]))
		self.pipeline.values["img"] = self.function(self.parameters["img"], element)

class DilateOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(DilateOp, self).__init__(pipeline, cv2.dilate, staticParameters, ["img", "kernelSize"])

	def execute(self):
		super(DilateOp, self).execute()
		element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.parameters["kernelSize"], self.parameters["kernelSize"]))
		self.pipeline.values["img"] = self.function(self.parameters["img"], element)

class ThresholdOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(ThresholdOp, self).__init__(pipeline, cv2.inRange, staticParameters, ["hsvImg", "img", "lowerHue", "upperHue", "lowerSat", "upperSat", "lowerVal", "upperVal"])

	def execute(self):
		super(ThresholdOp, self).execute()
		hsvImg = self.pipeline.values["hsvImg"]
		self.pipeline.values["img"] = hsvImg.copy()
		self.pipeline.values["img"] = self.function(hsvImg, 
			(self.parameters["lowerHue"], self.parameters["lowerSat"], self.parameters["lowerVal"]), 
			(self.parameters["upperHue"], self.parameters["upperSat"], self.parameters["upperSat"]),
			self.pipeline.values["img"])

class AdaptiveThresholdOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(AdaptiveThresholdOp, self).__init__(pipeline, cv2.adaptiveThreshold, staticParameters, ["grayImg", "maxValue", "blockSize"])

	def execute(self):
		super(AdaptiveThresholdOp, self).execute()
		grayImg = self.pipeline.values["grayImg"]
		self.pipeline.values["img"] = self.function(grayImg,\
			self.parameters["maxValue"],\
			cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
			cv2.THRESH_BINARY,\
			self.parameters["blockSize"],\
			2)

class BlurOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(BlurOp, self).__init__(pipeline, cv2.medianBlur, staticParameters, ["img", "kernelSize"])

	def execute(self):
		super(BlurOp, self).execute()
		self.pipeline.values["img"] = self.function(self.parameters["img"], self.parameters["kernelSize"])

class DistanceTransformOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(DistanceTransformOp, self).__init__(pipeline, cv2.distanceTransform, staticParameters, ["img"])

	def execute(self):
		super(DistanceTransformOp, self).execute()
		kernel = np.ones((3,3),np.uint8)
		img = cv2.morphologyEx(self.parameters["img"],cv2.MORPH_OPEN,kernel, iterations = 2)
		self.pipeline.values["img"] = self.function(img, cv2.cv.CV_DIST_L2, 5)

class WatershedOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(WatershedOp, self).__init__(pipeline, cv2.watershed, staticParameters, ["img"])

	def execute(self):
		super(WatershedOp, self).execute()
		kernel = np.ones((3,3),np.uint8)
		opening = cv2.morphologyEx(self.parameters["img"],cv2.MORPH_OPEN,kernel, iterations = 2)
		sure_bg = cv2.dilate(opening, kernel, iterations=3)
		dist_transform = cv2.distanceTransform(opening, cv2.cv.CV_DIST_L2, 5)
		ret, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)
		sure_fg = np.uint8(sure_fg)
		unknown = cv2.subtract(sure_bg, sure_fg)
		ret, markers = cv2.connectedComponents(sure_fg)
		markers += 1
		markers[unknown==255] = 0
		markers = cv2.watershed(img, markers)
		img[markers == -1] = [255,0,0]
		cv2.imshow("test", img)
		cv2.waitKey(0)
		cv2.destroyWindow("test")



# COUNTING OPERATIONS
class GetBlobsFromCirclesOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(GetBlobsFromCirclesOp, self).__init__(pipeline, cv2.HoughCircles, staticParameters, ["hsvImg", 
			"img", "constant", "dp", "minDistance", "param1", "param2", "minRadius", "maxRadius", "blobType"])

	def execute(self):
		super(GetBlobsFromCirclesOp, self).execute()
		circles = self.function(self.parameters["img"], self.parameters["constant"], dp=self.parameters["dp"],\
		                        minDist=self.parameters["minDistance"],\
		                        param1=self.parameters["param1"],\
		                        param2=self.parameters["param2"],\
		                        minRadius=self.parameters["minRadius"],\
		                        maxRadius=self.parameters["maxRadius"])
		blobs = []
		self.pipeline.values["unfilteredBlobsImg"] = self.pipeline.values["originalImg"].copy()
		if circles != None:
			for circle in circles[0]:
				x, y ,r = circle[0], circle[1], circle[2]
				center = (x,y)
				area = math.pi*r*r
				x0, x1, y0, y1 = self.getBounds(self.parameters["img"], x-r, x+r, y-r, y+r)
				if "hsvImg" in self.parameters.keys():
					roi = self.parameters["hsvImg"].copy()[y0:y1, x0:x1]
				else: 
					roi = None
				boundingBox = (x0, y0, x1-x0, y1-y0)
				blobs.append(Blob(self.parameters["blobType"], center, boundingBox, area, None, roi))
				#cv2.rectangle(self.pipeline.values["unfilteredBlobsImg"],(x0,y0),(x1,y1),(60,140,40),2)
			self.drawCircles(self.pipeline.values["unfilteredBlobsImg"], circles)
		self.pipeline.values["blobs"] = blobs

class GetBlobsFromContoursOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(GetBlobsFromContoursOp, self).__init__(pipeline, cv2.findContours, staticParameters, ["img", "blobType", "hsvImg"])
	
	def execute(self):
		super(GetBlobsFromContoursOp, self).execute()
		blobs = []
		contours, hierarchy = cv2.findContours(self.parameters["img"].copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
		self.pipeline.values["unfilteredBlobsImg"] = self.pipeline.values["originalImg"].copy()
		for i in xrange(len(contours)):
			contour = contours[i]
			m = cv2.moments(contour)
			if m['m00'] == 0:
				pass
			else:
				cx = int(m['m10']/m['m00'])
				cy = int(m['m01']/m['m00'])
				area = int(cv2.contourArea(contour)) #int(m['m00'])
				boundingBox = cv2.boundingRect(contour)
				x,y,w,h = boundingBox
				x0, x1, y0, y1 = self.getBounds(self.parameters["img"], x, x+w, y, y+h)
				roi = self.parameters["hsvImg"][y0:y1, x0:x1]
				blobs.append(Blob(self.parameters["blobType"], (cx, cy), boundingBox, area, None, roi))
				cv2.drawContours(self.parameters["img"], contours, i, (0, 255, 0), 1)
				cv2.rectangle(self.pipeline.values["unfilteredBlobsImg"],(x,y),(x+w,y+h),(60,140,40),2)
		self.pipeline.values["img"] = self.parameters["img"].copy()
		self.pipeline.values["blobs"] = blobs


# HELPER OPERATIONS
class ShowImageOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(ShowImageOp, self).__init__(pipeline, cv2.imshow, staticParameters, ["windowName", "on", "key"])

	def execute(self):
		super(ShowImageOp, self).execute()
		if self.parameters["on"]: 
			self.function(self.parameters["windowName"], self.pipeline.values[self.parameters["key"]])
			cv2.waitKey(0)
			cv2.destroyWindow(self.parameters["windowName"])

class SaveImageOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(SaveImageOp, self).__init__(pipeline, cv2.imwrite, staticParameters, ["modifier", "on", "key", "path"])

	def execute(self):
		super(SaveImageOp, self).execute()
		if self.parameters["on"]:
			filePath = SAVEDIR+self.pipeline.values["fileName"]+"_"+self.parameters["modifier"]+"_"+str(self.pipeline.values["index"])+".jpg"
			cv2.imwrite(filePath, self.pipeline.values[self.parameters["key"]])
			print "successfully saved to ", filePath

class LoadImageOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(LoadImageOp, self).__init__(pipeline, cv2.imread, staticParameters, ["imgPath"])

	def execute(self):
		super(LoadImageOp, self).execute()
		try:
		    for prefix in PREFIXES:
		        for suffix in SUFFIXES:
		            path = prefix+self.parameters["imgPath"]+suffix
		            img = cv2.imread(path)
		            if img != None:
		                break
		        if img != None:
		            break
		    if img == None:
		        raise Exception("image not found: %s " % self.parameters["imgPath"])
		    else:
		    	self.pipeline.values["img"] = img
		except Exception as e:
			print e
			sys.exit(1)
		if self.pipeline.values["img"] == None:
			raise Exception("image %s could not be loaded" % self.parameters["imgPath"])

class ConvertColorOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(ConvertColorOp, self).__init__(pipeline, cv2.cvtColor, staticParameters, ["img", "colorSpaceConstant"])

	def execute(self):
		super(ConvertColorOp, self).execute()
		self.pipeline.values["originalImg"] = self.pipeline.values["img"].copy()
		#self.pipeline.values["img"] = self.function(self.pipeline.values["originalImg"].copy(), self.parameters["colorSpaceConstant"])		

		if self.parameters["colorSpaceConstant"] == 6L:
			self.pipeline.values["grayImg"] = self.function(self.pipeline.values["originalImg"].copy(), self.parameters["colorSpaceConstant"])
			self.pipeline.values["img"] = self.pipeline.values["grayImg"]
		elif self.parameters["colorSpaceConstant"] == 40L:
			self.pipeline.values["hsvImg"] = self.function(self.pipeline.values["originalImg"].copy(), self.parameters["colorSpaceConstant"])
			self.pipeline.values["img"] = self.pipeline.values["hsvImg"]

class SubDivideOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(SubDivideOp, self).__init__(pipeline, None, staticParameters, ["img", "xDivide", "yDivide"])

	def execute(self):
		super(SubDivideOp, self).execute()
		width = self.parameters["img"].shape[0]
		height = self.parameters["img"].shape[1]
		sub_w = float(width)/float(self.parameters["xDivide"])
		sub_h = float(height)/float(self.parameters["yDivide"])
		subdividedimgs = []
		for x in xrange(self.parameters["xDivide"]):
			for y in xrange(self.parameters["yDivide"]):
				subdividedimgs.append(self.parameters["img"][sub_w*x:sub_w*x+sub_w, sub_h*y:sub_h*y+sub_h])
		self.pipeline.values["imgs"] = subdividedimgs

# FILTER OPERATIONS
class CellBeadProximityFilterOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(CellBeadProximityFilterOp, self).__init__(pipeline, None, staticParameters, ["cells", "beads", "maxDistance", "img"])

	def execute(self):
		super(CellBeadProximityFilterOp, self).execute()
		filteredCells = []
		count = 0
		if DEBUG:
			print "NUMBER OF CELLS: ",str(len(self.parameters["cells"]))
		for cell in self.parameters["cells"]:
			for bead in self.parameters["beads"]:
				if cell.calculateDistance(bead) < self.parameters["maxDistance"]:
					filteredCells.append(cell)
					x,y,w,h = cell.getBoundingBox()
					cv2.rectangle(self.pipeline.values["img"], (int(x),int(y)), (int(x+w), int(y+h)), (60,140,140),2 )
					if DEBUG:
						print "NUM CELLS IN BLOB: %d" % (-(-(cell.getArea()+1) // CELL_SIZE))
					count += (-(-(cell.getArea()+1) // CELL_SIZE))
					break
		self.pipeline.values["filteredCells"] = filteredCells
		self.pipeline.values["count"] = count

class FilterBlobsOp(Operation):
	def __init__(self, pipeline=None, staticParameters=None):
		super(FilterBlobsOp, self).__init__(pipeline, None, staticParameters, ["originalImg", "img", "blobs", "lowerHue", "upperHue", "lowerArea", "upperArea"])

	def execute(self):
		super(FilterBlobsOp, self).execute()
		filteredBlobs = []
		for blob in self.parameters["blobs"]:
			properColorRange = blob.getColor()[0] > self.parameters["lowerHue"] and blob.getColor()[0] < self.parameters["upperHue"]
			properArea = blob.getArea() > self.parameters["lowerArea"] and blob.getArea() < self.parameters["upperArea"]		
			if properColorRange and properArea:
				filteredBlobs.append(blob)
			"""else:
				if DEBUG:
					print "proper color? %s proper area? %s" % (properColorRange, properArea)"""
		"""if DEBUG:
			if len(self.parameters["blobs"]) == 0:
				print "NO BLOBS"
			else:
				print "LENGTH OF FILTERED %ss: %d" % (self.parameters["blobs"][0].getBlobType(),len(filteredBlobs))"""
		drawImg = self.pipeline.values["originalImg"].copy()
		for blob in filteredBlobs:
			x,y,w,h = blob.getBoundingBox()
			cv2.rectangle(drawImg, (x,y),(x+w,y+h),(0,255,0),2)
		self.pipeline.values["filteredBlobsImg"] = drawImg
		self.pipeline.values["blobs"] = filteredBlobs


"""
cv2.imshow("test", self.pipeline.values["originalImg"])
cv2.waitKey(0)
cv2.destroyWindow("test")
"""




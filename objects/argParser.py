#!/usr/bin/python

import xml.etree.ElementTree as elementTree
from pipeline import *
from operation import *

nameToOp = {
	"BlurOp": BlurOp,
	"CannyOp": CannyOp,
	"ErodeOp": ErodeOp,
	"DilateOp": DilateOp,
	"ThresholdOp": ThresholdOp,
	"GetBlobsFromCirclesOp": GetBlobsFromCirclesOp,
	"GetBlobsFromContoursOp": GetBlobsFromContoursOp,
	"ShowImageOp": ShowImageOp,
	"LoadImageOp": LoadImageOp,
	"ConvertColorOp": ConvertColorOp,
	"SubDivideOp": SubDivideOp,
	"CellBeadProximityFilterOp": CellBeadProximityFilterOp,
	"FilterBlobsOp": FilterBlobsOp,
	"AdaptiveThresholdOp": AdaptiveThresholdOp,
	"DistanceTransformOp": DistanceTransformOp,
	"WatershedOp": WatershedOp,
	"SaveImageOp": SaveImageOp
}

class ArgParser(object):
	def parse(self, argFilePath):
		assert argFilePath != None
		p = Pipeline([])
		tree = elementTree.parse(argFilePath)
		for child in tree.getroot():
			if child.tag == 'repeat':
				p.addOp(self.parseRepeat(child, p))
			elif child.tag == 'operation':
				p.addOp(self.parseOp(child, p))
			else:
				raise Exception("invalid xml element")
		return p

	def parseOp(self, xmlOpElement, pipeline):
		staticParameters = {}
		for child in xmlOpElement:
			staticParameters[child.tag] = eval(child.text)
		return nameToOp[xmlOpElement.get("name")](pipeline=pipeline, staticParameters=staticParameters)

	def parseRepeat(self, xmlRepeatElement, pipeline):
		ops = []
		for i in xrange(int(xmlRepeatElement.find("iterations").text)):
			for grandchild in xmlRepeatElement:
				if grandchild.tag == 'operation':
					ops.append(self.parseOp(grandchild, pipeline))
		return ops




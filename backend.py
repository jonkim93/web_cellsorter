#!/usr/bin/python

from objects.argParser import *
from objects.pipeline import *
import sys
from objects.constants import *
import cv2
from os import listdir
from os.path import isfile, join
import collections

#TRYPAN BLUE

def getSubImages(imgPath):
	prelimPipeline = Pipeline([], {"imgPath": imgPath})
	prelimPipeline.addOp(LoadImageOp(pipeline=prelimPipeline))
	prelimPipeline.addOp(SubDivideOp(pipeline=prelimPipeline, staticParameters={"xDivide": 6, "yDivide": 8}))
	results = prelimPipeline.execute()
	subdividedImgs = results["imgs"]

	processedImgs = []
	for img in subdividedImgs:
		h, w = img.shape[:2]
		processedImgs.append(cv2.resize(img, (2*w, 2*h), interpolation=cv2.INTER_CUBIC))
	return processedImgs

def process(imgPath, DEBUG=False):
	cellArgParser = ArgParser()
	beadArgParser = ArgParser()
	beadAttachedArgParser = ArgParser()

	if THRESHOLD_CELLS:
		segmentCellsPipeline = cellArgParser.parse("config/cell_thresholdDetect.xml")
	else:
		segmentCellsPipeline = cellArgParser.parse("config/cell_circleDetect.xml")
	segmentBeadsPipeline = beadArgParser.parse("config/bead_circleDetect.xml")
	countBeadAttachedCellsPipeline = beadAttachedArgParser.parse("config/countBeadAttachedCells.xml")

	subdividedImgs = getSubImages(imgPath)

	cellCount = 0
	images = []
	for i in xrange(len(subdividedImgs)): 
		segmentCellsPipeline.values["fileName"] = imgPath.split("/")[-1][:-4]
		segmentBeadsPipeline.values["fileName"] = imgPath.split("/")[-1][:-4]	
		countBeadAttachedCellsPipeline.values["fileName"] = imgPath.split("/")[-1][:-4]

		#if i in IGNORE_INDICES_48:
		#	continue
		if DEBUG:
			print "PROCESSING IMG %d" % i
			print "executing segment cells"
		segmentCellsPipeline.values["img"] = subdividedImgs[i]
		segmentCellsPipeline.values["index"] = i
		cells = segmentCellsPipeline.execute()["blobs"]

		if DEBUG:
			print "executing segment beads"
		segmentBeadsPipeline.values["img"] = subdividedImgs[i]
		segmentBeadsPipeline.values["index"] = i
		beads = segmentBeadsPipeline.execute()["blobs"]

		if DEBUG:
			print "executing counting"
		countBeadAttachedCellsPipeline.values["img"] = subdividedImgs[i]
		countBeadAttachedCellsPipeline.values["cells"] = cells
		countBeadAttachedCellsPipeline.values["beads"] = beads
		countBeadAttachedCellsPipeline.values["index"] = i
		results = countBeadAttachedCellsPipeline.execute()
		images.append(countBeadAttachedCellsPipeline.values["img"])

		if DEBUG:
			print "CELL COUNT FOR IMG %d : %d \n" % (i, results["count"])
		cellCount += results["count"]
		segmentCellsPipeline.values = {}
		segmentBeadsPipeline.values = {}
		countBeadAttachedCellsPipeline.values = {}

	if DEBUG:
		print "%s TOTAL CELL COUNT: %d\n" % (imgPath.split("/")[-1],cellCount)
	return cellCount, images

def multi_process(start_num, end_num):
	imgCellCount = collections.OrderedDict()
	for i in xrange(start_num, end_num+1):
		cellCount = main("/Users/Jon/Documents/College/Research/HealyLab/Trial1/IMG_"+str(i))
		imgCellCount["IMG_"+str(i)] = cellCount

def getFilesInDir(path):
	files = [ join(path,f) for f in listdir(path) if isfile(join(path,f)) and f[-4:].lower() in SUFFIXES ]
	return files

if __name__=="__main__":
	option = sys.argv[1]
	if option == "-s":
		imgPath = INPUTDIR + sys.argv[2]
		main(imgPath)
	elif option == "-r":
		files = getFilesInDir(INPUTDIR)
		print files
		f = files[eval(sys.argv[2])]
		print f
		main(f)
	elif option == "-m":
		start_num = eval(sys.argv[2])
		end_num = eval(sys.argv[3])
		multi_process(start_num, end_num)
	else:
		raise Exception("not a valid option")



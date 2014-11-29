#!/usr/bin/python

from operation import *

class Pipeline(object):
	def __init__(self, opList=[], values={}):
		self.opList = opList
		self.values = values

	def execute(self):
		for op in self.opList:
			op.execute()
		return self.values

	def addOp(self, operation):
		if isinstance(operation, Operation):
			self.opList.append(operation)
		elif type(operation) == list:
			self.opList += operation

	def clearArgs(self):
		for op in self.opList:
			op.parameters = {}
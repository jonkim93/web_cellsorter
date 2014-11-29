#!/usr/bin/python

INPUTDIR = "/Users/Jon/Documents/College/Research/HealyLab/In/raw/"
SAVEDIR = "/Users/Jon/Documents/College/Research/HealyLab/Out/Processed/trypanBlue/"

CELL_SIZE = 4000

DEBUG = False
PREFIXES = ["CellBoundImages/", "WrightStainImages/", "CellScope/", "" ]
SUFFIXES = [".jpg", ".png", ".jpeg", ".tif", ""]

THRESHOLD_CELLS = False

IGNORE_INDICES_48 = (0,1,6,7,8,14,15,16,23,24,31,32,39,40,41,46,47)
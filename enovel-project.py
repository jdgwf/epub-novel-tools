#!/usr/bin/env python3

"""Sets up a series of directories and MarkDown compilation tools for Novel E-Book novel
creation on Linux (tested on Ubuntu 16.04 and 16.10, should work on and Debian too).
Provides word count functions and history tracking.
"""

import os
import sys
from glob import glob
from shutil import copyfile
import yaml
import csv
import datetime
import imp
import hashlib
import requests

__author__ = "Jeffrey D. Gordon"
__copyright__ = "Copyright 2016-2017, Jeffrey D. Gordon"
__credits__ = ["Jeffrey D. Gordon"]
__license__ = "GPL"
__version__ = "0.8.5"
__maintainer__ = "Jeffrey D. Gordon"
__email__ = "jeff@jdgwf.com"
__status__ = "Development"

# Configurable Options (not really recommended)
exportDirectory = "./Exports"
manuscriptDir = "./Manuscript"
progressDirectory = "./Progress"

# Initial Config - this will create a config.yml file to modify
todaysProgress = 0
recreateEPUBAndTempFiles = True

config = dict(
	bookName = "My Ebook",
	bookFile = "My Ebook",
	authorName = "Author Name",
	copyRight = str(datetime.datetime.now().year) + " All rights reserved",
	languageCode = "en-US",
	publisherName = "Self Published",
	coverImage = "",
	nanoWriMoSecretKey = "",
	nanoWriMoUsername = ""
)

if os.path.isfile("config.yml") == False:
	with open('config.yml', 'w', encoding="utf8") as outfile:
		yaml.dump(config, outfile, default_flow_style=False)
else:
	config = yaml.safe_load(open("config.yml", encoding="utf8"))


# To get NanoWrioSecret go to https://nanowrimo.org/api/wordcount while logged in.
if "nanoWriMoSecretKey" not in config:
	config["nanoWriMoSecretKey"] = ""

if "nanoWriMoUsername" not in config:
	config["nanoWriMoUsername"] = ""

try:
    imp.find_module('numpy')
    imp.find_module('matplotlib')
    foundMatPlotLib = True
except ImportError:
    foundMatPlotLib = False

if foundMatPlotLib:
	import numpy as np
	import matplotlib.pyplot as plt

# Immutable Variables
nanoAPIUrlCurrentWordCount = "https://nanowrimo.org/modules/wordcount_api/wc/" + config["nanoWriMoUsername"]
nanoAPIUrlCurrentWordCountHistory = "https://nanowrimo.org/modules/wordcount_api/wchistory/" + config["nanoWriMoUsername"]
nanoAPIUrlUpdateWordCount = "https://nanowrimo.org/api/wordcount"

def normalizeMarkDown( fileContents ):
	# trim the contents
	fileContents = fileContents.strip()
	# remove existing markdown HRs
	fileContents = fileContents.replace( "----\n", "")
	fileContents = fileContents.replace( "\n----", "")
	fileContents = fileContents.replace( "---\n", "")
	fileContents = fileContents.replace( "\n---", "")

	# replace all triple newlines with double newlines (normalize any extras)
	fileContents = fileContents.replace( "\n\n\n", "\n\n")

	return fileContents

def updateNaNo():
	if config["nanoWriMoSecretKey"] and config["nanoWriMoUsername"]:

		manuscriptData = preProcess()
		manuscriptData = normalizeMarkDown( manuscriptData )
		theWordCount = str(len(manuscriptData.split()))

		theWordCount = "59003"

		theHash =  str(hashlib.sha1( str.encode(config["nanoWriMoSecretKey"] + config["nanoWriMoUsername"] + theWordCount) ).hexdigest() )

		payload = {
			'hash': theHash,
			'username': config["nanoWriMoUsername"],
			'wordcount': theWordCount
		}
		print("* Connecting to " + nanoAPIUrlUpdateWordCount)
		print( payload )
		requestResult = requests.put( nanoAPIUrlUpdateWordCount, data=payload )

		print( "Request Result" + str(requestResult) )


def preProcess(writeFile = False):
	if os.path.isdir(exportDirectory) == False:
		os.mkdir( exportDirectory )
	manuscriptContents = ""
	for root, dirs, files in sorted(os.walk( manuscriptDir )):
		path = root.split('/')
		for file in sorted(files):
			if file[0] != ".":
				with open(manuscriptDir + "/" + os.path.basename(root) + "/" + file , 'r', encoding="utf8") as content_file:
					# get file contents
					fileContents = content_file.read()

					fileContents = normalizeMarkDown( fileContents )
					# add an md HR at the end of the file
					manuscriptContents += fileContents + "\n\n----\n\n"
		# remove final "\n\n----\n\n"
		if manuscriptContents.endswith("\n\n----\n\n"):
			manuscriptContents = manuscriptContents[:-len("\n\n----\n\n")]
			manuscriptContents += "\n\n"


	# save contents
	if writeFile:
		with open("./temp_work_file.md" , 'w', encoding="utf8") as working_file:
			working_file.write( manuscriptContents )

	return manuscriptContents

def createBookMetaData():
	if recreateEPUBAndTempFiles == True:
		fileContents = "---\n"
		fileContents += "title: " + config["bookName"] + "\n"
		fileContents += "author: " + config["authorName"] + "\n"
		fileContents += "rights:  " + config["copyRight"] + "\n"
		fileContents += "language: " + config["languageCode"] + "\n"
		fileContents += "publisher: " + config["publisherName"] + "\n"
		if "coverImage" in config and config["coverImage"] != "":
			fileContents += "cover-image: " + config["coverImage"] + "\n"
		fileContents += "...\n"
		with open("./" + "00-ebook-info.txt" , 'w', encoding="utf8") as metaFile:
			metaFile.write( fileContents )

def removeTempFiles():
	if os.path.isfile("./temp_work_file.md"):
		os.remove( "./temp_work_file.md" )
	if os.path.isfile("./" + "00-ebook-info.txt"):
		os.remove( "./" + "00-ebook-info.txt" )
	tmpPDFConv = glob("tex2pdf.*")
	for tmpDir in tmpPDFConv:
		os.rmdir( tmpDir )



def saveProgress():
	global todaysProgress
	if os.path.isdir( progressDirectory ) == False:
		os.mkdir( progressDirectory )
	manuscriptData = preProcess()
	manuscriptData = normalizeMarkDown( manuscriptData )
	currentWordCount = len(manuscriptData.split())
	wordCountDict = {}
	if os.path.isfile( progressDirectory + "/progress.tsv"):
		with open( progressDirectory + "/progress.tsv" , 'r', encoding="utf8") as content_file:
			# get file contents
			for line in content_file:
				entryDate, wordCount = map(str, line.strip().split('\t') )
				wordCountDict[entryDate] = wordCount

	wordCountDict[ str( datetime.date.today())] = currentWordCount

	lastCount = 0
	for entryDate in sorted(wordCountDict.keys()):
		if str(datetime.date.today()) == entryDate:
			todaysProgress = int(wordCountDict[ entryDate ]) - lastCount
		lastCount = int(wordCountDict[ entryDate ])

	with open( progressDirectory + "/progress.tsv" , 'w', encoding="utf8") as content_file:
		for entryDate in sorted(wordCountDict.keys()):
			content_file.write( str(entryDate) + "\t" + str(wordCountDict[entryDate]) + "\n")

	if foundMatPlotLib:

		#Create Overall Progress Graph
		graphX = []
		graphY = []

		for entryDate in sorted(wordCountDict.keys()):
			graphX.append(entryDate)
			graphY.append( int(wordCountDict[ entryDate ]) )

		overallGraphNumCols = len(graphX)
		overallGraphLocations = np.arange(overallGraphNumCols)  # the x locations for the groups
		overallGraphBarWidth = 0.37       # the width of the bars

		overallGraphFig, overallGraphAX = plt.subplots()
		figureWidth = (len(graphX) / 10 * 3)
		if figureWidth < 10:
			figureWidth = 10
		overallGraphFig.set_size_inches(figureWidth, 5)

		rects1 = overallGraphAX.bar(overallGraphLocations, graphY, overallGraphBarWidth, color='r')

		# add some text for labels, title and axes ticks
		overallGraphAX.set_ylabel('Word Count')
		overallGraphAX.set_title('Overall Word Count Progress for "' + config["bookName"] + '"' )
		overallGraphAX.set_xticks(overallGraphLocations + overallGraphBarWidth)
		overallGraphAX.set_xticklabels(graphX,  ha='center', rotation=90 )

		overallGraphRects = overallGraphAX.patches

		for overallRect, overallLabel in zip(overallGraphRects, graphY):
		    labelHeight = overallRect.get_height()
		    overallGraphAX.text(overallRect.get_x() + overallRect.get_width()/2, labelHeight + 10, overallLabel, ha='center', va='bottom', rotation=90 )

		plt.savefig(progressDirectory + "/progress-overall.png", bbox_inches='tight', dpi=300)

		overallGraphFig.clf()
		plt.clf()

		#Create Daily Progress Graph
		graphX = []
		graphY = []



		lastCount = 0
		for entryDate in sorted(wordCountDict.keys()):
			graphX.append(entryDate)
			graphY.append( int(wordCountDict[ entryDate ]) - lastCount )
			lastCount = int(wordCountDict[ entryDate ])

		dailyGraphNumCols = len(graphX)
		dailyGraphLocations = np.arange(dailyGraphNumCols)  # the x locations for the groups
		dailyGraphWidth = 0.38 # the width of the bars

		dailyGraphFig, dailyGraphAX = plt.subplots()
		rects1 = dailyGraphAX.bar(dailyGraphLocations, graphY, dailyGraphWidth, color='r')

		figureWidth = (len(graphX) / 10 * 3)
		if figureWidth < 10:
			figureWidth = 10
		dailyGraphFig.set_size_inches( figureWidth, 5)

		# add some text for labels, title and axes ticks
		dailyGraphAX.set_ylabel('Word Count')
		dailyGraphAX.set_title('Daily Word Count Progress for "' + config["bookName"] + '"' )
		dailyGraphAX.set_xticks( dailyGraphLocations + dailyGraphWidth )
		dailyGraphAX.set_xticklabels(graphX,  ha='center', rotation=90 )

		dailyGraphRects = dailyGraphAX.patches

		for dailyRect, dailyLabel in zip(dailyGraphRects, graphY):
		    labelHeight = dailyRect.get_height()
		    dailyGraphAX.text(dailyRect.get_x() + dailyRect.get_width()/2, labelHeight + 10, dailyLabel, ha='center', va='bottom', rotation=90 )


		plt.savefig(progressDirectory + "/progress-daily.png", bbox_inches='tight', dpi=300)

		dailyGraphFig.clf()
		plt.clf()

def printHelp():
	print( "Usage:" )
	print( "	enovel-project init - create base directories and starter content - DANGER: this will overwrite your current content" )
	print( "	enovel-project all - creates a .mobi, .epub, .pdf, .txt, and .html from your manuscript then displays a wordcount" )
	print( "	enovel-project ebooks - create .mobi and .epub from your manuscript" )
	print( "	enovel-project pdf - creates a pdf from your manuscript" )
	print( "	enovel-project html - creates a html from your manuscript" )
	print( "	enovel-project text - creates a text file from your manuscript" )
	print( "	enovel-project wordcount - gives you a current wordcount of your manuscript" )

def directoryCount(path):
	dirCount = 0
	for root, dirs, files in os.walk(path):
		dirCount += len(dirs)

	return dirCount

def newChapter( chapterNumber = 0 ):
	if chapterNumber == 1:
		chapterName = "Your first Chapter"
	else:
		chapterName = "New Chapter"

	if os.path.isdir("./Manuscript") == False:
		os.mkdir( "./Manuscript" )

	if chapterNumber == 0:
		chapterNumber = directoryCount( "./Manuscript" ) + 1


	if os.path.isdir("./Manuscript/Chapter " + str(chapterNumber) + " - " + chapterName + "/") == False:
		os.mkdir( "./Manuscript/Chapter " + str(chapterNumber) + " - " + chapterName + "/" )

	chapterHeading = "\\\\newpage\n\n"
	chapterHeading += "#Chapter " + str(chapterNumber) + " - " + chapterName + "\n\n"
	if os.path.isfile("./Manuscript/Chapter " + str(chapterNumber) + " - " + chapterName + "/00 - Chapter Header.md") == False:
		with open("./Manuscript/Chapter " + str(chapterNumber) + " - " + chapterName + "/00 - Chapter Header.md" , 'w', encoding="utf8") as chapterHeaderFile:
			chapterHeaderFile.write( chapterHeading )

	firstScene = "Your book starts here!\n\n"
	firstScene += "Your second paragraph\n"

	if os.path.isfile("./Manuscript/Chapter " + str(chapterNumber) + " - " + chapterName + "/01 - Setting the stage.md") == False:
		with open("./Manuscript/Chapter " + str(chapterNumber) + " - " + chapterName + "/01 - Setting the stage.md" , 'w', encoding="utf8") as firstSceneFile:
			firstSceneFile.write( firstScene )

def initProject():
	newChapter(1)

	if os.path.isdir("./Bios") == False:
		os.mkdir( "./Bios" )
	if os.path.isdir("./Scenes") == False:
		os.mkdir( "./Scenes" )
	if os.path.isdir("./Notes") == False:
		os.mkdir( "./Notes" )
	if os.path.isdir(exportDirectory) == False:
		os.mkdir( exportDirectory )

	exampleCharacter = "#New Character Name\n\n##Role\n\nCharacter's role in the story\n\n##Description\n\nPhysical and mental description of the character."
	if os.path.isfile("./Bios/Example Character.md") == False:
		with open("./Bios/Example Character.md" , 'w', encoding="utf8") as exampleBioFile:
			exampleBioFile.write( exampleCharacter )

	exampleScene = "#New Location Name\n\n##Role\n\nScene's's role in the story\n\n##Description\n\nPhysical and mental description of the scene."
	if os.path.isfile("./Scenes/Example Scene.md") == False:
		with open("./Scenes/Example Scene.md" , 'w', encoding="utf8") as exampleSceneFile:
			exampleSceneFile.write( exampleScene )


def createEPUB():
	global recreateEPUBAndTempFiles
	#Requires SYSCALL to pandoc
	if os.path.isfile('./" + exportDirectory + "/" + config["bookFile"] + ".epub') == False and recreateEPUBAndTempFiles == True:
		createBookMetaData()
		preProcess( writeFile = True )
		os.system("pandoc -S -o \"" + exportDirectory + "/" + config["bookFile"] + ".epub\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
		recreateEPUBAndTempFiles = False
		print("* " + exportDirectory + "/" + config["bookFile"] + ".epub created")

def createTXT():
	#Requires SYSCALL to pandoc
	os.system("pandoc -t plain \"" + exportDirectory + "/" + config["bookFile"] + ".epub\" -o \"" + exportDirectory + "/" + config["bookFile"] + ".txt\"")
	print("* " + exportDirectory + "/" + config["bookFile"] + ".txt created")

def createHTML():
	#Requires SYSCALL to pandoc
	createBookMetaData()
	preProcess( writeFile = True )
	os.system("pandoc -s -S -o \"" + exportDirectory + "/" + config["bookFile"] + ".html\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
	print("* " + exportDirectory + "/" + config["bookFile"] + ".html created")


def createMOBI():
	#Requires SYSCALL to pandoc
	#Requires SYSCALL to calibre tools
	createEPUB()
	os.system("ebook-convert \"" + exportDirectory + "/" + config["bookFile"] + ".epub\" \"" + exportDirectory + "/" + config["bookFile"] + ".mobi\" > \"" + config["bookFile"] + ".convert.log\"")
	print("* " + exportDirectory + "/" + config["bookFile"] + ".mobi created")
	if os.path.isfile( config["bookFile"] + ".convert.log" ):
		os.remove( config["bookFile"] + ".convert.log" )

def createMD():
	copyfile( "./temp_work_file.md", exportDirectory + "/" + config["bookFile"] + ".md" )
	print("* " + exportDirectory + "/" + config["bookFile"] + ".md created")


def createPDF():
	#Requires SYSCALL to pandoc
	createBookMetaData()
	preProcess( writeFile = True )
	os.system("pandoc -S -o \"" + exportDirectory + "/" + config["bookFile"] + ".pdf\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
	print("* " + exportDirectory + "/" + config["bookFile"] + ".pdf created")


def wordCount():
	manuscriptData = preProcess()
	manuscriptData = normalizeMarkDown( manuscriptData )
	print("    Project Wordcount: " + str(len(manuscriptData.split())))
	print("     Today's Progress: " + str(todaysProgress) )

if len(sys.argv) > 1:
	for arg in sys.argv:
		if arg == "init":
			initProject()
		elif arg == "all":
			saveProgress()
			createEPUB()
			createMOBI()
			createHTML()
			createTXT()
			createPDF()
			createMD()
			wordCount()
		elif arg == "ebooks":
			saveProgress()
			createEPUB()
			createMOBI()
		elif arg == "mobi":
			saveProgress()
			createMOBI()
		elif arg == "epub":
			saveProgress()
			createEPUB()
		elif arg == "pdf":
			saveProgress()
			createPDF()
		elif arg == "md":
			saveProgress()
			createMD()
		elif arg == "markdown":
			saveProgress()
			createMD()
		elif arg == "nc":
			newChapter()
		elif arg == "newchapter":
			newChapter()
		elif arg == "chapter":
			newChapter()
		elif arg == "html":
			saveProgress()
			createHTML()
		elif arg == "txt":
			saveProgress()
			createTXT()
		elif arg == "text":
			saveProgress()
			createTXT()
		elif arg == "wordcount":
			# saveProgress()
			wordCount()
		elif arg == "nano":
			updateNaNo()
		elif arg == __file__:
			# Do Nothing
			pass
		else:
			print("Warning unknown argument '" + arg + "'");
			printHelp()
	removeTempFiles()

else:
	printHelp()

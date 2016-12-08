#!/usr/bin/python
import os
import sys

import yaml

# Initial Config - this will create a config.yml file to modify
config = dict(
	bookName = "My Ebook",
	bookFile = "My Ebook",
	authorName = "Author Name",
	copyRight = "2016 All rights reserved",
	languageCode = "en-US",
	publisherName = "Self Published",
	coverImage = ""
)

if os.path.isfile("config.yml") == False:
	with open('config.yml', 'w') as outfile:
		yaml.dump(config, outfile, default_flow_style=False)
else:
	config = yaml.safe_load(open("config.yml"))

# Immutable Variables
manuscriptDir = "./Manuscript"

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

def preProcess(writeFile = False):
    #global manuscriptDir
    manuscriptContents = ""
    for root, dirs, files in sorted(os.walk( manuscriptDir )):
        path = root.split('/')
        for file in sorted(files):
            with open(manuscriptDir + "/" + os.path.basename(root) + "/" + file , 'r') as content_file:
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
        with open("./temp_work_file.md" , 'w') as working_file:
            working_file.write( manuscriptContents )

    return manuscriptContents

def createBookMetaData():
    fileContents = "---\n"
    fileContents += "title: " + config["bookName"] + "\n"
    fileContents += "author: " + config["authorName"] + "\n"
    fileContents += "rights:  " + config["copyRight"] + "\n"
    fileContents += "language: " + config["languageCode"] + "\n"
    fileContents += "publisher: " + config["publisherName"] + "\n"
    if config["coverImage"] != "":
        fileContents += "cover-image: " + config["coverImage"] + "\n"
    fileContents += "...\n"
    with open("./" + "00-" + config["bookFile"] + "-info.txt" , 'w') as metaFile:
        metaFile.write( fileContents )

def removeTempFiles():
    if os.path.isfile("./temp_work_file.md"):
        os.remove( "./temp_work_file.md" )
    if os.path.isfile("./" + "00-" + config["bookFile"] + "-info.txt"):
        os.remove( "./" + "00-" + config["bookFile"] + "-info.txt" )

def printHelp():
	print( "Usage:" )
	print( "	enovel-project init - create base directories and starter content - DANGER: this will overwrite your current content" )
	print( "	enovel-project requirements - for Ubuntu users: installs calibre and pandoc" )
	print( "	enovel-project ebooks - create .mobi and .epub from your manuscript" )
	print( "	enovel-project pdf - creates a pdf from your manuscript" )
	print( "	enovel-project wordcount - gives you a current wordcount of your manuscript" )

def initProject():
    if os.path.isdir("./Manuscript") == False:
        os.mkdir( "./Manuscript" )
    if os.path.isdir("./Manuscript/Chapter 1 - Your first Chapter/") == False:
        os.mkdir( "./Manuscript/Chapter 1 - Your first Chapter/" )

    chapterHeading = "\\\\newpage\n\n"
    chapterHeading += "#Chapter 1 - Your first Chapter\n\n"
    if os.path.isfile("./Manuscript/Chapter 1 - Your first Chapter/00 - Chapter Header.md") == False:
        with open("./Manuscript/Chapter 1 - Your first Chapter/00 - Chapter Header.md" , 'w') as chapterHeaderFile:
            chapterHeaderFile.write( chapterHeading )

    firstScene = "Your book starts here!\n\n"
    firstScene += "Your second paragraph\n"

    if os.path.isfile("./Manuscript/Chapter 1 - Your first Chapter/01 - Setting the stage.md") == False:
        with open("./Manuscript/Chapter 1 - Your first Chapter/01 - Setting the stage.md" , 'w') as firstSceneFile:
            firstSceneFile.write( firstScene )

    if os.path.isdir("./Bios") == False:
        os.mkdir( "./Bios" )
    if os.path.isdir("./Scenes") == False:
        os.mkdir( "./Scenes" )
    if os.path.isdir("./Notes") == False:
        os.mkdir( "./Notes" )

def createEPUB():
    #Requires SYSCALL to pandoc
    createBookMetaData()
    preProcess( writeFile = True )
    os.system("pandoc -S -o \"" + config["bookFile"] + ".epub\" \"00-" + config["bookFile"] + "-info.txt\" \"temp_work_file.md\"")
    removeTempFiles()

def createTXT():
    #Requires SYSCALL to pandoc
    createEPUB()
    os.system("pandoc -t plain \"" + config["bookFile"] + ".epub\" -o \"" + config["bookFile"] + ".txt\"")

def createHTML():
    #Requires SYSCALL to pandoc
    createBookMetaData()
    preProcess( writeFile = True )
    os.system("pandoc -s -S -o \"" + config["bookFile"] + ".html\" \"00-" + config["bookFile"] + "-info.txt\" \"temp_work_file.md\"")
    removeTempFiles()

def createMOBI():
    #Requires SYSCALL to pandoc
    #Requires SYSCALL to calibre tools
    createEPUB()
    os.system("ebook-convert \"" + config["bookFile"] + ".epub\" \"" + config["bookFile"] + ".mobi\" > \"" + config["bookFile"] + ".convert.log\"")
    if os.path.isfile( config["bookFile"] + ".convert.log" ):
        os.remove( config["bookFile"] + ".convert.log" )


def createPDF():
    #Requires SYSCALL to pandoc
    createBookMetaData()
    preProcess( writeFile = True )
    os.system("pandoc -S -o \"" + config["bookFile"] + ".pdf\" \"00-" + config["bookFile"] + "-info.txt\" \"temp_work_file.md\"")
    removeTempFiles()

def wordCount():
    manuscriptData = preProcess()
    manuscriptData = normalizeMarkDown( manuscriptData )
    print "Wordcount: " + str(len(manuscriptData.split()))

if len(sys.argv) == 2:
    if sys.argv[1] == "init":
        initProject()
    elif sys.argv[1] == "ebooks":
        createEPUB()
        createMOBI()
    elif sys.argv[1] == "pdf":
        createPDF()
    elif sys.argv[1] == "html":
        createHTML()
    elif sys.argv[1] == "txt":
        createTXT()
    elif sys.argv[1] == "text":
        createTXT()
    elif sys.argv[1] == "wordcount":
        wordCount()
    else:
        printHelp()
else:
    printHelp()

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
import xmltodict

__author__ = "Jeffrey D. Gordon"
__copyright__ = "Copyright 2016-2017, Jeffrey D. Gordon"
__credits__ = ["Jeffrey D. Gordon"]
__license__ = "GPL"
__version__ = "0.8.5"
__maintainer__ = "Jeffrey D. Gordon"
__email__ = "jeff@jdgwf.com"
__status__ = "Development"

# Configurable Options (not really recommended)
export_directory = "./Exports"
manuscript_dir = "./Manuscript"
progressDirectory = "./Progress"

# Initial Config - this will create a config.yml file to modify
todaysProgress = 0
recreate_epub_and_temp_files = True

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


# To get NanoWrioSecret go to https://nanowrimo.org/api/word_count while logged in.
if "nanoWriMoSecretKey" not in config:
    config["nanoWriMoSecretKey"] = ""

if "nanoWriMoUsername" not in config:
    config["nanoWriMoUsername"] = ""

try:
    imp.find_module('numpy')
    imp.find_module('matplotlib')
    found_matplotlib = True
except ImportError:
    found_matplotlib = False

if found_matplotlib:
    import numpy as np
    import matplotlib.pyplot as plt

# Immutable Variables
nano_api_url_current_word_count = "https://nanowrimo.org/wordcount_api/wc/" + config["nanoWriMoUsername"]
nano_api_url_current_word_count_history = "https://nanowrimo.org/modules/wordcount_api/wchistory/" + config["nanoWriMoUsername"]
nano_api_url_update_word_count = "https://nanowrimo.org/api/wordcount"

def normalize_markdown( file_contents ):
    # trim the contents
    file_contents = file_contents.strip()
    # remove existing markdown HRs
    file_contents = file_contents.replace( "----\n", "")
    file_contents = file_contents.replace( "\n----", "")
    file_contents = file_contents.replace( "---\n", "")
    file_contents = file_contents.replace( "\n---", "")

    # replace all triple newlines with double newlines (normalize any extras)
    file_contents = file_contents.replace( "\n\n\n", "\n\n")

    return file_contents

def updateNaNo():
    if config["nanoWriMoSecretKey"] and config["nanoWriMoUsername"]:

        manuscript_data = pre_process()
        manuscript_data = normalize_markdown( manuscript_data )
        theword_count = len(manuscript_data.split())

        the_hash =  str(hashlib.sha1( str.encode(config["nanoWriMoSecretKey"] + config["nanoWriMoUsername"] + str(theword_count)) ).hexdigest() )

        payload = {
            'hash': the_hash,
            'name': config["nanoWriMoUsername"],
            'wordcount': theword_count
        }

        print("* Updating NaNoWriMo update count (currently " + str(theword_count) + ")... Connecting to " + nano_api_url_update_word_count)

        request_result = requests.put( nano_api_url_update_word_count, data=payload )

        current_word_count_response = requests.get( nano_api_url_current_word_count )
        current_word_count = xmltodict.parse(current_word_count_response.text)


        if int( current_word_count["wc"]["user_wordcount"]) == theword_count:
            print( "* SUCCESS! NaNoWriMo count matches current count")
        else:
            print( "ERROR: NaNoWriMo count does NOT match your current count after update - check your NaNoWriMo secret and username", current_word_count["wc"]["user_wordcount"], theword_count)
        #~ if request_result.status_code == 200:
            #~ print("* NanoWriMo.org responded positive (status code 200). Your word might have been updated.")
            #~ return True
        #~ else:
            #~ print("* NanoWriMo.org responded NEGATIVE. Your word count was not updated")
            #~ return False
    else:
        print("ERROR: Cannot update NaNoWriMo counts - no configuration.")
        print("* Be sure to set your nanoWriMoSecretKey and nanoWriMoUsername in your config.yml.")


def pre_process(writeFile = False):
    if os.path.isdir(export_directory) == False:
        os.mkdir( export_directory )
    manuscript_contents = ""
    for root, dirs, files in sorted(os.walk( manuscript_dir )):
        path = root.split('/')
        for file in sorted(files):
            if file[0] != ".":
                with open(manuscript_dir + "/" + os.path.basename(root) + "/" + file , 'r', encoding="utf8") as content_file:
                    # get file contents
                    file_contents = content_file.read()

                    file_contents = normalize_markdown( file_contents )
                    # add an md HR at the end of the file
                    manuscript_contents += file_contents + "\n\n----\n\n"
        # remove final "\n\n----\n\n"
        if manuscript_contents.endswith("\n\n----\n\n"):
            manuscript_contents = manuscript_contents[:-len("\n\n----\n\n")]
            manuscript_contents += "\n\n"


    # save contents
    if writeFile:
        with open("./temp_work_file.md" , 'w', encoding="utf8") as working_file:
            working_file.write( manuscript_contents )

    return manuscript_contents

def create_book_metadata():
    if recreate_epub_and_temp_files == True:
        file_contents = "---\n"
        file_contents += "title: " + config["bookName"] + "\n"
        file_contents += "author: " + config["authorName"] + "\n"
        file_contents += "rights:  " + config["copyRight"] + "\n"
        file_contents += "language: " + config["languageCode"] + "\n"
        file_contents += "geometry: margin=3cm\n"
        file_contents += "fontsize: 12pt\n"
        file_contents += "publisher: " + config["publisherName"] + "\n"
        if "coverImage" in config and config["coverImage"] != "":
            file_contents += "cover-image: " + config["coverImage"] + "\n"
        file_contents += "...\n"
        with open("./" + "00-ebook-info.txt" , 'w', encoding="utf8") as meta_file:
            meta_file.write( file_contents )

def remove_temp_files():
    if os.path.isfile("./temp_work_file.md"):
        os.remove( "./temp_work_file.md" )
    if os.path.isfile("./" + "00-ebook-info.txt"):
        os.remove( "./" + "00-ebook-info.txt" )
    tmp_pdf_conv = glob("tex2pdf.*")
    for tmp_dir in tmp_pdf_conv:
        os.rmdir( tmp_dir )



def save_progress():
    global todaysProgress
    if os.path.isdir( progressDirectory ) == False:
        os.mkdir( progressDirectory )
    manuscript_data = pre_process()
    manuscript_data = normalize_markdown( manuscript_data )
    currentword_count = len(manuscript_data.split())
    word_count_dict = {}
    if os.path.isfile( progressDirectory + "/progress.tsv"):
        with open( progressDirectory + "/progress.tsv" , 'r', encoding="utf8") as content_file:
            # get file contents
            for line in content_file:
                entryDate, word_count = map(str, line.strip().split('\t') )
                word_count_dict[entryDate] = word_count

    word_count_dict[ str( datetime.date.today())] = currentword_count

    lastCount = 0
    for entryDate in sorted(word_count_dict.keys()):
        if str(datetime.date.today()) == entryDate:
            todaysProgress = int(word_count_dict[ entryDate ]) - lastCount
        lastCount = int(word_count_dict[ entryDate ])

    with open( progressDirectory + "/progress.tsv" , 'w', encoding="utf8") as content_file:
        for entryDate in sorted(word_count_dict.keys()):
            content_file.write( str(entryDate) + "\t" + str(word_count_dict[entryDate]) + "\n")

    if found_matplotlib:

        #Create Overall Progress Graph
        graphX = []
        graphY = []

        for entryDate in sorted(word_count_dict.keys()):
            graphX.append(entryDate)
            graphY.append( int(word_count_dict[ entryDate ]) )

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
        for entryDate in sorted(word_count_dict.keys()):
            graphX.append(entryDate)
            graphY.append( int(word_count_dict[ entryDate ]) - lastCount )
            lastCount = int(word_count_dict[ entryDate ])

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

def print_help():
    print( "Usage:" )
    print( "    enovel-project init        Creates the base directories and starter content")
    print("                    DANGER: this will overwrite your current content" )
    print( "    enovel-project all         Creates a .mobi, .epub, .pdf, .txt, and .html from your")
    print("                    manuscript then displays a word_count" )
    print( "    enovel-project ebooks       Create .mobi and .epub from your manuscript" )
    print( "    enovel-project pdf          Creates a .pdf from your manuscript" )
    print( "    enovel-project mobi         Creates a .mobi from your manuscript" )
    print( "    enovel-project epub         Creates an .epub from your manuscript" )
    print( "    enovel-project html         Creates a .html from your manuscript" )
    print( "    enovel-project text         Creates a .txt file from your manuscript" )
    print( "    enovel-project rtf          Creates a .rtf (Rich Text Format)")
    print( "                                file from your manuscript" )
    print( "    enovel-project md           Creates a .md (MarkDown) file from")
    print( "                                your manuscript" )
    print( "    enovel-project chapter      Creates a new chapter template in")
    print( "                                your manuscript folder" )
    print( "    enovel-project nc           Alias to enovel-project chapter" )
    print( "    enovel-project newchapter   Alias to enovel-project chapter" )
    print( "    enovel-project word_count    Gives you a current word_count of your manuscript" )
    print( "    enovel-project wc           Alias to enovel-project word_count" )
    print( "    enovel-project nano         If your nanowrimo username and secret is in")
    print("                                the config, this will attempt to update your ")
    print("                                nanowrimo daily stat automatically." )

def directoryCount(path):
    dir_count = 0
    for root, dirs, files in os.walk(path):
        dir_count += len(dirs)

    return dir_count

def newChapter( chapter_number = 0 ):
    if chapter_number == 1:
        chapter_name = "Your first Chapter"
    else:
        chapter_name = "New Chapter"

    if os.path.isdir("./Manuscript") == False:
        os.mkdir( "./Manuscript" )

    if chapter_number == 0:
        chapter_number = directoryCount( "./Manuscript" ) + 1


    if os.path.isdir("./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/") == False:
        os.mkdir( "./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/" )

    chapter_heading = "\\newpage\n\n"
    chapter_heading += "# Chapter " + str(chapter_number) + " - " + chapter_name + "\n\n"
    if os.path.isfile("./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/00 - Chapter Header.md") == False:
        with open("./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/00 - Chapter Header.md" , 'w', encoding="utf8") as chapterHeaderFile:
            chapterHeaderFile.write( chapter_heading )

    first_scene = "Your book starts here!\n\n"
    first_scene += "Your second paragraph\n"

    if os.path.isfile("./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/01 - Setting the stage.md") == False:
        with open("./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/01 - Setting the stage.md" , 'w', encoding="utf8") as first_scene_file:
            first_scene_file.write( first_scene )

    print("* Added new chapter directory: " + "Chapter " + str(chapter_number) + " - " + chapter_name + "")

def initProject():
    newChapter(1)

    if os.path.isdir("./Bios") == False:
        os.mkdir( "./Bios" )
    if os.path.isdir("./Scenes") == False:
        os.mkdir( "./Scenes" )
    if os.path.isdir("./Notes") == False:
        os.mkdir( "./Notes" )
    if os.path.isdir(export_directory) == False:
        os.mkdir( export_directory )

    exampleCharacter = "# New Character Name\n\n## Role\n\nCharacter's role in the story\n\n## Description\n\nPhysical and mental description of the character."
    if os.path.isfile("./Bios/Example Character.md") == False:
        with open("./Bios/Example Character.md" , 'w', encoding="utf8") as example_bio_file:
            example_bio_file.write( exampleCharacter )

    exampleScene = "# New Location Name\n\n## Role\n\nScene's's role in the story\n\n## Description\n\nPhysical and mental description of the scene."
    if os.path.isfile("./Scenes/Example Scene.md") == False:
        with open("./Scenes/Example Scene.md" , 'w', encoding="utf8") as example_scene_file:
            example_scene_file.write( exampleScene )


def create_epub():
    global recreate_epub_and_temp_files
    #Requires SYSCALL to pandoc
    if os.path.isfile('./" + export_directory + "/" + config["bookFile"] + ".epub') == False and recreate_epub_and_temp_files == True:
        create_book_metadata()
        pre_process( writeFile = True )
        os.system("pandoc -S -o \"" + export_directory + "/" + config["bookFile"] + ".epub\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
        recreate_epub_and_temp_files = False
        print("* " + export_directory + "/" + config["bookFile"] + ".epub created")

def create_txt():
    #Requires SYSCALL to pandoc
    os.system("pandoc -t plain \"" + export_directory + "/" + config["bookFile"] + ".epub\" -o \"" + export_directory + "/" + config["bookFile"] + ".txt\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".txt created")

def create_html():
    #Requires SYSCALL to pandoc
    create_book_metadata()
    pre_process( writeFile = True )
    os.system("pandoc -s -S -o \"" + export_directory + "/" + config["bookFile"] + ".html\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".html created")


def create_mobi():
    #Requires SYSCALL to pandoc
    #Requires SYSCALL to calibre tools
    create_epub()
    os.system("ebook-convert \"" + export_directory + "/" + config["bookFile"] + ".epub\" \"" + export_directory + "/" + config["bookFile"] + ".mobi\" > \"" + config["bookFile"] + ".convert.log\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".mobi created")
    if os.path.isfile( config["bookFile"] + ".convert.log" ):
        os.remove( config["bookFile"] + ".convert.log" )

def create_md():
    global recreate_epub_and_temp_files
    #Requires SYSCALL to pandoc
    if os.path.isfile('./" + export_directory + "/" + config["bookFile"] + ".epub') == False and recreate_epub_and_temp_files == True:
        create_book_metadata()
        pre_process( writeFile = True )
        copyfile( "./temp_work_file.md", export_directory + "/" + config["bookFile"] + ".md" )
        print("* " + export_directory + "/" + config["bookFile"] + ".md created")
        recreate_epub_and_temp_files = False




def create_pdf():
    #Requires SYSCALL to pandoc
    create_book_metadata()
    pre_process( writeFile = True )
    os.system("pandoc -V fontsize=12pt -S -o \"" + export_directory + "/" + config["bookFile"] + ".pdf\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".pdf created")

def create_doc():
    #Requires SYSCALL to pandoc
    create_book_metadata()
    pre_process( writeFile = True )
    os.system("pandoc -s -S -o \"" + export_directory + "/" + config["bookFile"] + ".doc\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".doc created")

def create_docx():
    #Requires SYSCALL to pandoc
    create_book_metadata()
    pre_process( writeFile = True )
    os.system("pandoc -s -S -o \"" + export_directory + "/" + config["bookFile"] + ".docx\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".docx created")


def word_count():
    manuscript_data = pre_process()
    manuscript_data = normalize_markdown( manuscript_data )
    print("    Project word_count: " + str(len(manuscript_data.split())))
    print("     Today's Progress: " + str(todaysProgress) )

if len(sys.argv) > 1:
    for arg in sys.argv:
        if arg == "init":
            initProject()
        elif arg == "all":
            save_progress()
            create_epub()
            create_mobi()
            create_html()
            create_txt()
            create_pdf()
            create_md()
            create_doc()
            create_docx()
            word_count()
        elif arg == "ebooks":
            save_progress()
            create_epub()
            create_mobi()
        elif arg == "mobi":
            save_progress()
            create_mobi()
        elif arg == "epub":
            save_progress()
            create_epub()
        elif arg == "pdf":
            save_progress()
            create_pdf()
        elif arg == "doc":
            save_progress()
            create_doc()
        elif arg == "docx":
            save_progress()
            create_docx()
        elif arg == "md":
            save_progress()
            create_md()
        elif arg == "markdown":
            save_progress()
            create_md()
        elif arg == "html":
            save_progress()
            create_html()
        elif arg == "txt":
            save_progress()
            create_txt()
        elif arg == "text":
            save_progress()
            create_txt()
        elif arg == "word_count":
            save_progress()
            word_count()
        elif arg == "wc":
            save_progress()
            word_count()
        elif arg == "nano":
            updateNaNo()
        elif arg == "nc":
            newChapter()
        elif arg == "newchapter":
            newChapter()
        elif arg == "chapter":
            newChapter()
        elif arg == __file__:
            # Do Nothing
            pass
        else:
            print("Warning unknown argument '" + arg + "'");
            print_help()
    remove_temp_files()

else:
    print_help()

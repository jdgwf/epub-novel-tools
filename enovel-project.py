#!/usr/bin/env python3

"""Sets up a series of directories and MarkDown compilation tools for Novel E-Book novel
creation on Linux (tested on Ubuntu 16.04 and 16.10, should work on and Debian too).
Provides word count functions and history tracking.

Find this at: https://github.com/jdgwf/epub-novel-tools
"""

import os
import sys
from glob import glob
from shutil import copyfile
import yaml
import csv
import datetime
import importlib
import hashlib
import requests
import xmltodict

__author__ = "Jeffrey D. Gordon"
__copyright__ = "Copyright 2016-2017, Jeffrey D. Gordon"
__credits__ = ["Jeffrey D. Gordon"]
__license__ = "GPL"
__version__ = "0.9.5"
__maintainer__ = "Jeffrey D. Gordon"
__email__ = "jeff@jdgwf.com"
__status__ = "Development"

_debug = False

# Configurable Options (not really recommended)
export_directory = "./Exports"
manuscript_dir = "./Manuscript"
progress_directory = "./Progress"

default_pdf_font_size = "12pt" # latex only supports 10pt, 11pt, and 12pt

pandoc_markdown_arg = ""

# Initial Config - this will create a config.yml file to modify
todays_progress = 0
recreate_epub_and_temp_files = True

config = dict(
    bookName = "My Ebook",
    bookFile = "My Ebook",
    authorName = "Author Name",
    copyRight = str(datetime.datetime.now().year) + " All rights reserved",
    languageCode = "en-US",
    publisherName = "Self Published",
    pdfFontSize = default_pdf_font_size,
    coverImage = "",
    nanoWriMoSecretKey = "",
    nanoWriMoUsername = "",
    wordCountOffset = 0,
    replacements = {},
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

if "wordCountOffset" not in config:
    config["wordCountOffset"] = 0

if "pdfFontSize" not in config:
    config["pdfFontSize"] = default_pdf_font_size

try:
    importlib.util.find_spec('numpy')
    importlib.util.find_spec('matplotlib')

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

def _set_pandoc_args():
    global pandoc_markdown_arg

    if pandoc_markdown_arg == "":
        # For pandoc 2+
        # pandoc_markdown_arg = "-f markdown+smart"

        # For pandoc 1.19.2.4
        # pandoc_markdown_arg = "-S"

        version_return = os.popen("pandoc --version").read()
        # print("v", version_return)
        version_return_lines = version_return.split("\n")
        if version_return_lines[0].find("pandoc 1.1") == 0:
            pandoc_markdown_arg = "-S"
            if _debug:
                print( "* Detected " + version_return_lines[0] + ". Setting markdown arg to '" + pandoc_markdown_arg + "'")

        if version_return_lines[0].find("pandoc 2.") == 0:
            pandoc_markdown_arg = "-f markdown+smart"
            if _debug:
                print( "* Detected " + version_return_lines[0] + ". Setting markdown arg to ''" + pandoc_markdown_arg + "'")


def watch():
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    global current_word_count, start_word_count


    save_progress()

    current_word_count = word_count()
    start_word_count = int(current_word_count)
    class Watcher:
        DIRECTORY_TO_WATCH = manuscript_dir

        def __init__(self):
            self.observer = Observer()

        def run(self):
            event_handler = Handler()
            self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
            self.observer.start()
            try:
                while True:
                    time.sleep(5)
            except:
                self.observer.stop()
                # print("Error")

            self.observer.join()


    class Handler(FileSystemEventHandler):

        @staticmethod
        def on_any_event(event):
            global current_word_count, start_word_count
            if event.is_directory:
                return None

            elif event.event_type == 'created':
                # Take any action here when a file is first created.

                print("---------- Watch Event @ " + datetime.datetime.now().strftime("%H:%M:%S") + " ----------------")
                print("* Received created event - %s." % event.src_path)

            elif event.event_type == 'modified':
                # Taken any action here when a file is modified.
                print("---------- Watch Event @ " + datetime.datetime.now().strftime("%H:%M:%S") + " ----------------")
                print("* Received modified event - %s." % event.src_path)
            new_word_count = word_count()
            save_progress(True)

            print("* Words writting since start: " + str(new_word_count - start_word_count) )
            print("* Words writting since last save: " + str(new_word_count - current_word_count) )
            current_word_count = new_word_count
    w = Watcher()
    print("* Press Control-C to stop watching")
    w.run()


def apply_replacements( file_contents ):
    if config["replacements"]:
        for replace_value in config["replacements"]:
            replace_with = config["replacements"][replace_value]
            file_contents = file_contents.replace( replace_value, replace_with )
    return file_contents


def normalize_markdown( file_contents ):

    file_contents = apply_replacements( file_contents)

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
        theword_count = len(manuscript_data.split()) - config["wordCountOffset"]

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
            if file.endswith(".md"):
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

def pre_process_chapters(writeFile = False):
    if os.path.isdir(export_directory) == False:
        os.mkdir( export_directory )
    chapters_manuscript_contents = {}
    for root, dirs, files in sorted(os.walk( manuscript_dir )):
        path = root.split('/')
        for file in sorted(files):
            if file.endswith(".md"):

                if os.path.basename(root) not in chapters_manuscript_contents:
                    chapters_manuscript_contents[ os.path.basename(root) ] = ""

                with open(manuscript_dir + "/" + os.path.basename(root) + "/" + file , 'r', encoding="utf8") as content_file:
                    # get file contents
                    file_contents = content_file.read()

                    file_contents = normalize_markdown( file_contents )
                    # add an md HR at the end of the file
                    chapters_manuscript_contents[ os.path.basename(root) ] += file_contents + "\n\n----\n\n"
                # remove final "\n\n----\n\n"
                if chapters_manuscript_contents[ os.path.basename(root) ].endswith("\n\n----\n\n"):
                    chapters_manuscript_contents[ os.path.basename(root) ] = chapters_manuscript_contents[ os.path.basename(root) ][:-len("\n\n----\n\n")]
                    chapters_manuscript_contents[ os.path.basename(root) ] += "\n\n"


    # save contents
    # if writeFile:
    #     with open("./temp_work_file.md" , 'w', encoding="utf8") as working_file:
    #         working_file.write( manuscript_contents )

    return chapters_manuscript_contents

def create_book_metadata():
    if recreate_epub_and_temp_files == True:
        file_contents = "---\n"
        file_contents += "title: " + config["bookName"] + "\n"
        file_contents += "author: " + config["authorName"] + "\n"
        file_contents += "rights:  " + config["copyRight"] + "\n"
        file_contents += "language: " + config["languageCode"] + "\n"
        file_contents += "geometry: margin=3cm\n"
        file_contents += "fontsize: " + config["pdfFontSize"] + "\n"
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



def save_progress( dont_draw_graphs = False):
    global todays_progress
    _set_pandoc_args()

    if os.path.isdir( progress_directory ) == False:
        os.mkdir( progress_directory )
    manuscript_data = pre_process()
    manuscript_data = normalize_markdown( manuscript_data )
    currentword_count = len(manuscript_data.split())
    word_count_dict = {}
    if os.path.isfile( progress_directory + "/progress.tsv"):
        with open( progress_directory + "/progress.tsv" , 'r', encoding="utf8") as content_file:
            # get file contents
            for line in content_file:
                entryDate, word_count = map(str, line.strip().split('\t') )
                word_count_dict[entryDate] = word_count

    word_count_dict[ str( datetime.date.today())] = currentword_count

    lastCount = 0
    for entryDate in sorted(word_count_dict.keys()):
        if str(datetime.date.today()) == entryDate:
            todays_progress = int(word_count_dict[ entryDate ]) - lastCount
        lastCount = int(word_count_dict[ entryDate ])

    with open( progress_directory + "/progress.tsv" , 'w', encoding="utf8") as content_file:
        for entryDate in sorted(word_count_dict.keys()):
            content_file.write( str(entryDate) + "\t" + str(word_count_dict[entryDate]) + "\n")

    if found_matplotlib and dont_draw_graphs == False:

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

        plt.savefig(progress_directory + "/progress-overall.png", bbox_inches='tight', dpi=300)

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


        plt.savefig(progress_directory + "/progress-daily.png", bbox_inches='tight', dpi=300)

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

def new_chapter( chapter_number = 0 ):
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

    chapter_notes = "Place your chapter notes here!\n"

    if os.path.isfile("./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/_Chapter notes.txt") == False:
        with open("./Manuscript/Chapter " + str(chapter_number) + " - " + chapter_name + "/_Chapter notes.txt" , 'w', encoding="utf8") as first_scene_file:
            first_scene_file.write( chapter_notes )

    print("* Added new chapter directory: " + "Chapter " + str(chapter_number) + " - " + chapter_name + "")

def init_project():
    new_chapter(1)

    if os.path.isdir("./People") == False:
        os.mkdir( "./People" )
    if os.path.isdir("./Places") == False:
        os.mkdir( "./Places" )
    if os.path.isdir("./Things") == False:
        os.mkdir( "./Things" )
    if os.path.isdir("./Notes") == False:
        os.mkdir( "./Notes" )
    if os.path.isdir(export_directory) == False:
        os.mkdir( export_directory )

    exampleCharacter = "# New Character Name\n\n## Role\n\nCharacter's role in the story\n\n## Description\n\nPhysical and mental description of the character."
    if os.path.isfile("./People/Example Character.md") == False:
        with open("./People/Example Character.md" , 'w', encoding="utf8") as example_bio_file:
            example_bio_file.write( exampleCharacter )

    exampleScene = "# New Location Name\n\n## Role\n\nScene's's role in the story\n\n## Description\n\nPhysical and mental description of the scene."
    if os.path.isfile("./Places/Example Scene.md") == False:
        with open("./Places/Example Scene.md" , 'w', encoding="utf8") as example_scene_file:
            example_scene_file.write( exampleScene )


def create_epub():
    global recreate_epub_and_temp_files
    #Requires SYSCALL to pandoc
    if os.path.isfile('./" + export_directory + "/" + config["bookFile"] + ".epub') == False and recreate_epub_and_temp_files == True:
        create_book_metadata()
        pre_process( writeFile = True )

        os.system("pandoc " + pandoc_markdown_arg + " -o \"" + export_directory + "/" + config["bookFile"] + ".epub\" \"00-ebook-info.txt\" \"temp_work_file.md\"")

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

    os.system("pandoc " + pandoc_markdown_arg + " -o \"" + export_directory + "/" + config["bookFile"] + ".html\" \"00-ebook-info.txt\" \"temp_work_file.md\"")

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

    os.system("pandoc -V fontsize=" + config["pdfFontSize"] + " " + pandoc_markdown_arg + " -o \"" + export_directory + "/" + config["bookFile"] + ".pdf\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    # print("pandoc -V fontsize=" + config["pdfFontSize"] + " " + pandoc_markdown_arg + " -o \"" + export_directory + "/" + config["bookFile"] + ".pdf\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".pdf created")


def create_doc():
    #Requires SYSCALL to pandoc
    create_book_metadata()
    pre_process( writeFile = True )
    os.system("pandoc " + pandoc_markdown_arg + " -o \"" + export_directory + "/" + config["bookFile"] + ".doc\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".doc created")


def create_docx():
    #Requires SYSCALL to pandoc
    create_book_metadata()
    pre_process( writeFile = True )
    os.system("pandoc -s -o \"" + export_directory + "/" + config["bookFile"] + ".docx\" \"00-ebook-info.txt\" \"temp_work_file.md\"")

    print("* " + export_directory + "/" + config["bookFile"] + ".docx created")


def create_odt():
    #Requires SYSCALL to pandoc
    create_book_metadata()
    pre_process( writeFile = True )

    os.system("pandoc " + pandoc_markdown_arg + " -o \"" + export_directory + "/" + config["bookFile"] + ".odt\" \"00-ebook-info.txt\" \"temp_work_file.md\"")
    print("* " + export_directory + "/" + config["bookFile"] + ".odt created")


def word_count():
    manuscript_data = pre_process()
    manuscript_data = normalize_markdown( manuscript_data )


    word_count =  len(manuscript_data.split()) - config["wordCountOffset"]
    print("    Project Wordcount: " + str(word_count) )
    print("     Today's Progress: " + str(todays_progress ) )
    return word_count


def chapter_word_count():
    chapter_data = pre_process_chapters()
    print("  -------------- Chapter Word Counts -----------------" )
    rpad_length = 0
    for chapter in chapter_data.keys():
        if len(chapter) > rpad_length:
            rpad_length = len(chapter)
    for chapter in chapter_data.keys():
        print( chapter.rjust(rpad_length) + ': ' + str( len(chapter_data[chapter].split()) ) )


if len(sys.argv) > 1:
    for arg in sys.argv:
        if arg == "init":
            init_project()
        elif arg == "all":
            save_progress()
            create_epub()
            create_mobi()
            create_html()
            create_txt()
            create_pdf()
            create_md()
            # create_doc()
            create_odt()
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
        # elif arg == "doc":
        #     save_progress()
        #     create_doc()
        elif arg == "odt":
            save_progress()
            create_odt()
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
            chapter_word_count()
        elif arg == "wc":
            save_progress()
            word_count()
            chapter_word_count()
        elif arg == "wordcount":
            save_progress()
            word_count()
            chapter_word_count()
        elif arg == "nano":
            updateNaNo()
        elif arg == "nc":
            new_chapter()
        elif arg == "newchapter":
            new_chapter()
        elif arg == "chapter":
            new_chapter()
        elif arg == "watch":
            watch()
        elif arg == __file__:
            # Do Nothing
            pass
        else:
            print("Warning unknown argument '" + arg + "'");
            print_help()
    remove_temp_files()

else:
    print_help()

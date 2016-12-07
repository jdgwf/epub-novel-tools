# EBook Creation Makefile
# Version .5 Alpha
# Tested only on Ubuntu 16.04

# Requires Pandock and Calibre to be installed
# sudo apt-get install -y pandoc calibre calibre-bin
# For PDF exports: sudo apt-get install texlive-latex-base texlive-fonts-recommended

# Jeffrey D. Gordon
# Twitter: @gauthic
# Github: JDGwf

# Change the following variables to suit your project :)
bookName = My Ebook
bookFile = My Ebook
authorName = Author Name
#copyRight = Creative Commons Non-Commercial Share Alike 3.0
copyRight = 2016 All rights reserved
languageCode = en-US
publisherName = Self Published
# just the name of your image in the current directory, such as coverImage.png
coverImage = 

# Once the project has been created, you'll have to edit 00-$(bookFile)-info.txt to change the title, etc. or init a new project

# Everything below here probably doesn't need to be changed
default:
	@echo "Usage:"
	@echo "	make init - create base directories and starter content - DANGER: this will overwrite your current content"
	@echo "	make requirements - for Ubuntu users: installs calibre and pandoc"
	@echo "	make ebooks - create .mobi and .epub from your manuscript"
	@echo "	make pdf - creates a pdf from your manuscript"
	@echo "	make wordcount - gives you a current wordcount of your manuscript"


epub:
	@# This assumes that files and folders in wildcards are listed in alphabetcal order
	@python ./md-preprocess.py
	@pandoc -S -o "$(bookFile).epub" "00-$(bookFile)-info.txt" ./temp_work_file.md
	@rm ./temp_work_file.md
plaintext: epub
	@pandoc -t plain "$(bookFile).epub" -o "$(bookFile).txt"

html:
	@# This assumes that files and folders in wildcards are listed in alphabetcal order
	@python ./md-preprocess.py
	@pandoc -s -S -o "$(bookFile).html" "00-$(bookFile)-info.txt" ./temp_work_file.md
	@rm ./temp_work_file.md

mobi: epub
	@ebook-convert "$(bookFile).epub" "$(bookFile).mobi" > "$(bookFile).convert.log"

ebooks: mobi

pdf:
	@python ./md-preprocess.py
	@pandoc -S -o "$(bookFile).pdf" "00-$(bookFile)-info.txt" ./temp_work_file.md
	@rm ./temp_work_file.md

requirements:
	@echo "Installing ebook compilation requirements via apt..."
	@sudo apt-get install -y pandoc calibre calibre-bin

pdfrequirements: requirements
	@echo "Installing PDF compilation requirements via apt..."
	@sudo apt-get -y install texlive-latex-base texlive-fonts-recommended

wordcount:
	@find ./Manuscript/ -type f -name "*.md" -exec wc -w {} +

init:
	@echo "---" > "00-$(bookFile)-info.txt"
	@echo "title: $(bookName)" >> "00-$(bookFile)-info.txt"
	@echo "author: $(authorName)" >> "00-$(bookFile)-info.txt"
	@echo "rights: $(copyRight)" >> "00-$(bookFile)-info.txt"
	@echo "language: $(languageCode)" >> "00-$(bookFile)-info.txt"
	@echo "publisher: $(publisherName)" >> "00-$(bookFile)-info.txt"
	@echo "cover-image: $(coverImage)" >> "00-$(bookFile)-info.txt"
	@echo "..." >> "00-$(bookFile)-info.txt"
	@mkdir -p "./Manuscript/Chapter 1/"
	@echo "\\\newpage" > "./Manuscript/Chapter 1/00 - chapter_heading.md"
	@echo "#Chapter 1 - Your first Chapter" >> "./Manuscript/Chapter 1/00 - chapter_heading.md"
	@echo "Your book starts here" > "./Manuscript/Chapter 1/01 - scene name.md"
	@echo "" >> "./Manuscript/Chapter 1/01 - scene name.md"
	@echo "Your second paragraph" >> "./Manuscript/Chapter 1/01 - scene name.md"
	@mkdir -p "./Bios/"
	@mkdir -p "./Scenes/"
	@mkdir -p "./Notes/"

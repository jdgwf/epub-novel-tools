#E-Novel project

##Description
Sets up a series of directories and compilation tools for Novel E-Book creation on Ubuntu Linux (tested on 16.04).

##Requirements
This software uses python, calibre, and pandoc..

The requirements for this can be installed by: 

    `sudo apt-get install -y pandoc calibre calibre-bin`

If you are wanting to create pdfs then you'll need to install (hard drive expensive) the latex pdf libraries:

    `sudo apt-get install texlive-latex-base texlive-fonts-recommended`

##Usage
Creation of a novel is simple.
Modify the Makefile variables (lines 14-22) to suit your project. Then type

    `make init`

to create the initial project directories. The only directory processed is the ./Manuscript/ the other directories are there for your own notes and reminders :)

To compile your ebooks there are various commands:

* `make ebooks` - creates both .mobi and .epub versions of your ./Manucript/
* `make html` - creates a formatted HTML file of your Manuscript
* `make pdf` - if the latex libs are installed, this will create a beautiful PDF of your manuscript
* `make wordcount` - will provide a final wordcount for your manuscript
* `make` - shows some of the options

##Editor
Until I write my own simplified editor, I use `atom .` to open the current directory for creating and modifying directories and files. There's a few plugins that I use that's very handy for UTF-8 fancy quotes:

* linter-write-good
* smart-quotes-plus

Atom can be downloaded at http://atom.io or installed via `apt-get install atom`
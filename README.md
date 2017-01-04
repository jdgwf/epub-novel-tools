# E-Novel project

## Description
Sets up a series of directories and MarkDown compilation tools for Novel E-Book novel creation on Linux (tested on Ubuntu 16.04 and 16.10, should work on and Debian too).

## Ubuntu on Windows 10
This **almost** works in Windows 10's Windows Subsystem for Linux. There's an issue with the POSIX timer that's been fixed in the next Windows 10 release when trying to run pandoc. I'll see how it goes and keep this section updated.

Reference: <https://github.com/Microsoft/BashOnWindows/issues/307>

## Requirements
This software uses python3, calibre, and pandoc..

### Ubuntu 16.04 && 16.10 (Tested and Verified)
You can install the requirements for this app with the following command (install size: ~223mb, this does include the full calibre e-book reader for your convienience):

    sudo apt-get install -y pandoc calibre calibre-bin

If want to create pdfs then you'll need to install the latex pdf libraries (install size: ~282mb):

    sudo apt-get install -y texlive-latex-base texlive-fonts-recommended


# Fedora 25
You can install the requirements for this app with the following command (install size: ~365mb, this does include the full calibre e-book reader for your convienience):

    sudo yum -y install -y pandoc calibre python3-yaml

If want to create pdfs then you'll need to install the latex pdf libraries (install size: ~255mb):

    sudo yum -y install texlive

This should work in CentOS, but pandoc and calibre aren't in the standard repositpories and you'll have to install them manually or add the Fedora repos

# Windows (Native, tested in Windows 10)
Install Python 3 for Windows (don't forget to add the 'add python to path variable' in the install options ) <https://www.python.org/downloads/windows/>

Install tye pyyaml package via pip (needed for reading config files)

Install pandoc for Windows including the suggested MiKTeX package <http://www.pandoc.org/installing.html>

Install Calibre for Windows: <http://calibre-ebook.com/download_windows> for ebook-convert

# Progress Tracking
I've added functionality which will track your word count progress per day. A ./Progress directory will be created which will update the progress.tsv every time the script is run (even for just displaying the help). Additionally, if the python3-matplotlib library is installed it'll create a PNG graph of your progress. You can install it by typing:

    sudo apt-get install python3-matplotlib

Otherwise only the TSV will be updated.

## Usage
Creation of a novel is simple.
Type:

    python enovel-project.py init

or

    ./enovel-project.py init

to create the initial project directories. The only directory processed is the ./Manuscript/ the other directories are there for your own notes and reminders :)

Modify the newly created `config.yml` file to suit your novel name and your author name before compiling. It can easily be changed after compilation, but you'll need to recompile the ebooks and pdf if you do.

To compile your ebooks there are various commands:

* `python enovel-project.py` - shows some of the options
* `python enovel-project.py ebooks` - creates both .mobi and .epub versions of your ./Manucript/
* `python enovel-project.py html` - creates a formatted HTML file of your Manuscript
* `python enovel-project.py pdf` - if the latex libs are installed, this will create a beautiful PDF of your manuscript
* `python enovel-project.py wordcount` - will provide a final wordcount for your manuscript

You can combine arguments as well `python enovel-project.py html pdf` will create html and pdf formats of the manuscript

## Looking to the Future
Eventually I'd like to remove the os.system() calls and have all the document creation native Python. This will be a long, slow process *IF* I decide to go that route.

### NanoWriMo Imports and Updates
By NaNoWriMo 2017, I'll should have the ability to update your word count from a wordcount or new function. I should also have the ability to import current word counts via their API too. I'm still looking into that.

## Editor
Until I write my own simplified editor, I use `atom .` to open the current directory for creating and modifying directories and files. There's a few plugins that I use that's very handy for UTF-8 fancy quotes:

* linter-write-good
* smart-quotes-plus

Atom can be downloaded at http://atom.io or installed via `apt-get install atom`

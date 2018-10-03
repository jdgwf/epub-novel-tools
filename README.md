# E-Novel project

## Description
Sets up a series of directories and MarkDown compilation tools for Novel E-Book novel creation on Linux (tested on Ubuntu 16.04 and 16.10, should work on and Debian too).

As of version 0.8 Provides word count functions and history tracking.

## Ubuntu on Windows 10
This **almost** works in Windows 10's Windows Subsystem for Linux. There's an issue with the POSIX timer that's been fixed in the next Windows 10 release when trying to run pandoc. I'll see how it goes and keep this section updated.

Reference: <https://github.com/Microsoft/BashOnWindows/issues/307>

**Verified**: This now works on the Fast Ring release of Windows 10. That version will trickle down to Slow Ring and eventually Release.

## Requirements
This software uses python3, calibre, and pandoc..

### Ubuntu 16.04 && 16.10 (Tested and Verified)
You can install the requirements for this app with the following command (install size: ~223mb, this does include the full calibre e-book reader for your convienience):

    sudo apt-get install -y pandoc calibre calibre-bin python3-yaml

If want to create pdfs then you'll need to install the latex pdf libraries (install size: ~282mb):

    sudo apt-get install -y texlive-latex-base texlive-fonts-recommended

*I have not tested this with Ubuntu 14.\* or 15.\* as I don't use anything older than the latest LTS on my desktop (#sorrynotsorry). I'm sure that python3 will at least have to be installed.*

# Fedora 25
You can install the requirements for this app with the following command (install size: ~365mb, this does include the full calibre e-book reader for your convienience):

    sudo yum -y install -y pandoc calibre python3-yaml

If want to create pdfs then you'll need to install the latex pdf libraries (install size: ~255mb):

    sudo yum -y install texlive

This should work in CentOS 7, but pandoc and calibre aren't in the standard repositpories and you'll have to install them manually or add the Fedora repos

# Windows (Native, tested in Windows 10)
Install Python 3 for Windows (don't forget to add the 'add python to path variable' in the install options ) <https://www.python.org/downloads/windows/>

Install tye pyyaml package via pip (needed for reading config files)

Install pandoc for Windows including the suggested MiKTeX package <http://www.pandoc.org/installing.html>

Install Calibre for Windows: <http://calibre-ebook.com/download_windows> for ebook-convert

*I'm not sure if it's the environment, the python, Calibre, and/or pandoc builds, but it seems that the compilation seems noticeably slower than Ubuntu 16.04. Don't fret still not slow (as you should be spending more time writing than compiling).*

# MacOS (Native)

This guide requires the use of homebrew - https://brew.sh/ Install this fantastic package manager to install the requirements.

	brew install python3 pandoc Caskroom/cask/calibre
	pip3 install pyyaml matplotlib

## For PDF Creation
Again, this is a fairly large library and you may not need it

	brew cask install mactex

**Note:** You'll have to restart your shell for pdflatex to show up for some reason I don't want to research.

# Progress Tracking
I've added functionality which will track your word count progress per day. A ./Progress directory will be created which will update the progress.tsv every time any progress is saved. Additionally, if the python3-matplotlib library is installed it'll create a PNG graph of your progress. You can install it by typing:

    sudo apt-get install python3-matplotlib

If not in Ubuntu:

    pip3 install matplotlib

Might work.

Otherwise only the TSV will be updated.

# Watchdog
For 2018's NaNoWriMo I've added a watch function which requires the installation of watchdog:
        pip3 install matplotlib
To invoke this functionality just run:
        python3 enovel-project.py watch

While running each time you save a file in the manuscript directory it'll display a wordcount, the difference since starting the watch function, and since the last file save.

To exit just Control-C as expected to close out of a CLI app.

## Usage
Creation of a novel is simple.
Type:

	python enovel-project.py init

or, if py3 is not your default version

	python3 enovel-project.py init

or

    ./enovel-project.py init

to create the initial project directories. The only directory processed is the ./Manuscript/ the other directories are there for your own notes and reminders :)

Modify the newly created `config.yml` file to suit your novel name and your author name before compiling. It can easily be changed after compilation, but you'll need to recompile the ebooks and pdf if you do.

To compile your ebooks there are various commands:

* `python enovel-project.py` - shows some of the options
* `python enovel-project.py ebooks` - creates both .mobi and .epub versions of your ./Manucript/
* `python enovel-project.py epub` - creates an .epub versions of your ./Manucript/
* `python enovel-project.py mobi` - creates a .mobi  versions of your ./Manucript/
* `python enovel-project.py html` - creates a formatted HTML file of your Manuscript
* `python enovel-project.py rtf` - creates a formatted Rich Text Format file of your Manuscript
* `python enovel-project.py text` - (also `txt`) creates a marginzed text file of your Manuscript
* `python enovel-project.py md` - (also `markdown`) creates a markdown file of your Manuscript
* `python enovel-project.py doc` - creates a legacy Microsoft Word file of your Manuscript
* `python enovel-project.py docx` - creates a Microsoft Word file file of your Manuscript
* `python enovel-project.py pdf` - if the latex libs are installed, this will create a beautiful PDF of your manuscript
* `python enovel-project.py wordcount` - will provide a final wordcount for your manuscript
* `python enovel-project.py nano` - will attempt to update the progress on your NaNoWriMo account if you've filled in your username and secret in the config.yml file
* `python enovel-project.py chapter` - ( also `newchapter` or `nc` ) - will try to automatically create a new chapter directory and initial files
* `python enovel-project.py all` - Attempts to export all exportable formats and then produces a word count.

You can combine arguments as well `python enovel-project.py html pdf` will create html and pdf formats of the manuscript

## Looking to the Future
Eventually I'd like to remove the os.system() calls and have all the document creation native Python. This will be a long, slow process *IF* I decide to go that route as what works here works great.

### NanoWriMo Imports and Updates
By NaNoWriMo 2017, I'll should have the ability to update your word count from a wordcount or new function. I may also have the ability to import current word counts via their API too. I'm still looking into that.

*Just a note for self-reminder: http://nanowrimo.org/en/wordcount_api*

## Editor
Until I write my own simplified editor, I use `atom .` to open the current directory for creating and modifying directories and files. There's a few plugins that I use that's very handy for UTF-8 fancy quotes:

* linter-write-good
* smart-quotes-plus

Atom can be downloaded at http://atom.io or installed via `apt-get install atom`

Feel free to use any editor you like, whether it be a coding editor, plain text or a dedicated markdown editor. Open Source is about choice and freedom :)

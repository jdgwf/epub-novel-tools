#E-Novel project

##Description
Sets up a series of directories and compilation tools for Novel E-Book creation on Ubuntu Linux (tested on 16.04).

##Requirements
This software uses python, calibre, and pandoc..

You can install the requirements for this app with the following command:

    sudo apt-get install -y pandoc calibre calibre-bin

If you are wanting to create pdfs then you'll need to install (hard drive expensive) the latex pdf libraries:

    sudo apt-get install -y texlive-latex-base texlive-fonts-recommended

##Usage
Creation of a novel is simple.
Then type

    python enovel-project.py init

to create the initial project directories. The only directory processed is the ./Manuscript/ the other directories are there for your own notes and reminders :)

Modify the created config.yml file to suit your novel name and your author name before compiling. It can easily be changed after compilation, but you'll need to recompile the ebooks and pdf if you do.

To compile your ebooks there are various commands:

* `python enovel-project.py ebooks` - creates both .mobi and .epub versions of your ./Manucript/
* `python enovel-project.py html` - creates a formatted HTML file of your Manuscript
* `python enovel-project.py pdf` - if the latex libs are installed, this will create a beautiful PDF of your manuscript
* `python enovel-project.py wordcount` - will provide a final wordcount for your manuscript
* `python enovel-project.py` - shows some of the options

##Editor
Until I write my own simplified editor, I use `atom .` to open the current directory for creating and modifying directories and files. There's a few plugins that I use that's very handy for UTF-8 fancy quotes:

* linter-write-good
* smart-quotes-plus

Atom can be downloaded at http://atom.io or installed via `apt-get install atom`

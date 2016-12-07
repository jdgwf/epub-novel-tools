#!/usr/bin/python
import os

manuscriptDir = "./Manuscript"

manuscriptContents = ""

for root, dirs, files in sorted(os.walk( manuscriptDir )):
    path = root.split('/')
    #print((len(path) - 1) * '---', os.path.basename(root))
    for file in sorted(files):
        #print(len(path) * '---', file)
        # print (manuscriptDir + "/" + os.path.basename(root) + "/" + file)


        with open(manuscriptDir + "/" + os.path.basename(root) + "/" + file , 'r') as content_file:
            # get file contents
            fileContents = content_file.read()

            # trim the contents
            fileContents = fileContents.strip()
            # remove existing markdown HRs
            fileContents = fileContents.replace( "----\n", "")
            fileContents = fileContents.replace( "\n----", "")
            fileContents = fileContents.replace( "---\n", "")
            fileContents = fileContents.replace( "\n---", "")

            # replace all triple newlines with double newlines (normalize any extras)
            fileContents = fileContents.replace( "\n\n\n", "\n\n")

            # add an md HR at the end of the file
            manuscriptContents += fileContents + "\n\n----\n\n"

    # remove final "\n\n----\n\n"
    if manuscriptContents.endswith("\n\n----\n\n"):
        manuscriptContents = manuscriptContents[:-len("\n\n----\n\n")]
        manuscriptContents += "\n\n"


# save contents
with open("temp_work_file.md" , 'w') as working_file:
    working_file.write( manuscriptContents )

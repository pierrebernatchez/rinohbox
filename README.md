
Project README
==============

A package to encapsulate a costomized pipeline for rendering .rst files into .pdf files
using RINOH and Sphinx and docutils AND pelican as infrastrucure elements.

## Explanation

These are the basic activities we want to support with this rinoh rendering pipeline.

1. Render each .rst file in a directory into a corresponging individual .pdf document.
2. Render all .rst files in a directory into a single comprehensive .pdf document for the directory.
3. Render temporary .pdf files to allow our editor to present a .pdf view of the document prior to submssion.
4. Render select .rst files into single .pdf documents for customized purposes such as a homework assignmment
   or an exam document.

The rinoh rendering system - used with sphinx - needs to work from a
directory where there is a conf.py config file an index.rst and any
number of .rst files to be rendered.  that directory needs to be set
up with a few items in it that the program expects to find. I have
taken to calling this a staging directory or simply a stage.

The process of rendering a list of one or more .rst files consists of

1. creating and initializing a tempory stage directory.
   Note the stage directory looks like this:
   stage/
   ├── images
   ├── output
   └── source
      ├── conf.py
      ├── rinoh_article_template.py
      ├── _static
      └── _templates

   6 directories, 2 files

2. Setting the stage: Populating the stage with content.  Generating an index.rst file
   while transferring .rst files to the stage source/ directory.  Then putting
   index.rst in source/ too.  The transferring process filters out
   metadata from the input .rst files.  It also adds a '.. pagegreak::' directives to
   the end of each of those .rst file.

   We also populate the images/ directory with media (.jpg, .png, ...) files used by
   those .rst files.

3. Invoking "sphinx-build -b rinoh" using the stage for its source and output directories.
   E.G. "sphinx-build -b rinoh /tmp/rinohbxxxxx/source /tmp/rinohbxxxxx/output" 


4. Extracting files from output/  directory (i.e. creating hard links to its files in some target directory).

5. Finally removing staging directory tree.


## Implementation Overview

  We have implemented **newstage** which accomplishes step 1.  It
  prints the full path name of the staging directory to stdout.  Any
  other printing is to stderr.  This is for the convenience of bash
  scripting.

  We have implemented **setstage** which accomplishes step 2 It takes
  the staging directory path as one of its inputs.  It also prints
  that path to stdout and any other print is to stderr, also for bash
  scripting convenience.

  We have implemented **rmstage** which recursively removes staging
  directories which accomplished step 5.  But since that is quite a
  dangerous command, it double checks the name pattern, and that the
  argument is a directory before removing the directory and everything
  below it.

  We have also implemented **clearstage** which removes all but its
  initial pre-setstage contents. This is to serve cases where we need
  to re-use a stage rather than remove it and re-create it.

  Both **newstage** and **setstage**
  print the stage path value as their only output to stdout.  This makes
  it easy to capture into a variable for bash scripting removal of it.

  At this point we have implementd three bash scripts which invoke these
  scripts.  Each of them look after invoking steps 3 and 4 of the rendering
  steps above. At some point after testing we are goint to want to translate
  those implementations to python scripts so as to make it straightforward
  to install all we using flit.

  single2pdf      renders a single file.
  alltogether2pdf renders all .rst files matching the given .rst file into a single .pdf file.
  allapart2pdf    renders all .rst files matching the given .rst file into separate .pdf files.



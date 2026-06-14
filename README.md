
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

1. creating and initializing a tempory stage.  Note I chose to
   create the stage with a subdirectory called 'out' that can serve
   as an output directory for rinoh_build command.

2. Populating the stage with content.  Generating an index.rst file
   while transferring .rst files to the sandbox.  Then putting
   index.rst in the stage too.  The transferring process filters out
   metadata from the input .rst files

3 .Invoking rinoh_build using that stage directory  as its source and the 'out' subdirectory as its output dirctory.

4. Extracting resulting pdfs from the 'out' directory (creating hard links to its .pdf files in some target directory).

5. Once we have finished our rendering we need to remove the staging directory.


## Implementation Overview

  We have implemented **newstage** which accomplishes step 1.  It
  prints the full path name of the staging directory to stdout.  Any
  other printing is to stderr.  This is for the convenience of bash
  scripting.

  We have implemented **setstage** which accomplishes steps 2, 3, and
  4.  It takes the staging directory path as one of its inputs.  It
  also prints that path to stdout and any other print is to stderr,
  also for bash scripting convenience.

  We have implemented **rmstage** which recursively removes staging
  directories which accomplished step 5.  But since that is quite a
  dangerous command, it double checks the name pattern, and that the
  argument is a directory before removing the directory and everything
  below it.

  We have also implemented **clearstage** which removes all but its
  initial pre-setstage contents. We have this in the case we need to
  re-use a stage rather than remove it and re-create it.

Both **newstage** and **setstage**
  print the stage path value as their only output to stdout.  This makes
  it easy to capture into a variable for bash scripting removal of it.






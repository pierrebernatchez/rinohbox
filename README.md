
Project README
==============

A package to encapsulate a costomized pipeline for rendering .rst files into .pdf files
using RINOH and Sphinx and docutils AND pelican as infrastrucure elements.

## Explanation

These are the basic activities we want to support with this rinoh rendering pipeline.

1. Render each .rst file in a directory into a corresponging individual .pdf document.
2. Render all .rst files in a directory into a single comprehensive .pdf document for the directory.
3. Render temporary .pdf files to allow our editor to present a .pdf view of the document priore to submssion.
4. Render select .rst files into single .pdf documents for customized purposes such as a homework assignmment
   or an exam document.

The rinoh rendering system - used with sphinx - needs to work from a
directory where there is a conf.py config file an index.rst and any
number of .rst files to be rendered.  that directory needs to be set
up with a few items in it that the program expects to find. I have
taken to calling this directory a sandbox.

The process of rendering a list of one or more .rst files consists of

1. creating and initializing a tempory sandbox.  Note I chose to
   create the sandbox with a subdirectory called 'out' that can serve
   as an output directory for rinoh_build command.

2. Populating the sandbox with content.  Generating an index.rst file
   while transferring .rst files to the sandbox.  Then putting
   index.rst in the sandbox too.  The transferring filters out
   metadata from the input .rst files

3 .Invoking rinoh_build using that sandbox as its source directory and the 'out' subdirectory as its output dirctory.

4. Extracting resulting pdfs from  the 'out' subdirectory (creating hard links to its .pdf files in some target directory).

5. Once we have finished our rendering we need to remove the sandbox.


## Implementation Overview

  We have implemented **newrinohbox** which accomplishes step 1.  It
  prints the full path name of the sandbox directory to stdout.  Any
  other printing is to stderr.  This is for the convenience of bash
  scripting.

  We have implemented **rinohrender** which accomplishes steps 2, 3, and
  4.  It takes the sandbox path as one of its inputs.  It also prints
  the sandbox path to stdout and any other print to stderr, also for
  bash scripting convenience.

  Removing the sandbox is merely a matter of **rm -r -I <sanboxpath>**
  which accomplished step 5.  Both **newrinohbox** and **rinohrender**
  print the <sanboxpath> value as their only output to stdout.  So it
  is easy to capture that into a variable for bash scfripting removal
  of the sandbox.






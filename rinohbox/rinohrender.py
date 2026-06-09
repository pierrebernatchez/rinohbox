#!/usr/bin/env python3

"""
  Tools to instantiate a sandbox environment for rendering from rst
  files to pdf documents, and using that sandbox to render .pdfs from
  .rst files.

"""
import os
import sys
import shutil
import argparse
import re
from pathlib import Path
DEFAULT_BOXDIR=Path("/tmp/rinohbox")
PROGNAME=os.path.basename(__file__)

def copy_no_meta(src, dst):
    """copies the file contents but skips lines with metadata"""
    with open(src) as fin, open(dst, 'w') as fout:
        for line in fin:
            if not re.match(r'^:.*:', line): # the ^ is unnecessary in this context, but does not hurt
                fout.write(line)

def emit_index_and_rstfiles(list_rstfiles, preamble="", sandbox=DEFAULT_BOXDIR):
    """Emit an index.rst file with an include for each file and emit each file with metatags stripped"""
    boxpath=Path(sandbox)
    incls = [ f"include={a}.rst" for a in list_rstfiles ]
    preamble_with_incls = [preamble] + incls
    preamble_with_incls.append("") # so that we get a trailing newline with join
    includeblock = "\n".join(preamble_with_incls)
    indexpath = boxpath / Path("index.rst")
    indexpath.write_text(includeblock)
    # hard link every source file into the sandbox
    for afull in list_rstfiles:
        abasename = os.path.basename(f"{afull}")
        afullsource = Path(afull)
        afulldest = boxpath / Path(abasename)
        afulldest.resolve()
        afullsource.resolve()
        print("{__file__}: {afullsource} -> {afulldest}",file=sys.stderr)
        copy_no_meta(afullsource, afulldest)        
    return
                

def renderinit(list_rstfiles, # source rst file full paths 
               preamble="", # Preamble for the index.rst file.
               sandbox=DEFAULT_BOXDIR):
    """Funcion  poputates a rinohbox with .rst files to be rendered and the index.rst that includes them."""
    # emit the index.rst file
    default_boxdir=Path("/tmp/rinohbox")
    parser = argparse.ArgumentParser(description='Initialize a rinoh sandbox directory')
    parser.add_argument('-t', '--target',
                        default=default_boxdir,
                        dest="target",
                        help=f"Path to target directory to serve as a sandbox (Dflt {default_boxdir})")
    parser.add_argument('-o','--overwrite',
                        action='store_true',
                        dest='overwrite',
                        help='Re-initialize target directory if it already exists.')
    
    args = parser.parse_args()
    targetdir = Path(args.target)
    if targetdir.is_dir():
        if args.overwrite:
            print(f"Removing existing tree: {targetdir}", file=sys.stderr)
            shutil.rmtree(targetdir)
        else:
            print(f"File {targetdir} already exists, and no --overwrite. ABORTING.", file=sys.stderr)
            exit( 1 )
    targetdir.mkdir()
    fulltarget = targetdir.resolve()
    transfer(fulltarget)    
    print(f"{fulltarget}")
    exit(0)

def validated_args(myargs):
    """Trim list to only readable files with names ending in '.rst'"""
    def rst_and_readable_but_not_index_files():
        valids= [ af for af in myargs if af.endswith(".rst") and
                  os.path.basename(af) != "index.rst" and
                  os.path.isfile(af) and
                  os.access(af, os.R_OK)]

        
        return list(dict.fromkeys(valids)) # drops duplicates, leaving order intact
    valids = rst_and_readable_but_not_index_files()
    for afile in myargs:
        if afile not in valids:
            print(f"{__file__}: Ignored: {afile}", file=sys.stderr)
    return valids

def render():
    """Composes list of '.rst' files and renders them into individual or a single '.pdf' file(s)"""
    curdir = Path('.').resolve()
    curbase = os.path.basename(curdir)
    dirname = curdir.parent
    dflt_media = dirname / Path( f"{curbase}-media")
    dflt_target= dirname / Path( f"{curbase}-pdfs")
    parser = argparse.ArgumentParser()
    parser.add_argument('rstfiles', nargs='*', help='RST files to process.')
    parser.add_argument('-b', '--boxpath', dest="boxpath", required=True,
                        help=f'Sandbox to use (as returned by newrinoh).')
    parser.add_argument('-m', '--media', default=dflt_media, dest="media",
                        help=f'Where to get media files from (dflt {dflt_media}).')
    parser.add_argument('-t', '--target', default=dflt_target, dest="target",
                        help=f'Where to put the resulting documents (dflt {dflt_target}).')
    parser.add_argument('-p', '--preamble', dest='preamble', help=f"File containing preamble text for index.rst file (dflt None)")
    
    args = parser.parse_args()
    
    if len(args.rstfiles) == 0:
        myargs = sorted([str(p) for p in Path('.').glob('*.rst')])
        valid_args= validated_args(myargs)
    else:
        valid_args= validated_args(args.rstfiles)
    if args.preamble is None:
        preamble = ""
        valid_args = [ Path(af).resolve() for af in valid_args ]        
    else:
        preamblefile = Path(args.preamble).resolve()
        # if necessary drop the preamble file from the ones we will include in the render
        valid_args = [ Path(af).resolve() for af in valid_args if not os.path.samefile(Path(af).resolve(),  preamblefile)]
        with open(preamblefile, "r") as pfile:
            preamble = pfile.read()
    print(f"{PROGNAME}: Preamble: BEGIN", file=sys.stderr)
    print(f"{preamble}{PROGNAME}: Preamble: END")
    print(f"{PROGNAME}: Media from: {args.media}", file=sys.stderr)
    print(f"{PROGNAME}: Results to: {args.target}", file=sys.stderr)
    if len(valid_args) == 0 :
        print(f"{PROGNAME}: Nothing to render.", file=sys.stderr)
    else:
        for anrst in valid_args:
            print(f"{PROGNAME}:     {anrst}", file=sys.stderr)
    

script_name = os.path.basename(__file__)
if __name__ == '__main__':
    render()
    print(f"{script_name}: This module is not intended to be used directly, but imported.")
    exit(1)

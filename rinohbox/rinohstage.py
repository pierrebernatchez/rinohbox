#!/usr/bin/env python3

"""
  Tools to instantiate a sandbox environment for rendering from rst
  files to pdf documents, and using that sandbox to render .pdfs from
  .rst files.

"""
import os
import sys
import tempfile
import shutil
import argparse
import importlib.resources as resources
from pathlib import Path
import re

DEFAULT_STAGINGDIR=Path("/tmp/rinohstage")
PROGNAME=os.path.basename(__file__)

SAFEPRIFIX="rinohb"
SAFESUFFIX="dblchk"
def preparestage(stagedir):
    """Create the subdirectories required by the rinoh-rendering staging
    subdirectory and transfer the .py files it needs there.
    The .py files are pulled out of the rinohbox package library.
    """ 
    subdir= stagedir / "output"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= stagedir / "source"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= stagedir / "images"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= stagedir / "source" / "_static"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= stagedir / "source" / "_templates"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    src = resources.files('rinohbox') #
    conf_file_src = src / 'rinohconf.py'
    conf_file_dst = stagedir / "source" / 'conf.py'
    temp_file_src = src / 'rinoh_article_template.py'
    temp_file_dst = stagedir / "source" / 'rinoh_article_template.py'
    print(f"src={conf_file_src} dest={conf_file_dst}", file=sys.stderr)
    shutil.copy(conf_file_src, conf_file_dst)
    print(f"src={temp_file_src} dest={temp_file_dst}", file=sys.stderr)
    shutil.copy(temp_file_src, temp_file_dst)
    return

def rmtree_keep_root(path):
    """like rmtree except wihtout removing the root"""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            shutil.rmtree(entry.path)
        else:
            os.remove(entry.path)
 
def do_clearstage(staging):
    """Clean out an existing staging area but leave the original stuff as it was"""
    # keepers under the staging directory
    keepers=(
        "output",
        "images",
        "source")
    # keepers under source subdirectory
    source_keepers=(
        "_templates",
        "_static",
        "conf.py",
        "rinoh_article_template.py")
    # We keep keeper directories but (exept for source) we remove their contents
    for entry in os.scandir(staging):
        if entry.name in keepers:
            if entry.name == "source":
                pass
            elif entry.is_dir(follow_symlinks=False): 
                rmtree_keep_root(entry.path)
            else:
                pass # skip regular files (if ever we add some to keepers list)
        elif entry.is_dir(follow_symlinks=False):
            shutil.rmtree(entry.path)
        else:
            os.remove(entry.path)
    staging_source = Path(staging) / "source"
    for entry in os.scandir(staging_source):
        if entry.name in source_keepers:
            if entry.is_dir(follow_symlinks=False):
                rmtree_keep_root(entry.path)
            else:
                pass
        elif entry.is_dir(follow_symlinks=False):
            shutil.rmtree(entry.path)
        else:
            os.remove(entry.path)
    return staging

def do_newstage():
    """Create and initialize a temp directory to use as a staging area
    for rendering with rinoh"""
    tmpdir = tempfile.mkdtemp(prefix=SAFEPRIFIX, suffix=SAFESUFFIX)
    fullstage = Path(tmpdir).resolve()
    preparestage(fullstage)    
    return fullstage

def newstage():
    """ENTRYPOINT  for creating a new rinohbox staging area directory"""
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    if len(sys.argv) > 1:
        parser.error("This command takes no arguments")    
    stagedir= do_newstage()
    print(f"{stagedir}")
    exit(0)

def clearstage():
    """ENTRYPOINT Remove all but what files and directories it began with from staging directory."""
    parser = argparse.ArgumentParser()
    parser.add_argument('stagingdir', nargs=1, help='Rinoh RST Staging directory to clean up.')
    args = parser.parse_args()
    requested_dir = args.stagingdir[0]
    if safestagedir(requested_dir) :
        target = do_clearstage(requested_dir)
        print(f"{target}")
        exit(0)
    else:
        print(f"Invalid Rinoh staging directory: {requested_dir}")
        exit(1)

def safestagedir(tmpboxdir):
    """Make sure our box is a directory that matches our nameing pattern"""
    filepath = Path(tmpboxdir)
    filepath.resolve()
    if filepath.is_dir():
        filename = filepath.name
        if filename.startswith(SAFEPRIFIX) and filename.endswith(SAFESUFFIX):
            return True
        else:
            print(f"{__file__}: safestagedir({filepath}) FAILED. Invalid Name pattern.", file=sys.stderr)
            return False
    else:
        print(f"{__file__}: safestagedir({filepath}) FAILED. Not a directory.", file=sys.stderr)
        return False
    
def saferemovestage():
    """ENTRYPOINT Recursively removes a staging directory.  But its name must match prefix and suffix."""
    parser = argparse.ArgumentParser()
    parser.add_argument('stagingdir', nargs=1, help='an existing rinoh staging directory.')
    args = parser.parse_args()
    tmpstagingdirr  = args.stagingdir[0]
    if safestagedir(tmpstagingdirr):
        shutil.rmtree(tmpstagingdirr)
        # the convention is to print the path name to return it to the invoking shell program
        print(f"{tmpstagingdirr}")
        exit(0)
    else:
        print(f"Invalid rinoh staging directory: {tmpstagingdirr}")
        exit(1)


def copy_no_meta(src, dst, pagebreak=None):
    """copies the file contents but skips lines with metadata"""
    # pagebreak is an optional pagebreak directive line to be appended
    with open(src) as fin, open(dst, 'w') as fout:
        for line in fin:
            if not re.match(r'^:.*:', line): # the ^ is unnecessary in this context, but does not hurt
                fout.write(line)
        if pagebreak is not None:
            fout.write(pagebreak)
        # add a page break as the last line
 
def emit_index_and_rstfiles(list_rstfiles, stagingdir=DEFAULT_STAGINGDIR):
    """Emit an index.rst file with an include for each file and emit each file with metatags stripped"""
    # All our index.rst files are the same.  No need for anything else.
    # These lines followed by one toc entry for each .rst file.
    default_preamble="""
.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: contents:
"""
    mypreamble = default_preamble
    stagepath=Path(stagingdir)
    inames= [ Path(ap).stem  for ap in list_rstfiles ] 
    incls = [ f"   {a}" for a in inames ]
    preamble_with_incls = [mypreamble] + incls
    preamble_with_incls.append("") # so that we get a trailing newline with join
    includeblock = "\n".join(preamble_with_incls)
    indexpath = stagepath / "source" /  Path("index.rst")
    indexpath.write_text(includeblock)
    # At this writing we are no longer appending page breaks.  FIXME if necessary.
    # filter every source file into the sandbox appending pagebreak on all but the last one
    mypairs = [ (afile, "\n\n.. pagebreak::\n") for afile in list_rstfiles ]
    mypairs[-1] = (mypairs[-1][0], None) # dont want a pagebreak on last one
    for afull, abreak  in mypairs:
        abasename = os.path.basename(f"{afull}")
        afullsource = Path(afull)
        afulldest = stagepath / "source" / Path(abasename)
        afulldest.resolve()
        afullsource.resolve()
        print(f"{__file__}: {afullsource} -> {afulldest}",file=sys.stderr)
        copy_no_meta(afullsource, afulldest, pagebreak=abreak)
    return
                
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

def setstage():
    """ENTRYPOINT
    Our job is to copy all our articles.rst files to the staging
    directory.  While doing so we must filter out all the meta data.
    We also need to make up an index.rst file by appending include
    statements - one for each copied file - to any preamble we have
    been given.  Then we write the index.rst file to the staging
    directory too.  In short we set up a staging area for rendering a
    .pdf file using Sphinx and rinoh on top of docutils.
    """
    curdir = Path('.').resolve()
    curbase = os.path.basename(curdir)
    dirname = curdir.parent
    dflt_media = dirname / Path( f"{curbase}-media")
    dflt_target= dirname / Path( f"{curbase}-pdfs")
    parser = argparse.ArgumentParser()
    parser.add_argument('rstfiles', nargs='*', help='RST files to process.')
    parser.add_argument('-s', '--stagingpath', dest="stagingpath", required=True,
                        help=f'staging directory to use (as returned by newrstage).')
    parser.add_argument('-l', '--lang', choices=["en","fr","es"], default="en",
                        help=f'language specific .rst files to glob for  (default en).')
    parser.add_argument('-m', '--media', default=dflt_media, dest="media",
                        help=f'Where to get media files from (dflt {dflt_media}).')
    parser.add_argument('-t', '--target', default=dflt_target, dest="target",
                        help=f'Where to put the resulting documents (dflt {dflt_target}).')
    parser.add_argument('-f', '--frontpage', dest='frontpage',
                        help=f"Front page article to come out as first page. (dflt None)")
    args = parser.parse_args()
    mystage = args.stagingpath
    # the convention is to print the path name to return it to the invoking shell program
    if safestagedir(mystage):
        pass
    else:
        print(f"{PROGNAME}: Invalid rinoh staging directory: {mystage}", file=sys.stderr)
        print(f"Invalid rinoh staging directory: {mystage}")
        exit(1)
    imagesdir = Path(mystage) / "images"
    images = [img for img in Path(args.media).glob('*')]
    for imgfile in images:
        dst = imagesdir / imgfile.name
        src = imgfile
        dst.unlink(missing_ok=True)
        dst.hardlink_to(src)\

    if len(args.rstfiles) == 0:
        myargs = sorted([str(p) for p in Path('.').glob(f'*-{args.lang}.rst')])
        valid_args= validated_args(myargs)
    else:
        valid_args= validated_args(args.rstfiles)
    if args.frontpage is None:
        frontpage = None
        print(f"{PROGNAME}: No Front Page.", file=sys.stderr)
        valid_args = [ Path(af).resolve() for af in valid_args ] # no frontpage file to drop
    else:
        frontpagefile = Path(args.frontpage).resolve()
        # double check the validity of the frontpage file just like the others.
        listofone = [ f"{frontpagefile}" ]
        validfrontpages = validated_args(listofone)
        if len(validfrontpages) != 1:
            print(f'{PROGNAME}: Front page: "{frontpagefile}" is not a valid file.', file=sys.stderr)
            print(f'Aborting render. Leaving the directory "{mystage}" intact.')
            exit(1)
         
        
        # if necessary drop the frontpage filename from the ones to include in the render
        valid_args = [Path(af).resolve() for af in valid_args
                      if not os.path.samefile(Path(af).resolve(),  frontpagefile)]
        print(f"{PROGNAME}: Front Page: {frontpagefile}", file=sys.stderr)
    print(f"{PROGNAME}: Media from: {args.media}", file=sys.stderr)
    print(f"{PROGNAME}: Results to: {args.target}", file=sys.stderr)
    if len(valid_args) == 0 :
        print(f'{PROGNAME}Nothing to render. Leaving the directory "{mystage}" intact.', file=sys.stderr)
        print(f'Nothing to render. Leaving the directory "{mystage}" intact.')
        exit(1)
    else:
        if args.frontpage is not None:
            valid_args.insert(0, frontpagefile)
        # Log the .rst file names 
        for anrst in valid_args:
            # Log each inpput .rst file name for debug info
            print(f"{PROGNAME}: {anrst}", file=sys.stderr)
        emit_index_and_rstfiles(valid_args, stagingdir=mystage) # let preamble default to None to trigger default
        # Report success
        print(f"{PROGNAME}: {mystage} is ready to render.", file=sys.stderr)
        print(f'{mystage}')
        

script_name = os.path.basename(__file__)
if __name__ == '__main__':
    print(f"{script_name}: This module is not intended to be used directly, but imported.")
    exit(1)

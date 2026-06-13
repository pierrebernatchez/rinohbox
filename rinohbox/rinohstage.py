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

SAFEPRIFIX="rinohb"
SAFESUFFIX="dblchk"
def preparestage(stagedir):
    """Create the subdirectories required by the rinoh-rendering staging
    subdirectory and transfer the .py files it needs there.
    The .py files are pulled out of the rinohbox package library.
    """ 
    src = resources.files('rinohbox') # / 'conf.py'
    conf_file_src = src / 'rinohconf.py'
    conf_file_dst = stagedir / 'conf.py'
    temp_file_src = src / 'rinoh_article_template.py'
    temp_file_dst = stagedir / 'rinoh_article_template.py'
    print(f"src={conf_file_src} dest={conf_file_dst}", file=sys.stderr)
    shutil.copy(conf_file_src, conf_file_dst)
    print(f"src={temp_file_src} dest={temp_file_dst}", file=sys.stderr)
    shutil.copy(temp_file_src, temp_file_dst)
    subdir= stagedir / "_static"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= stagedir / "_templates"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= stagedir / "out"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
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
    keepers=(
        "_templates",
        "_static",
        "conf.py",
        "out",
        "rinoh_article_template.py")
    for entry in os.scandir(staging):
        if entry.name in keepers:
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
    """Entry point for creating a new rinohbox staging area directory"""
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    if len(sys.argv) > 1:
        parser.error("This command takes no arguments")    
    stagedir= do_newstage()
    print(f"{stagedir}")
    exit(0)

def clearstage():
    """Remove all but what files and directories it began with from staging directory."""
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
    """Recursively removes a staging directory.  But its name must match prefix and suffix."""
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

script_name = os.path.basename(__file__)
if __name__ == '__main__':
    print(f"{script_name}: This module is not intended to be used directly, but imported.")
    exit(1)

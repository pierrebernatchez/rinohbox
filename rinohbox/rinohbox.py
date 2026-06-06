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

def preparebox(target):
    """Transfer the .py files we need to the target directory"""
    src = resources.files('rinohbox') # / 'conf.py'
    conf_file_src = src / 'rinohconf.py'
    conf_file_dst = target / 'conf.py'
    temp_file_src = src / 'rinoh_article_template.py'
    temp_file_dst = target / 'rinoh_article_template.py'
    print(f"src={conf_file_src} dest={conf_file_dst}", file=sys.stderr)
    shutil.copy(conf_file_src, conf_file_dst)
    print(f"src={temp_file_src} dest={temp_file_dst}", file=sys.stderr)
    shutil.copy(temp_file_src, temp_file_dst)
    subdir= target / "_static"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= target / "_templates"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    subdir= target / "out"
    print(f"Making directory: {subdir}", file=sys.stderr)
    subdir.mkdir()
    return

def do_cleanbox(target):
    """Clean out an existing rinohbox directory for re-use"""
    # get rid of .rst files in target and all files in target/out
    for f in Path(target).glob('*.rst'):
        f.unlink()
    outdir = Path(target) / Path('out')
    for f in Path(outdir).glob('*'):
        f.unlink()
    return target

def do_newbox():
    """Create and initialize a temp directory to be used as sandbox for rendering with rinoh"""
    tmpdir = tempfile.mkdtemp()    
    fulltarget = Path(tmpdir).resolve()
    preparebox(fulltarget)    
    return fulltarget

def cleanbox():
    """Clean out the contents of a rinohbox for re-use"""
    parser = argparse.ArgumentParser()
    parser.add_argument('rinohboxdir', nargs=1, help='RST files to process.')
    args = parser.parse_args()
    target = do_cleanbox(args.rinohboxdir[0])
    print(f"{target}")
    exit(0)
    
def newbox():
    """Create and initialize a temp directory to be used as sandbox for rendering with rinoh"""
    boxdir = do_newbox()
    print(f"{boxdir}")
    exit(0)


script_name = os.path.basename(__file__)
if __name__ == '__main__':
    print(f"{script_name}: This module is not intended to be used directly, but imported.")
    exit(1)

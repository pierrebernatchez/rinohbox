#!/usr/bin/env bash
#
set -euo pipefail
#
# bash trick to obtain a clean absolute path to this script.
#
pushd `dirname $0` >/dev/null
SCRIPTPATH=`pwd -P`
popd >/dev/null
#
#
MYPNAME=$(basename ${0})
# change the value of these to your specific circumstances
SOMENAME=rinohbox
REPOBASE=${HOME}/repos
GITREPO="git@github.com:pierrebernatchez/rinohbox.git"
#

source ./colorsource

# Get started making your repository called somename
# Clone the starter template and make it into your own repository
pnameit $(inform How to get started making your own repository called ${SOMENAME} )
pnameit $(inform "-------------------------------------" )
pnameit $(inform  Change SOMENAME GITREPO and REPOBASE inside this script. )
pnameit $(inform  You want "${MYPNAME}" to show what you need instead of ${SOMENAME}, )
pnameit $(inform  ${GITREPO} and ${REPOBASE} ) 
pnameit $(inform  Then rerun "${MYPNAME}" and follow the instructions )
pnameit $(inform "-------------------------------------" )
pnameit $(warning  On github:)
pnameit $(inform "-------------------------------------" )
pnameit $(emphasize  You start by logging in to your github console.)
pnameit $(emphasize  On the console you create a new empty repository called \"${SOMENAME}\")
pnameit $(fatal  JUST EMPTY DO NOT ADD ANYTHING)
pnameit $(inform "-------------------------------------" )
pnameit $(warning  On your workstation:)
pnameit $(inform "-------------------------------------" )
pnameit $(emphasize  Create a starter setup like this:)
pnameit $(codeblockify  cd ${REPOBASE}/)
pnameit $(codeblockify  cd ${SOMENAME}/)
pnameit $(emphasize  create a .gitignore file)
pnameit $(emphasize  create a README.md and any other files you need)
pnameit $(emphasize  Upload this as your new repository content like this:)
pnameit $(codeblockify  git init -b main)
pnameit $(codeblockify  git add .)
pnameit $(codeblockify  git commit -m \"First Commit\")
pnameit $(codeblockify  git remote add origin ${GITREPO})
pnameit $(codeblockify  git push --set-upstream origin main)
pnameit $(inform "-------------------------------------" )
pnameit $(emphasize  Begin adding site directories and content$ directories as you want)






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
pnameit $(info How to get started making your own repository called ${SOMENAME} )
pnameit $(info "-------------------------------------" )
pnameit $(info  Change SOMENAME GITREPO and REPOBASE inside this script. )
pnameit $(info  You want "${MYPNAME}" to show what you need instead of ${SOMENAME}, )
pnameit $(info  ${GITREPO} and ${REPOBASE} ) 
pnameit $(info  Then rerun "${MYPNAME}" and follow the instructions )
pnameit $(info "-------------------------------------" )
pnameit $(warn  On github:)
pnameit $(info "-------------------------------------" )
pnameit $(emph  You start by logging in to your github console.)
pnameit $(emph  On the console you create a new empty repository called \"${SOMENAME}\")
pnameit $(fatal  JUST EMPTY DO NOT ADD ANYTHING)
pnameit $(info "-------------------------------------" )
pnameit $(warn  On your workstation:)
pnameit $(info "-------------------------------------" )
pnameit $(emph Create a starter setup like this:)
pnameit $(code mkdir -p ${REPOBASE}/${SOMENAME})
pnameit $(code cd ${REPOBASE}/${SOMENAME})
pnameit $(emph create a .gitignore file)
pnameit $(emph create a README.md and any other files you need)
pnameit $(emph Upload this as your new repository content like this:)
pnameit $(code  git init -b main)
pnameit $(code  git add .)
pnameit $(code  git commit -m \"First Commit\")
pnameit $(code  git remote add origin ${GITREPO})
pnameit $(code  git push --set-upstream origin main)
pnameit $(info "-------------------------------------" )
pnameit $(emph  Begin maintaining the project content as and when required)






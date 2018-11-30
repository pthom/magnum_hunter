#!/usr/bin/env bash

set -x # echo on
set -e # exit on error

THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
MAINREPODIR=$THISDIR/..

cd $MAINREPODIR/polly
export PATH="`pwd`/bin:$PATH"

cd $MAINREPODIR/hunter
# polly.py --help
TOOLCHAIN=osx-10-14 PROJECT_DIR=examples/magnum ./jenkins.py

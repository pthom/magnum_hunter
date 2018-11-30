#!/usr/bin/env bash

set -x

THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
MAINREPODIR=$THISDIR/..

cd $MAINREPODIR/magnum
git remote add upstream git@github.com:mosra/magnum.git
git fetch origin
git checkout origin/magnum_hunter -b magnum_hunter


cd $MAINREPODIR/hunter
git remote add upstream git@github.com:ruslo/hunter.git
git fetch origin
git checkout origin/test.magnum -b test.magnum

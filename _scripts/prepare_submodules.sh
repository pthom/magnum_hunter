#!/usr/bin/env bash

set -x

THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
MAINREPODIR=$THISDIR/..

cd $MAINREPODIR/magnum
git remote add upstream git@github.com:mosra/magnum.git
git remote add wip git@github.com:pthom/magnum.git
git remote rm origin
git fetch wip
git checkout wip/magnum_hunter -b magnum_hunter


cd $MAINREPODIR/hunter
git remote add upstream git@github.com:ruslo/hunter.git
git remote add wip git@github.com:pthom/hunter.git
git remote rm origin
git fetch wip
git checkout wip/test.magnum -b test.magnum
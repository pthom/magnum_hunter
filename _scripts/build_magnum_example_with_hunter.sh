#!/usr/bin/env bash

set -x # echo on
set -e # exit on error

THISDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
MAINREPODIR=$THISDIR/..

cd $MAINREPODIR/magnum_example_app
if [[ ! -d build ]]; then
  mkdir build
fi
cd build
cmake .. -GNinja -DHUNTER_ENABLED=ON
ninja

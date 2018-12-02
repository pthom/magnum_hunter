docker run --rm -it -v $(pwd)/../..:/sources_docker gcc8_2_builder \
  /bin/zsh -c \
  "
  export LC_ALL=C.UTF-8
  export LANG=C.UTF-8
  rm -rf build.corrade
  export CXXFLAGS=\"-std=c++17\"
  ./TLDR_hunter.py test-build corrade
  "

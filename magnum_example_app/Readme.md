An example magnum program built using hunter

It uses hunter the way that is described in the hunter docs

* Except* for the fact that for the moment it -build the hunter packages from submodules
  (see magnum_example_app/cmake/Hunter/config.cmake)


├── CMakeLists.txt
├── PrimitivesExample.cpp
├── Readme.md
├── cmake
│   ├── Hunter
│   │   └── config.cmake           # will build corrade and magnum from those symlinks
│   └── HunterGate.cmake
└── third_party
    ├── corrade -> ../../corrade   # symlinks
    └── magnum -> ../../magnum
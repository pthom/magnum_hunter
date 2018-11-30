An example magnum program built using hunter

It uses hunter the way that is described in the hunter docs except* for the fact that it builds the hunter packages from submodules (see magnum_example_app/cmake/Hunter/config.cmake)


├── CMakeLists.txt                # The LOCAL param inside the HunterGate
├── PrimitivesExample.cpp         # will cause cmake/Hunter/config.cmake to be read
├── Readme.md
├── cmake
│   ├── Hunter
│   │   └── config.cmake           # specifies to build corrade and magnum from submodules
│   └── HunterGate.cmake
└── third_party
    ├── corrade -> ../../corrade   # symlinks
    └── magnum -> ../../magnum

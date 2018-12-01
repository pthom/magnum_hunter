An example magnum program built using hunter

It uses hunter the way that is described in the hunter docs except* for the fact that it builds the hunter packages from submodules (see magnum_example_app/cmake/Hunter/config.cmake)


````
├── CMakeLists.txt                # The LOCAL param inside the HunterGate() call inside CMakeLists.txt
├── PrimitivesExample.cpp         # will cause cmake/Hunter/config.cmake to be read
├── Readme.md
├── cmake
│   ├── Hunter
│   │   └── config.cmake           # specifies to build corrade and magnum from submodules
│   └── HunterGate.cmake
└── third_party
    ├── corrade -> ../../corrade   # symlinks
    └── magnum -> ../../magnum
````

`CMakeLists.txt`:

````cmake
include("cmake/HunterGate.cmake")
HunterGate(
    URL "https://github.com/pthom/hunter/archive/pr.magnum.v1.tar.gz"
    SHA1 "c19e05f8999e7aed6399b8c15a7006fdc750e41b"
    LOCAL # <----- load cmake/Hunter/config.cmake
)
project(MagnumPrimitivesExample)
hunter_add_package(magnum)
````

`cmake/Hunter/config.cmake`:

````cmake
hunter_config(corrade GIT_SUBMODULE "corrade")
hunter_config(magnum GIT_SUBMODULE "magnum" CMAKE_ARGS WITH_OBJIMPORTER=ON)
````

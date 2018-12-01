## An example magnum program built using hunter

It uses hunter the way that is described in the hunter docs except* for the fact that it builds the hunter packages from submodules (see magnum_example_app/cmake/Hunter/config.cmake)

### Structure

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


### Steps :

* Fetch HunterGate.cmake from `https://github.com/hunter-packages/gate/blob/master/cmake/HunterGate.cmake`
  and copy it to `cmake/HunterGate.cmake`
* Inside `CMakeLists.txt`, just add this in order to get magnum
````cmake
include("cmake/HunterGate.cmake")
HunterGate(
    URL "https://github.com/ruslo/hunter/archive/v2018.12.tar.gz"
    SHA1 "c19e05f8999e7aed6399b8c15a7006fdc750e41b")
    LOCAL # <----- load cmake/Hunter/config.cmake
project(MagnumPrimitivesExample)
hunter_add_package(magnum)
````
You will need to adjust the correct url and sha1 (see https://docs.hunter.sh/en/latest/packages/all.html)
The LOCAL params means that you intend to add some configuration options.

### Configuration

* Inside `cmake/Hunter/config.cmake` adjust your configuration

If you want to fetch magnum from a submodule (instead of using the standard hunter releaqe), write this
````cmake
hunter_config(corrade GIT_SUBMODULE "corrade")
hunter_config(magnum GIT_SUBMODULE "magnum" CMAKE_ARGS WITH_OBJIMPORTER=ON)
````

Note : after CMAKE_ARGS, you can alter the magnum cmake flags.


If you only want to modify the CMAKE_ARGS and specify the version, you can write:

````cmake
hunter_config(magnum VERSION v2018.12 CMAKE_ARGS WITH_AUDIO=OFF)
````

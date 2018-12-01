An example magnum program built using hunter

It uses hunter the way that is described in the hunter docs (and it uses the default packages,
and thus may used cached binaries from an artifactory)


````
├── CMakeLists.txt
├── PrimitivesExample.cpp
├── Readme.md
├── cmake
│   └── HunterGate.cmake
````

`CMakeLists.txt`:

````cmake
include("cmake/HunterGate.cmake")
HunterGate(
    URL "https://github.com/pthom/hunter/archive/pr.magnum.v1.tar.gz"
    SHA1 "c19e05f8999e7aed6399b8c15a7006fdc750e41b")
project(MagnumPrimitivesExample)
hunter_add_package(magnum)
````

## An example magnum program built using hunter

It uses hunter the way that is described in the hunter docs : it uses the default packages,
and thus may used cached binaries from an artifactory.


````
├── CMakeLists.txt
├── PrimitivesExample.cpp
├── Readme.md
├── cmake
│   └── HunterGate.cmake
````

### Steps :

* Fetch HunterGate.cmake from `https://github.com/hunter-packages/gate/blob/master/cmake/HunterGate.cmake`<br/>
  and copy it to `cmake/HunterGate.cmake`
* Inside `CMakeLists.txt`, just add this in order to get magnum

````cmake
include("cmake/HunterGate.cmake")
HunterGate(
    URL "https://github.com/ruslo/hunter/archive/v2018.12.tar.gz"
    SHA1 "c19e05f8999e7aed6399b8c15a7006fdc750e41b")
project(MagnumPrimitivesExample)
hunter_add_package(magnum)
````

Note: <br/>
You will need to adjust the correct url and sha1 (see https://docs.hunter.sh/en/latest/packages/all.html)

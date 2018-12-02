# magnum_hunter

Tooling to help building magnum and corrade hunter packages.

````
.
├── Readme.md
├── TLDR_hunter.py       # tool that tries to simplify hunter usage
├── TODO.md
├── _scripts
├── corrade/             # clone of corrade (no modifications)
├── hunter/              # fork of hunter (with several hunter and corrade related branches)
├── magnum/              # fork of magnum with several patches
|
├── magnum_example_app/  # An example application that builds using hunter
|   ├── CMakeLists.txt   # and the standard magnum & corrade packages
|   ├── PrimitivesExample.cpp
|   ├── Readme.md
|   ├── cmake
|   │   └── HunterGate.cmake
├── magnum_example_app_with_submodules/ # An example application that builds using hunter
|   ├── CMakeLists.txt                  # and which is based on the corrade/ and magnum/
|   ├── PrimitivesExample.cpp           # versions in this repo (good for local tests)
|   ├── Readme.md
|   ├── cmake
|   │   ├── Hunter
|   │   │   └── config.cmake            # this is where you specify the usage of magnum and
|   |   |                               # corrade as submodules (and you can add build options to magnum)
|   │   └── HunterGate.cmake
|   └── third_party/
|        ├── corrade -> ../../corrade
|        └── magnum -> ../../magnum
├── polly/                              # clone of polly (hunter toolchains,lots of them)
|   ├── gcc-7-cxx17.cmake
|   ├── gcc-8-cxx14-fpic.cmake
|   ├── gcc-cxx17-c11.cmake
|   ├── gcc-gold.cmake
|   ├── ios-10-1-dep-8-0-hid-sections.cmake
|   ├── etc...
|   ├── etc...
|   ├── etc...
|   ├── bin/
|        ├── polly*                      # this tool is used in the hunter build process
|        └── polly.bat
|        └── polly.py*
└── travis-hunter-master.yml
````

## Magnum related code inside Hunter:

````bash
hunter/cmake/projects/magnum/
                            └── hunter.cmake
hunter/docs/packages/pkg/magnum.rst
hunter/examples/magnum/
                      ├── CMakeLists.txt
                      └── PrimitivesExample.cpp
````



## Tooling / TLDR_Hunter.py

`TLDR_hunter.py` is a tool that tries to simplify some of the manual actions described at
  https://docs.hunter.sh/en/latest/creating-new/create/cmake.html

*Prerequisites*
* python 3
* Install "hub" (github command line client) : https://github.com/github/hub
* Install click : pip install click


````bash


TLDR_hunter.py test-build PROJECT_NAME [TOOLCHAIN]

  Helps to build a project using hunter.

  The project must be a subfolder of this repo).
  Basically it does this:

  \b
  export PATH=$(pwd)/polly/bin:$PATH
  mkdir build.project_name
  cd build.project_name
  polly.py --home --toolchain toolchain  # polly.py is a building script provided by polly

  \b
  Notes:
  * polly.py selects automatically the correct cmake generator according to the toolchain
  * Use `hunter-list-toolchains --filter` in order to find the available toolchains
  * if you want to use the toolchains manually, do:
  > cmake your/src/folder -DCMAKE_TOOLCHAIN_FILE=path/to/polly/toolchain.cmake

*************

TLDR_hunter.py project-create-release PROJECT_NAME TARGET_BRANCH RELEASE_NAME

  Creates a release on github for a project and optionally publish it to
  hunter
  Steps:
  * Creates a github release for a project (which must be subfolder of this repo)
  * Compute the sha1 of this release
  * Optionally add this release to hunter/cmake/project/project_name/hunter.cmake
  * Optionally make this release default in hunter/cmake/configs/defaults.cmake

**************

TLDR_hunter.py hunter-create-release RELEASE_NAME

  Publish a release on your hunter fork and assist you to use this hunter
  release in a sample app

````

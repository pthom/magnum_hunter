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


## TODO

* [X] Corrade hunter package
  * [X] Build and test package on all platforms<br/>
    See https://travis-ci.org/pthom/hunter/builds/462197201 and <br/> https://ci.appveyor.com/project/pthom/hunter/builds/20699264
    * [X] Correct pb / docs (badly configured spell-checker in hunter !)
    * [X] Re-enable build Android & iOS via hunter
        * [X] Build native corrade-rc<br/>
        -> Done with the addition of a script magnum-build-corrade-rc.sh to hunter
        (I do not know if this will be accepted)
        * [X] Build iOS and android in the hunter CI for corrade
  * [ ] Push PR to hunter (and hope that the hack for corrade-rc will pass)

* [X] Magnum hunter package
  * [X] Status :<br/>
    https://travis-ci.org/pthom/hunter/builds/462213975<br/>
    and<br/>
    https://ci.appveyor.com/project/pthom/hunter/builds/20700057
  * [X] Decide about default packages<br/>
      See https://github.com/pthom/hunter/blob/pr.magnum/cmake/projects/magnum/hunter.cmake<br/>
      I took inspiration from the various magnum packages. It proved to be way too difficuly to try
      to find a set of common options for all the platforms, so that it is separated per platform.
  * [X] Check Magnum correct CI compilation inside Hunter
    * [X] OSX / Linux
    * [X] Windows<br/>
      However, I had to disable the sound in windows because of an issue in hunter's `OpenAL`
      package. Hopefuly someone will fix this in the near future.
    * [ ] Cross-Compilation
      * [X] Build native corrade-rc
      * [ ] Build Android -> Fail<br/>
          See https://travis-ci.org/pthom/hunter/jobs/462202107
          ````bash
          CMake Error at cmake/Magnum/FindMagnum.cmake:839 (find_package):
          By not providing "FindOpenGLES3.cmake" in CMAKE_MODULE_PATH this project
          has asked CMake to find a package configuration file provided by
          "OpenGLES3", but CMake did not find one.
          Could not find a package configuration file provided by "OpenGLES3" with
          any of the following names:
            OpenGLES3Config.cmake
            opengles3-config.cmake
          ````
      * [ ] build iOS -> Fail<br/>
      See https://travis-ci.org/pthom/hunter/jobs/462202114
      ````bash
      [hunter ** FATAL ERROR **] 'find_package(EGL)' should be called with REQUIRED
      ...
      /cmake/modules/hunter_find_helper.cmake:59 (hunter_user_error)
      /cmake/find/FindEGL.cmake:5 (hunter_find_helper)
      src/Magnum/Platform/CMakeLists.txt:717 (find_package)
      ````
      I think I will give up on this, unless you have some good clues.
      However, the situation as it is is acceptable,
      since I left some explanations, and another person can hande this in the future.

* [ ] Magnum issues:
  * [ ] Investigate GlyphCache issue
  * [ ] Investigate error with TOOLCHAIN=sanitize-address-cxx17
    cf https://travis-ci.org/pthom/hunter/jobs/461801690
  * [ ] Report error in magnum/package/archlinux/*emscripten* :
    `-WDITH_WINDOWLESSEGLAPPLICATION` instead of `-DWITH_WINDOWLESSEGLAPPLICATION`


* [X] Magnum_hunter: Push this repo
  * [X] Test this repo from scratch on an empty docker linux box
  * [X] Make doc & prepare PR magnum
    * [X] Explain how to add options to the magnum package build
  * [X] cli TL_DR


## Info about hunter branching model

````
  Info about hunter branching model:
    * branch test.project_name = this branch contains all the modifications
      (packages and version + appveyor/travis CI scripts)
      This branch can be pushed to your own fork of hunter, so that you can test
      the build through Appveyor and Travis.
      This is the branch where you work & do your commits, and where you can test the CI
    * branch pr.project_name = pull request candidate for hunter repo
            (https://github.com/ruslo/hunter)
            This is the same aa the branch test.project_name except for the
            files appveyor.yml and .travis.yml.
    * branch pr.pkg.project_name = pull request candidate for hunter package testing templates
            (https://github.com/ingenue/hunter)
            this branch shall contains only modifications to appveyor.yml and .travis.yml
````


## Tooling / TLDR_Hunter.py

`TLDR_hunter.py` is a tool that tries to simplify some of the manual actions described in
  https://docs.hunter.sh/en/latest/creating-new/create/cmake.html

*Prerequisites*
* Install "hub" (kind of github command line client : https://github.com/github/hub)
* Install click : pip install click


````bash

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

*************

TLDR_hunter.py hunter-test-build PROJECT_NAME TOOLCHAIN

  Builds a project inside hunter using the given toolchain

  Basically it does this :
    > export PATH=$PATH:$(pwd)/polly/bin
    > cd hunter
    > TOOLCHAIN=toolchain PROJECT_DIR=examples/project_name jenkins.py

You can list the toolchains using
./TLDR_hunter.py hunter-list-toolchains
````

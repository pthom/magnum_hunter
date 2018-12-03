## TODO


* [ ] Corrade hunter package
  * [ ] Hunter CI Back to travis ? (requires quite some boilerplate commits). What is your opinion?
  * [ ] Create a release on corrade main repo
  * [ ] Add the release link and it's sha1 to hunter / make it the default and only version
  * [ ] Push PR to hunter (and hope that the hack for corrade-rc will pass)
  * [ ] Proof read the readme inside hunter
  * [ ] Push PR to hunter building repo
        (and hope that the hack for corrade-rc will pass)
  * [ ] Push PR to hunter main repo

* [ ] Magnum hunter package
  * [ ] Hunter CI Back to travis ? (requires quite some boilerplate commits)
  * [ ] Merge magnum_hunter branch
  * [ ] Create a release on corrade main repo
  * [ ] Add the release link and it's sha1 to hunter / make it the default and only version
  * [ ] Proof read the readme inside hunter
  * [ ] Push PR to hunter building repo
        (and hope that the hack for corrade-rc will pass)
  * [ ] Push PR to hunter main repo

* Magnum
  * [ ] Integrate example_apps into magnum-bootstrap ?
  * [ ] What to do about the magnum_hunter repo itself (which can be useful for future maintainers of the hunter package, or people wanting to add hunter plugins)

* [X] Magnum hunter package
  * [ ] Push PR to hunter (and hope that the hack for corrade-rc will pass)
    * [ ] This require to have another magnum release where some small patches are applied (see below)
  * [ ] Status :<br/>
  * [ ] Check default packages<br/>
  * [X] Check Magnum correct CI compilation inside Hunter
    * [X] OSX / Linux
    * [X] Windows<br/>
      However, I had to disable the sound in windows because of an issue in hunter's `OpenAL`
      package. Hopefuly someone will fix this in the near future.
    * [X] sanitizers : cxx analyze / sanitize-address -> disable (problem inside SDL2 actually)
    * [ ] Re-enable build mingw and msys
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

* [ ] Magnum repo:
  * [ ] Merge hunter related modifications ?
    See https://github.com/mosra/magnum/compare/master...pthom:magnum_hunter?
  * [X] Investigate GlyphCache issue
  * [X] Report error in magnum/package/archlinux/*emscripten* :
    `-WDITH_WINDOWLESSEGLAPPLICATION` instead of `-DWITH_WINDOWLESSEGLAPPLICATION`


* [X] magnum_hunter repo<br/>
  * [X] Add tool to help building the packages (https://github.com/pthom/magnum_hunter)
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

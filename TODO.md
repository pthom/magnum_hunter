
* [X] Magnum_hunter: Push this repo
  * [X] Test this repo from scratch on an empty docker linux box
  * [ ] Make doc & prepare PR magnum
    * [ ] Explain how to add options to the magnum package build
    * [X-] Decide about default packages
    See https://github.com/pthom/hunter/blob/pr.magnum/cmake/projects/magnum/hunter.cmake

  * [X] cli to open hunter CI (travis & appveyor) in the browser

* [X] Corrade / Full OK
  See https://travis-ci.org/pthom/hunter/builds/462197201 and https://ci.appveyor.com/project/pthom/hunter/builds/20699264
  * [X] Correct pb / docs (badly configured spell-checker in hunter !)
  * [X-] Re-enable build Android & iOS via hunter
      * [X] Build native corrade-rc
      -> Done with the addition of a script magnum-build-corrade-rc.sh to hunter
      (I do not know if this will be accepted)
      * [X] Build iOS and android in the hunter CI for corrade

* [X] Magnum
  * [X] Check Magnum correct CI compilation inside Hunter
    * [X] Windows /OSX / Linux (had to disable sound in windows because of an issue in hunter)
    * [] Cross-Compilation
      * [X] Build native corrade-rc
      * [NO] Re-enable build Android
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
      * [NO] Re-enable build iOS:
      See https://travis-ci.org/pthom/hunter/jobs/462202114
      ````bash
      [hunter ** FATAL ERROR **] 'find_package(EGL)' should be called with REQUIRED
      ...
      /cmake/modules/hunter_find_helper.cmake:59 (hunter_user_error)
      /cmake/find/FindEGL.cmake:5 (hunter_find_helper)
      src/Magnum/Platform/CMakeLists.txt:717 (find_package)
      ````

  * [ ] Investigate GlyphCache issue
    * [ ] Give clues on hunter CI
    * [ ] Give clues in this tool

  * [ ] Investigate error with TOOLCHAIN=sanitize-address-cxx17
    cf https://travis-ci.org/pthom/hunter/jobs/461801690

  * [] error in all magnum/package/archlinux/PKGBUILD-emscripten*:
    -WDITH_WINDOWLESSEGLAPPLICATION=ON

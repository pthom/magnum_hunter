# Copyright (c) 2015, Ruslan Baratov
# All rights reserved.

cmake_minimum_required(VERSION 3.2)

# The part below is adapted from
# https://github.com/mosra/magnum-examples/blob/master/src/primitives/CMakeLists.txt

# CMake policies. 0025 needs to be before project(), so putting all there.
# Use AppleClang instead of Clang on Apple
if(POLICY CMP0025)
    cmake_policy(SET CMP0025 NEW)
endif()
# Don't treat imported targets with :: as files
if(POLICY CMP0028)
    cmake_policy(SET CMP0028 NEW)
endif()
# Enable MACOSX_RPATH by default
if(POLICY CMP0042)
    cmake_policy(SET CMP0042 NEW)
endif()
# Quoted variables should not be dereferenced
if(POLICY CMP0054)
    cmake_policy(SET CMP0054 NEW)
endif()

set(
    HUNTER_CACHE_SERVERS
    "https://github.com/elucideye/hunter-cache;https://github.com/ingenue/hunter-cache"
    CACHE
    STRING
    "Hunter cache servers"
)
include("cmake/HunterGate.cmake")
HunterGate(
    URL "https://github.com/pthom/hunter/archive/pr.magnum.v1.tar.gz"
    SHA1 "c19e05f8999e7aed6399b8c15a7006fdc750e41b"
    LOCAL # <----- load cmake/Hunter/config.cmake
)

project(MagnumPrimitivesExample)
hunter_add_package(magnum)

# Add module path in case this is project root
if(PROJECT_SOURCE_DIR STREQUAL CMAKE_SOURCE_DIR)
    set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/../../modules/")
endif()

find_package(Magnum CONFIG REQUIRED
    GL
    MeshTools
    Primitives
    Shaders
    Sdl2Application)

set_directory_properties(PROPERTIES CORRADE_USE_PEDANTIC_FLAGS ON)

add_executable(magnum-primitives PrimitivesExample.cpp)
target_link_libraries(magnum-primitives PRIVATE
    Magnum::Application
    Magnum::GL
    Magnum::Magnum
    Magnum::MeshTools
    Magnum::Primitives
    Magnum::Shaders)

install(TARGETS magnum-primitives DESTINATION ${MAGNUM_BINARY_INSTALL_DIR})
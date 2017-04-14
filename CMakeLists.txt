cmake_minimum_required(VERSION 2.8.11)
project(diffscraper)

find_package( PythonLibs 3 REQUIRED )
include_directories( ${PYTHON_INCLUDE_DIRS} )

find_package( Boost COMPONENTS python REQUIRED )
#find_package( Boost COMPONENTS python3 REQUIRED )
include_directories( ${Boost_INCLUDE_DIR} )

add_subdirectory(src/native)


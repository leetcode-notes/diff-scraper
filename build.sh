#!/bin/bash
if [ ! -d "build" ]; then
    mkdir build
fi

if [ -d "build" ]; then
    pushd build
    cmake ..
    make clean
    make all
    popd
fi


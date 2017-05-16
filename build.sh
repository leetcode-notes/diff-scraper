#!/bin/bash
echo -e '\033[1;31mNative module is not supported yet.\033[0m'
echo -e '$ \033[1;32mpython3 -m diffscraper.main\033[0m'

exit

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


#!/bin/bash
if [ -f test.sh ]; then
    echo "run from the parent directory"
    exit 1
fi
if ! docker image ls | grep -q "^p2fa_example3 "; then
    echo "couldn't find docker image p2fa"
    exit 1
fi
docker run -it --rm -v ./test:/mount -v .:/m p2fa_example3 python /m/alignx.py CarrieFisher10s.wav CarrieFisher10s.tdf
cd test
diff CarrieFisher10s.align.ref CarrieFisher10s.tdf.align
diff CarrieFisher10s.words.ref CarrieFisher10s.tdf.words
diff CarrieFisher10s.unks.ref CarrieFisher10s.tdf.unks
# cd ..
# docker run -it --rm -v ./test:/mount -v .:/m p2fa_example3 python /m/alignx.py -g CarrieFisher10s.wav CarrieFisher10s.tdf
# cd test
# diff CarrieFisher10s.TextGrid.example1 CarrieFisher10s.TextGrid


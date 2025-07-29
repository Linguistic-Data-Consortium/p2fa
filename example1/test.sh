#!/bin/bash
if [ -f test.sh ]; then
    echo "run from the parent directory"
    exit 1
fi
if ! docker image ls | grep -q ^p2fa_example1; then
    echo "couldn't find docker image p2fa_example1"
    exit 1
fi
docker run -it --rm -v ./test:/mount p2fa_example1 python /app/aligner/align.py CarrieFisher10s.wav CarrieFisher10s.txt CarrieFisher10s.TextGrid
diff test/CarrieFisher10s.TextGrid.example1 test/CarrieFisher10s.TextGrid

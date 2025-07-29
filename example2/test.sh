#!/bin/bash
if [ -f test.sh ]; then
    echo "run from the parent directory"
    exit 1
fi
if ! docker image ls | grep -q ^p2fa_example2; then
    echo "couldn't find docker image p2fa_example2"
    exit 1
fi
docker run -it --rm -v ./test:/mount p2fa_example2 python /app/aligner/align_tdf.py CarrieFisher10s.wav CarrieFisher10s.tdf CarrieFisher10s.align CarrieFisher10s.words
cd test
cat CarrieFisher10s.{align,words,unks}.ref > CarrieFisher10s.t1
cat CarrieFisher10s.{align,words,unks}     > CarrieFisher10s.t2
diff CarrieFisher10s.t[12] > CarrieFisher10s.t3
diff diff.example2 CarrieFisher10s.t3
rm CarrieFisher10s.t?


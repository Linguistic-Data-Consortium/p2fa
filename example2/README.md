# Example 2

This example uses p2fa with different I/O formats, and also handles unknown words
with the `g2p-en` python package.  It's only relevant to people who may have used this code or one of the many similar versions that were used at Penn.

You can build the image as follows; here we tag it with p2fa_example2.

    docker build -f example2/Dockerfile -t p2fa_example2 .

You can test the code as follows:

    docker run -it --rm -v ./test:/mount p2fa_example2 python /app/aligner/align_tdf.py CarrieFisher10s.wav CarrieFisher10s.tdf CarrieFisher10s.align CarrieFisher10s.words

This mounts the local `test` dir onto the working directory of the container, `/mount`, and runs the aligner on the test audio and transcript.  The output is nearly identical to the test output of example3 which uses Phonetisaurus, only differing on the one unknown word, Leia.  The differences can be seen in `test/diff.example2`.  The differences to Example 3 were saved rather than Example 2 reference files, since most people won't be interested in Example 2.  The test is automated with:

    example2/test.sh

If successful, there won't be any diff output, only two output lines from `align_tdf.py`.  See the test script if necessary.


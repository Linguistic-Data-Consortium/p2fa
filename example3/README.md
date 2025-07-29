# Example 3

This example uses the same p2fa models, but includes various updates to the wrapping code, including using Phonetisaurus for unknown words.  See the Details section below.

You can build the image as follows; here we tag it with p2fa.

    docker build -f example3/Dockerfile -t p2fa .

You can test the code as follows:

    docker run -it --rm -v ./test:/mount p2fa python /app/aligner/alignx.py CarrieFisher10s.wav CarrieFisher10s.tdf

This mounts the local `test` dir onto the working directory of the container, `/mount`, and runs the aligner on the test audio and transcript.  The output should be identicial to the reference files, so the following should produce no output:

    diff test/CarrieFisher10s.align.ref test/CarrieFisher10s.align
    diff test/CarrieFisher10s.words.ref test/CarrieFisher10s.words
    diff test/CarrieFisher10s.unks.ref test/CarrieFisher10s.unks

This test and several others are automated with:

    example3/test.sh

# Details




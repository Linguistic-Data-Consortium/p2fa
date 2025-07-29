# Example 1

This example uses the aligner as available from Penn Phonetics.

You can build the image as follows; here we tag it with p2fa_example1.

    docker build -f example1/Dockerfile -t p2fa_example1 .

You can test the code as follows:

    docker run -it --rm -v ./test:/mount p2fa_example1 python /app/aligner/align.py CarrieFisher10s.wav CarrieFisher10s.txt CarrieFisher10s.TextGrid

This mounts the local `test` dir onto the working directory of the container, `/mount`, and runs the aligner on the test audio and transcript.  The output should be identicial to the reference file, so the following should produce no output:

    diff test/CarrieFisher10s.TextGrid.example1 test/CarrieFisher10s.TextGrid

For convenience, these commands can be run with:

    example1/test.sh




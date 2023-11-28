# Example 2

This example uses p2fa with different I/O formats, and also handles OOV
with the `g2p-en` python package.

This example uses the aligner as available from Penn Phonetics.
You need the "htk" and "model" directories.  The recipe makes a slight
change to the dictionary, assuming the Penn Phonetics version.  If you happen to
already have a modified dictionary, you should comment out the patch
line in the Dockerfile.  This example provides a different python script,
rather than using the Penn Phonetics script.

You can build the image as follows; here we tag it with p2fa_example2.

    docker build -t p2fa_example2 .

One way to run the aligner from the image would be 

    docker run -it --rm -v ~/dockermount:/mount p2fa_example2

Before running this, a local directory `~/dockermount` was created with an audio
file `foo.wav` and a transcript `foo.tdf`; `foo.align`, `foo.words`, and `foo.unks` go to the same directory.
See the default command in the Dockerfile, which uses `/mount` as the working directory.
You can model other commands off of the default command.  For example, if you have files named `bar` instead, you could do

    docker run -it --rm -v ~/dockermount:/mount p2fa_example2 python3 /app/aligner/align_tdf.py bar.wav bar.tdf bar.align bar.words


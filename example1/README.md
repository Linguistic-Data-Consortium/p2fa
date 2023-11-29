# Example 1

This example uses the aligner as available from Penn Phonetics.

You can build the image as follows; here we tag it with p2fa_example1.

    docker build -f example1/Dockerfile -t p2fa_example1 .

One way to run the aligner from the image would be 

    docker run -it --rm -v ~/dockermount:/mount p2fa_example1

Before running this, a local directory `~/dockermount` was created with an audio
file `foo.wav` and a transcript `foo.txt`; `foo.TextGrid` goes to the same directory.
See the default command in the Dockerfile, which uses `/mount` as the working directory.
You can model other commands off of the default command.  For example, if you have files named `bar` instead, you could do

    docker run -it --rm -v ~/dockermount:/mount p2fa_example1 python /app/aligner/align.py bar.wav bar.txt bar.TextGrid


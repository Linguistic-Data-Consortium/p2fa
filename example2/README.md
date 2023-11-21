# example2
aligner variant used on TDF files

# Instructions

The docker file expects "htk" and "model" directories.  The model directory
should be as found in the published aligner, and the recipe will make
a slight alteration of the dictionary inside the image.  The included
python script runs the aligner with a TDF transcript file.

You can build the image as follows; here we tag it with p2fa_example2.

    docker build -t p2fa_example2 .

One way to run the aligner from the image would be 

    docker run -it --rm -v ~/dockermount:/mount p2fa_example2

Before running this, a local directory `~/dockermount` was created with an audio
file and a transcript.  The local directory could be anything, but the
default command in the dockerfile expects it to be mounted to `/mount`, and
expects files called `foo.wav` and `foo.tdf` in the local directory.  The label files are
written to the same local directory, called `foo.align` and `foo.words`.  You can model other commands off of the default command.  For example, if you have files named `bar` instead, you could do

    docker run -it --rm -v ~/dockermount:/mount p2fa_example2 python3 /app/aligner/align_tdf.py bar.wav bar.tdf bar.align bar.words

The aligner supplements the included dictionary by running g2p on any unknown words, and also produces a `.unk` file with those
unknown words.


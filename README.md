# p2fa

Code for working with the Penn Phonetics Lab Forced Aligner (p2fa)

# Introduction

The Penn Phonetics Lab Forced Aligner is still available from the Lab website:

    https://web.sas.upenn.edu/phonetics-lab/facilities/

From its documentation:

    P2FA can be cited as:
    Jiahong Yuan and Mark Liberman. 2008. Speaker identification on the SCOTUS corpus. Proceedings of Acoustics '08.

For full documentation, see that package.  This repo contains the primary components of p2fa and
additional code for working with it.  The following checksum file documents the exact zip file
from that website that was the basis for this repo:

    sums/Penn-Phonetics-forced-aligner-2d2jfwb.zip.md5

# Model Directory

The "model" directory, copied here from the Phonetics Lab release, contains
the model files for English, as well as a version of the CMU pronouncing dictionary,
documented with this checksum file:

    sums/model.md5

# HTK

HTK version 3.4.1 must be acquired separately.  Other version may work but haven't been tested.  The docker recipes assume the presence of the unpacked "htk" directory in the current directory.

# Docker Examples

This repo is designed to be used with docker, and contains several examples.  Each example contains a Dockerfile
and a readme with example commands, which are meant to be run from the current directory, not the example directories.
If you prefer not to use docker, the recipes serve as documentation for configuring your environment.  Most users should skip to Example 3, the most useful version, while Examples 1 and 2 are provided for historical reference.

## Example 1

Example 1 represents the aligner as available from Penn Phonetics.  See details in that [README](example1/README.md).

## Example 2

Example 2 represents one of the many updated, but now obsolete, versions used at Penn.  See details in that [README](example2/README.md).

## Example 3

Example 3 represents the current version, see that [README](example3/README.md).




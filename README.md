# ctcsound Example
This repository provides examples of how to use the ctcsound library in python, in order to use Csound with python.

## How to use this file
See ctcsound_example.py for an example of how to use the ctcsound library. Csound instruments and the score are written as strings (with normal Csound syntax) and then passed to the perform function.

### Markov Model
For an example of a Markov chain in music composition, see music_markov.py. This file contains 4 instruments, a simple tone, a "drum", a piano, and a thunder sound. For the tone and piano, the markov model is used to generate notes and the duration matrices are used to generate each duration. For the drum, only the duration matrix is used. For the thunder, the thunder sound is simply placed 4 times randomly in the entire duration. 

Probability matrices are from [this](https://github.com/haebichan/PopMusicMaker/tree/master/probability%20matrices) repository. The repository contains probability matrices based on input pop songs.


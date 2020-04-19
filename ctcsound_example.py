import ctcsound

REVERB = True

# Info on ctcsound: https://github.com/csound/ctcsound

ORC_SETTINGS = """
sr=44100
kr=4400
nchnls=2
0dbfs=1

gaverb init 0
"""

# basic tone
INSTR1 = """
; p4 is freq
; p5 is amplitude
instr 1
ifreq = p4
iamp = p5
kenv linseg 0, p3/8, 0.8, p3/4, 0.4, 5*p3/8, 0
asig1 oscil 0.2, ifreq
asig2 oscil 0.2, ifreq*2
asig3 oscil 0.2, ifreq*3
aout = (asig1 + asig2 + asig3)*kenv*iamp*0.5
gaverb	 =	gaverb+aout*0.1
outs aout, aout
endin
"""

# drum
INSTR2 = """
; p4 is amplitude
instr 2
iamp = p4
kenv linseg 0, 0.01, 1, 0.01, 0, p3 - 0.02, 0
asig rand 1
aout = asig*kenv*iamp
gaverb	 =	gaverb+aout*0.1
outs aout, aout
endin
"""

REVERB_INST = """
instr	99			
averb	reverb	gaverb,2
outs	averb, averb
gaverb	=  0		; reinitialize global reverb variable
endin
"""

INSTRUMENTS = [INSTR1, INSTR2]
SCORE_FUNCTIONS = "" # used for functions called in instruments

def create_orchestra(settings, instruments, reverb=REVERB):
    """
    Inputs:
        * settings: Csound settings, including sr, kr, nchnls, 
            and 0dbfs in a string format
        * instruments: list of instruments, each defined in a string
    Outputs: full orchestra in a string
    """
    output = settings + '\n'
    for instr in instruments:
        output += instr + '\n'
    if (reverb):
        output += REVERB_INST
    return output

def create_score(score_functions, score, duration=60, reverb=REVERB):
    """Inputs: 
        * core_functions: csound functions for any instruments in a string
        * score: a csound score in a string, of form "i1 0 5"
        * duration: for the reverb instrument, should be 
            duration of the entire composition in seconds
        * reverb: boolean used if reverb is wanted in the composition
    Returns the final score in a string"""
    reverb_score = ""
    if (reverb):
        reverb_score = "i99 0 " + str(duration) + '\n'
    return score_functions+reverb_score+score

def perform(orc, score, create_wav=False, wav_file='output.wav'):
    """
    Inputs: 
        * orc: csound orchestra in a string
        * score: csound score in a string
        * create_wav: boolean setting for if running this 
            function will create an output wav file. 
            Default False.
        * wav_file: file name for output wav file. 
            Default 'output.wav'.

    Function reads input orc and score and plays
        the corresponding csound composition. It generates
        the corresponding wav file if create_wav is True.
    """
    c = ctcsound.Csound()
    c.setOption("-odac")

    if (create_wav):
        output_file_flag = '-o ' + wav_file
        c.setOption(output_file_flag)

    # prepare the inputs
    c.compileOrc(orc)
    c.readScore(score)

    # performance
    c.start()
    c.perform()
    c.reset()

import random
import ctcsound
import numpy as np
import pandas as pd

# ------------ HOW TO USE THIS FILE ------------------------
# Use the function pop() to generate a wav file, change
# the duration value to change the duration of the 
# produced sound

REVERB = True

DURATION_MATRIX_1 = {
    0.125 : [0.35, 0.25, 0.05, 0.15, 0.05, 0.05, 0.1],
    0.25 : [0.1, 0.25, 0.1, 0.2, 0.05, 0.1, 0.2],
    0.333 : [0.05, 0.05, 0.3, 0.1, 0.2, 0.1, 0.2],
    0.5: [0.125, 0.125, 0.05, 0.35, 0.05, 0.1, 0.2],
    0.666: [0.05, 0.05, 0.3, 0.1, 0.2, 0.1, 0.2],
    0.75: [0.1, 0.25, 0.1, 0.2, 0.05, 0.1, 0.2],
    1: [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.25]
}

# favor shorter notes
DURATION_MATRIX_2 = {
    0.125 : [0.35, 0.25, 0.05, 0.15, 0.05, 0.05, 0.1],
    0.25 : [0.15, 0.25, 0.1, 0.2, 0.05, 0.1, 0.15],
    0.333 : [0.05, 0.05, 0.3, 0.1, 0.2, 0.1, 0.2],
    0.5: [0.2, 0.2, 0.05, 0.35, 0.05, 0.05, 0.1],
    0.666: [0.05, 0.05, 0.3, 0.1, 0.2, 0.1, 0.2],
    0.75: [0.1, 0.25, 0.1, 0.2, 0.05, 0.1, 0.2],
    1: [0.25, 0.25, 0.05, 0.125, 0.125, 0.1, 0.1]
}

# favor longer notes
DURATION_MATRIX_3 = {
    0.125 : [0.25, 0.25, 0.05, 0.15, 0.05, 0.05, 0.2],
    0.25 : [0.15, 0.25, 0.1, 0.2, 0.05, 0.1, 0.15],
    0.333 : [0.05, 0.05, 0.3, 0.1, 0.2, 0.1, 0.2],
    0.5: [0.125, 0.125, 0.05, 0.35, 0.05, 0.1, 0.2],
    0.666: [0.05, 0.05, 0.3, 0.1, 0.2, 0.1, 0.2],
    0.75: [0.1, 0.25, 0.1, 0.2, 0.05, 0.1, 0.2],
    1: [0.1, 0.125, 0.05, 0.25, 0.125, 0.1, 0.25]
}

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

# piano
INSTR3 = """
instr 3
; prepiano opcode: http://www.csounds.com/manualOLPC/prepiano.html
; p4 is frequency
; p5 is amplitude
; al,ar prepiano ifreq, iNS, iD, iK, iT30, iB,    kbcl, kbcr, imass, ifreq, iinit, ipos, ivel, isfreq, isspread
al,ar prepiano   p4,    2,   10, 1,  3,    0.001, 2,    2,    0.5,   3000,  0,     0.09, 45,   0,      0.1
alout = al * p5
arout = ar * p5
gaverb	 =	gaverb+alout*0.1
    outs alout, arout
endin
"""

# thunder
INSTR4 = """
instr 4
asig diskin "thunder16.wav", 1, 0
gaverb	 =	gaverb+asig*0.1
outs asig, asig
endin
"""

REVERB_INST = """
instr	99			
averb	reverb	gaverb,2
outs	averb, averb
gaverb	=  0		; reinitialize global reverb variable
endin
"""

INSTRUMENTS = [INSTR1, INSTR2, INSTR3, INSTR4]
SCORE_FUNCTIONS = "" # used for functions called in instruments

def create_orchestra(settings, instruments, reverb=REVERB):
    """
    Inputs:
        settings: Csound settings, including sr, kr, nchnls, 
            and 0dbfs in a string format
        instruments: list of instruments, each defined in a string
    Outputs: full orchestra in a string
    """
    output = settings + '\n'
    for instr in instruments:
        output += instr + '\n'
    if (reverb):
        output += REVERB_INST
    return output

def generate_score(instrument, duration, start_note = None, random=False):
    """"
    Generate score of length duration in seconds, in a string
    """
    if instrument == INSTR1:
        return instr1_score(start_note, duration)
    elif instrument == INSTR2:
        return instr2_score(duration)
    elif instrument == INSTR3:
        return instr3_score(start_note, duration)
    elif instrument == INSTR4:
        return instr4_score(duration)

def generate_durations(total_duration, duration_matrix=DURATION_MATRIX_1, start_duration = 0.5):
    """Returns sequence of values that sum to ~total_duration"""
    durationDF = pd.DataFrame.from_dict(duration_matrix, orient='index', 
                    columns=[0.125, 0.25, 0.333, 0.5, 0.666, 0.75, 1])
    sequence = [start_duration]
    current = start_duration
    count = start_duration
    while (count < total_duration):
        nextVal = np.random.choice(durationDF.columns.to_list(), replace=True, p=durationDF.loc[current].values)
        sequence.append(nextVal)
        current = nextVal
        count += nextVal
    return sequence

def instr3_score(start_note, duration):
    """Create score for instr3, the piano"""
    if start_note == None:
        start_note = 'C3'

    durations = generate_durations(duration, duration_matrix=DURATION_MATRIX_3)

    # generate sequence of notes based on pop music
    # generate notes for each duration in durations
    sequence = getNotes(start_note, len(durations))

    # Get the frequencies for each second
    frequencies = getFrequencies(sequence)

    second = 0
    score = ""
    index = 0
    for freqList in frequencies:
        note_duration = durations[index]
        for note in freqList:
            line = f"i3 {second} {note_duration} {note} 1\n"
            score += line
        second += note_duration
        index += 1
    return score

def instr2_score(duration):
    """Create score for instr2, the drum"""
    durations = generate_durations(duration, duration_matrix=DURATION_MATRIX_2)
    index = 0
    second = 0
    score = ""
    while (index < len(durations)):
        note_duration = durations[index]
        line = f"i2 {second} {note_duration} 0.05\n"
        score += line
        second += note_duration
        index += 1
    return score

def instr1_score(start_note, duration):
    """Create score for instr1, the simple tone"""
    if start_note == None:
        start_note = 'C3'

    durations = generate_durations(duration)

    # generate notes for each duration in durations
    #   sequence of notes based on pop music
    sequence = getNotes(start_note, len(durations))

    # Get the frequencies for each second
    frequencies = getFrequencies(sequence)

    second = 0
    index = 0
    score = ""
    for freqList in frequencies:
        note_duration = durations[index]
        for note in freqList:
            line = f"i1 {second} {note_duration} {note} 1\n"
            score += line
        second += note_duration
        index += 1
    return score

def instr4_score(duration):
    """Create score for instr4, thunder
        Adds thunder 4 times randomly in the score.
    """
    score = ""
    for _ in range(4):
        second = random.randint(0, duration - 4)
        line = f"i4 {second} 4\n"
        score += line
    return score

def remove_non_music_characters(string):
    """Used to normalize the datasets together"""
    musical_characters = ['A', 'B', 'C', 'D', 'E', 
                            'F', 'G', '1', '2', '3', 
                            '4', '5', '6', '7', '8', 
                            '9', '0', '|']
    output = ''
    for c in string:
        if c in musical_characters:
            output += c
    return output

def getNotesDF():    
    """Create a DataFrame of note probabilities based on input pop data"""
    # get matrix of note probabilities
    # Source: https://github.com/haebichan/PopMusicMaker/tree/master/probability%20matrices
    raw_notes = pd.read_csv('./probability_matrices/hori_dep_matrix.csv')
    raw_notes = raw_notes.rename(columns={ 'Unnamed: 0' : 'start_note'})
    raw_notes['start_note'] = raw_notes['start_note']
    notes = raw_notes.set_index('start_note')
    return notes

def getNotes(start_note, number_of_notes):
    """Input a start_note like 'C3' and return sequence of
    notes in a list, based on model
    """
    # get notes data
    notes = getNotesDF()

    # choose notes
    seq = [start_note]
    current = start_note
    count = 1
    while (count < number_of_notes):
        nextVal = np.random.choice(notes.columns.to_list(), replace=True, p=notes.loc[current].values)
        seq.append(nextVal)
        current = nextVal
        count += 1
    
    return seq

def getFrequencies(seq):
    """Take in a list of note names and convert them to frequencies in Hz"""
    # Create map of note name to frequency in Hz
    # Source: https://pages.mtu.edu/~suits/NoteFreqCalcs.html
    raw_freqs = pd.read_csv('./notes_freqs.csv')
    raw_freqs['name'] = raw_freqs['name']
    freqs = raw_freqs.set_index('name')

    frequencies = []
    for noteString in seq:
        noteString = remove_non_music_characters(noteString)
        noteList = getNoteList(noteString)
        freqList = []
        for note in noteList:
            freq = freqs.loc[note]['freq']
            freqList.append(freq)
        frequencies.append(freqList)
    return frequencies

def getNoteList(noteString):
    """Takes input string of style 'C3|A4' and returns corresponding list of notes"""
    if noteString == "":
        return []
    elif not '|' in noteString:
        return [noteString]
    else:
        c = 0
        note = ''
        while noteString[c] != '|':
            c += 1
        note = noteString[:c]
        return [note] + getNoteList(noteString[c+1:])

def create_score(score_functions, score, reverb=REVERB, duration = 10):
    """Returns the final score in a string"""
    reverb_score = ""
    if (reverb):
        reverb_score = "i99 0 " + str(duration) + '\n'
    return score_functions+reverb_score+score

def perform(orc, score, create_wav=False):
    """
    Inputs: 
        orc - csound orchestra in a string
        sco - csound score in a string

    Function reads input orc and score and plays
        the corresponding csound composition.
    """
    c = ctcsound.Csound()
    c.setOption("-odac")
    if (create_wav):
        c.setOption("-o output.wav")

    # prepare the inputs
    c.compileOrc(orc)
    c.readScore(score)

    # performance
    c.start()
    c.perform()
    c.reset()

def pop(create_wav=False):
    """Create basic composition based on pop song """
    orc = create_orchestra(ORC_SETTINGS, INSTRUMENTS)
    instr4_notes = generate_score(INSTR4, 60)
    instr3_notes = generate_score(INSTR3, 60, 'C3')
    instr2_notes = generate_score(INSTR2, 60)
    instr1_notes = generate_score(INSTR1, 60, 'A3')
    notes = instr1_notes + instr2_notes + instr3_notes + instr4_notes
    score = create_score(SCORE_FUNCTIONS, notes, duration=60)
    perform(orc, score, create_wav=create_wav)

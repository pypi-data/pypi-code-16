import time
import random
import os
from keyInfo import keyInfos

"""Variable declaration"""
bpm = 120
numberOfInstruments = 1
currentBarLength = 0

notes = {
    "1e": 32, "1f": 33, "1f#": 34, "1g": 35,
    "1g#": 36, "1a": 37, '1a#': 38, '1b': 39,
    '1c': 40, '1c#': 41, '1d': 42, '1d#': 43,
    '2e': 44, '2f': 45, '2f#': 46, '2g': 47,
    '2g#': 48, '2a': 49, 'a#': 50, '2b': 51,
    '2c': 52, '2c#': 53, '2d': 54, '2d#': 55,
    '3e': 56
}

keysSharps = {
    "a": ("f", "c", "g"),
    "b": ("f", "c", "g", "d", "a"),
    "c": (),
    "d": ("f", "c"),
    "e": ("f", "c", "g", "d"),
    "g": ("f"),
    "am": (),
    "em": ("f"),
    "bm": ("f", "c"),
    "f#m": ("f", "c", "g"),
    "c#m": ("f", "c", "g", "d"),
    "g#m": ("f", "c", "g", "d", "a")
}

keysFlats = {
    "f": ("b"),
    "a#": ("b", "e"),
    "d#": ("b", "e", "a"),
    "g#": ("b", "e", "a", "d"),
    "c#": ("b", "e", "a", "d", "g"),
    "f#": ("b", "e", "a", "d", "g", "c"),
    "dm": ("b"),
    "gm": ("b", "e"),
    "cm": ("b", "e", "a"),
    "fm": ("b", "e", "a", "d"),
    "a#m": ("b", "e", "a", "d", "g"),
    "d#m": ("b", "e", "a", "d", "g", "c")
}


def getNote(key):
    """Generate a new song because the createSong button was pressed"""

    def getFrequencyofNote(note):
        """Getting the frequency of each of the notes"""
        frequency = note - 49
        frequency = frequency / 12
        frequency = (2 ** frequency) * 440
        return frequency


    def checkNote(n, key, notes):
        """Checking to see if the note is in the right key"""
        chars = "123#"
        b = n
        for c in chars:
            b = b.replace(c, "")
        if key in keysSharps:
            b = (str(b in str(keysSharps[key])))
            if b == "True":
                finalNote = notes[n] + 1
                return finalNote
            return notes[n]
        elif key in keysFlats:
            b = (str(b in str(keysFlats[key])))
            if b == "True":
                finalNote = notes[n] - 1
                return finalNote
            return notes[n]


    def getAmplitude():
        """Get amplitude of note"""
        normal = 0.5
        ranDecide = random.randint(0, 10)
        if ranDecide > 8:
            amplitude = random.uniform(0, 1)
        else:
            amplitude = normal
        return amplitude


    def noteLength():
        """Generate the length of the note"""
        chooseLength = random.randint(1, 10)
        if chooseLength == 1:
            lengthOfNote = bpm/bpm
            return lengthOfNote
        elif chooseLength == 2 or chooseLength == 3:
            lengthOfNote = 1/2
            return lengthOfNote
        elif chooseLength > 3 and chooseLength < 7:
            lengthOfNote = 1/4
            return lengthOfNote
        elif chooseLength == 7 or chooseLength == 8:
            lengthOfNote = 1/8
            return lengthOfNote
        elif chooseLength == 9:
            lengthOfNote = 1/16
            return lengthOfNote
        elif chooseLength == 10:
            lengthOfNote = 1/32
            return lengthOfNote


    def checkBarLength(lengthOfNote, currentBarLength):
        if currentBarLength == 1:
            currentBarLength = 0
        else:
            if currentBarLength > 1:
                lengthOfNote = noteLength()
                checkBarLength(lengthOfNote, currentBarLength)
            elif currentBarLength < 1:
                currentBarLength = currentBarLength + lengthOfNote


    """Generating the notes and their attributes"""
    totalLength = 0.0
    n = random.choice(list(notes.keys()))
    note = checkNote(n, key, notes)
    frequency = getFrequencyofNote(note)
    lengthOfNote = noteLength()
    checkBarLength(lengthOfNote, currentBarLength)
    amplitudeOfNote = getAmplitude()
    return lengthOfNote, frequency, amplitudeOfNote

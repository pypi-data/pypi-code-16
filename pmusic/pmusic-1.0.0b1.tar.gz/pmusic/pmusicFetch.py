import random

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


def getNoteNumber(note):
    return notes[note]

def getKeySignature(key):
    try:
        attributes = list(keysSharps[key])
        return attributes
    except:
        try:
            attributes = list(keysFlats[key])
            return attributes
        except:
            return None
        

def getKey():
    """Getting the key of the song"""
    majorOrMinor = random.randint(0, 1)
    if majorOrMinor == 0:
        key = random.choice(list(keysSharps.keys()))
        type = False
    elif majorOrMinor == 1:
        key = random.choice(list(keysFlats.keys()))
        type = True
    return key

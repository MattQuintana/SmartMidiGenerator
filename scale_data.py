__author__ = 'Matthew Quintana'

### Keys
#   Structured so that key is represented by the step difference between notes
#   Major Key = First note, whole step (two tones) to next note, whole step, half step (1 tone), whole, ...
all_notes = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
major_key = [0, 2, 2, 1, 2, 2, 2, 1]
minor_key = [0, 2, 1, 2, 2, 2, 1, 2]
mixolydian = [0, 2, 2, 1, 2, 2, 1, 2]
minor_pentatonic = [0, 2, 1, 2, 1, 2, 1, 2]
ahava_raba = [0, 1, 3, 1, 2, 1, 2, 2]
natural_minor = [0, 2, 1, 2, 2, 1, 2, 2]
super_locrian = [0, 1, 2, 1, 2, 2, 2, 2]
blues = [0, 3, 2, 1, 1, 3, 2, 3]
diminished = [0, 2, 1, 2, 1, 2, 1, 2]
dominant_diminished = [0, 1, 2, 1, 2, 1, 2, 1]
test = [0, 1, 2, 2, 1, 2, 2, 1]
raised_fifth = [0, 2, 2, 2, 1, 2, 2, 1]
augmented_sixth = [0, 2, 2, 1, 2, 3, 1, 1]

# From A3 to F5
# 57 - 77
MAX_MIDI_VALUE = 77
MIN_MIDI_VALUE = 57

### Structured so that in order to define a chord change all you have to do is specify the key name
### and the chord number. So a Major 5th chord would be represented as ("major", 5)
### The entire chord will be constructed rather than by triads.
common_chord_change = [("major", 1), ("major", 5), ("minor", 6), ("major", 4)]
church_chords = [("major", 4), ("major", 5), ("augmented sixth", 5), ("minor", 6)]
timeless_change = [("major", 1), ("major", 5), ("major", 4), ("major", 5)]
fifties_changes = [("major", 1), ("minor", 6), ("major", 4), ("major", 5)]
love_changes = [("major", 1), ("major", 4), ("major", 5), ("major", 4)]
mixolydian_changes = [("major", 1), ("mixolydian", 7), ("major", 4), ("major", 1)]
flamenco = [("minor", 6), ("major", 5), ("major", 4), ("major", 3)]

# Used to identify what MIDI values correspond to note names
full_notes = {
    "C":60,
    "C#":61,
    "C#/Db":61,
    "Db":61,
    "D":62,
    "D#":63,
    "D#/Eb":63,
    "Eb":63,
    "E": 64,
    "F":65,
    "F#":66,
    "F#/Gb":66,
    "Gb":66,
    "G":67,
    "G#":68,
    "G#/Ab":68,
    "Ab":68,
    "A":69,
    "A#":70,
    "A#/Bb":70,
    "Bb":70,
    "B":71
}

# Used to identify what note name a MIDI value corresponds to
rev_full_notes = {
    60: "C",
    61: "C#",
    62: "D",
    63: "Eb",
    64: "E",
    65: "F",
    66: "F#",
    67: "G",
    68: "G#",
    69: "A",
    70: "Bb",
    71: "B"
}

# Associating a key string with its numerical representation
chord_names = {
    "major" : major_key,
    "minor" : minor_key,
    "blues" : blues,
    "mixolydian": mixolydian,
    "ahava raba" : ahava_raba,
    "diminished" : diminished,
    "augmented sixth" : augmented_sixth,
    "all notes":all_notes
}

# Associating a sequence of chord changes to their name.
changes = {
    "common":common_chord_change,
    "timeless":timeless_change,
    "flamenco":flamenco,
    "church":church_chords,
    "fifties":fifties_changes,
    "love":love_changes
}

##################################################
### Generates a scale based on a string scale name
def generate_scale(scale_name, key):
    start_note = full_notes[scale_name]
    new_scale = []

    # Add the note values into the note array to be chosen from.
    for i in range(0,len(key)):
        new_scale.append((start_note + key[i]))
        start_note += key[i]

    outside_additions = []
    for tone in new_scale:
        if((tone - 12 >= MIN_MIDI_VALUE) and (tone - 12 not in new_scale)):
            outside_additions.append(tone-12)
        if((tone + 12 <= MAX_MIDI_VALUE) and (tone + 12 not in new_scale)):
            outside_additions.append(tone+12)

    for tone in outside_additions:
        new_scale.append(tone)
    return new_scale

###########################################################################
### Generate a scale based on a starting midi value and the key to generate
def generate_scale_w_start(tone_value, key):
    new_scale = []
    # Add the note values into the note array to be chosen from.
    for i in range(0,len(key)):
        new_scale.append((tone_value + key[i]))
        tone_value += key[i]

    outside_additions = []
    for tone in new_scale:
        if((tone - 12 > MIN_MIDI_VALUE) and (tone - 12 not in new_scale)):
            outside_additions.append(tone-12)
        if((tone + 12 < MAX_MIDI_VALUE) and (tone + 12 not in new_scale)):
            outside_additions.append(tone+12)

    for tone in outside_additions:
        new_scale.append(tone)
    return new_scale
__author__ = 'Matthew Quintana'

from midiutil.MidiFile import MIDIFile


################################################
### Write the song to a midi file
################################################
def write_song(song):

    MyMIDI = MIDIFile(1) # One track
    file = open("neural_notes_data.txt", "w+")
    degrees = [60, 62, 64, 65, 67, 69, 71, 72] # Midi note number
    track = 0
    channel = 0
    time = 0 # time in beats
    duration = 1 # duration in beats
    tempo = 140 # tempo of the song
    volume = 100 # volume of the note

    MyMIDI.addTempo(track, time, tempo)

    for phrase in song:
        for measure in phrase:
            for note in measure:
                # Add the new note into the MIDI object
                # Note tuple structure: (note_start_time, note_value, note_length)
                MyMIDI.addNote(track, channel, note[1], note[0], note[2], volume)
                file.write("%.2f %d %.2f \n" % (note[0], note[1], note[2]))

    with open("neural_song.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

    #os.system("start " + "neural_song.mid")

def write_named_song(song, name):

    MyMIDI = MIDIFile(1) # One track
    file = open("individual_song.txt", "w+")
    degrees = [60, 62, 64, 65, 67, 69, 71, 72] # Midi note number
    track = 0
    channel = 0
    time = 0 # time in beats
    duration = 1 # duration in beats
    tempo = 140 # tempo of the song
    volume = 100 # volume of the note

    MyMIDI.addTempo(track, time, tempo)

    for phrase in song:
        for measure in phrase:
            for note in measure:
                # Add the new note into the MIDI object
                # Note tuple structure: (note_start_time, note_value, note_length)
                MyMIDI.addNote(track, channel, note[1], note[0], note[2], volume)
                file.write("%.2f %d %.2f \n" % (note[0], note[1], note[2]))

    with open(name, "wb") as output_file:
        MyMIDI.writeFile(output_file)

##########################################
### Write the song generated from the GUI
##########################################
def write_gui_song(song, gui_tempo, name="gui_song.mid"):

    MyMIDI = MIDIFile(1) # One track
    file = open("gui_notes_data.txt", "w+")
    track = 0
    channel = 0
    time = 0 # time in beats
    tempo = gui_tempo # tempo of the song
    volume = 120 # volume of the note

    MyMIDI.addTempo(track, time, tempo)

    for phrase in song:
        for measure in phrase:
            for note in measure:
                # Add the new note into the MIDI object
                # Note tuple structure: (note_start_time, note_value, note_length)
                MyMIDI.addNote(track, channel, note[1], note[0], note[2], volume)
                file.write("%.2f %d %.2f \n" % (note[0], note[1], note[2]))

    with open(name, "wb") as output_file:
        MyMIDI.writeFile(output_file)


__author__ = 'Matthew Quintana'

try:
    import Tinter as tk
except:
    import tkinter as tk
    import tkinter.ttk as ttk

from midigenerator import outside_create

root = tk.Tk()

generating_string = tk.StringVar()
generating_string.set(" ")

def process_data():
    global time_sig_int
    global time_sig
    temp_timesig = tk.IntVar()
    timesig_string = time_sig.get()
    if (timesig_string == '4/4'):
        temp_timesig = 4
    elif (timesig_string == '3/4'):
        temp_timesig = 3
    elif (timesig_string == '2/4'):
        temp_timesig = 2
    time_sig_int.set(temp_timesig)

def generate():
    global generating_string
    generating_string.set("Generating...")
    root.update_idletasks()
    process_data()
    passing_data = {
        "scale_name":scale_name.get(),
        "key_name":key_name.get().lower(),
        "song_type":song_type_choice.get(),
        "chord_changes": chord_changes.get(),
        "tempo":tempo.get(),
        "time_sig": time_sig_int.get(),
        "num_changes_repeats": num_chord_changes_repeat.get(),
        "num_phrases": num_phrases.get(),
        "num_measures_per_phrase": num_measure_per_phrase.get(),
        "num_layered_ideas": num_ideas_in_layered_melody.get()
    }
    outside_create(passing_data)
    generating_string.set("Complete")

nb = ttk.Notebook(root)

nb.pack(fill='both', expand='yes')

basic_win = ttk.Frame(nb)
advanced_win = ttk.Frame(nb)


nb.add(basic_win, text='Basic')
nb.add(advanced_win, text='Advanced')

# use width x height + x_offset + y_offset (no spaces!)
root.geometry("%dx%d+%d+%d" % (500, 450, 220, 150))
root.title("Midi Song Generator")

# Variables to use for passing to the method for generation
scale_name = tk.StringVar(root)
key_name = tk.StringVar(root)
chord_changes = tk.StringVar(root)
tempo = tk.IntVar()
time_sig = tk.StringVar()
time_sig_int = tk.IntVar()
num_chord_changes_repeat = tk.IntVar()
num_phrases = tk.IntVar()
num_measure_per_phrase = tk.IntVar()
num_ideas_in_layered_melody = tk.IntVar()

### Create a label for the scale option
scale_label = tk.Label(basic_win, text="Root Note: ").grid(row=0, column=0)
#scale_label.pack(side = "left", anchor="nw")
#scale_options.pack(padx=10, pady=10, anchor="nw", side="left")

### Scale Choosing
# initial value
scale_name.set('C')
scale_choices = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
scale_options = tk.OptionMenu(basic_win, scale_name, *scale_choices).grid(row=0, column=1)

### Create a label for the key option
key_label = tk.Label(basic_win, text="Key: ").grid(row=0, column = 2)
#key_label.pack(side = "left", anchor="nw")
### Key Choosing
key_name.set('Major')
key_choices = ['Major', 'Minor', 'Mixolydian', 'Ahava Rab', 'Blues', 'All Notes']
key_options = tk.OptionMenu(basic_win, key_name, *key_choices).grid(row=0, column = 3)

#key_options.pack(padx = 10, pady = 10, anchor="nw", side = "left")

### Time signature
timesig_label = tk.Label(basic_win, text="Time Signature: ").grid(row = 0, column = 4)
time_sig.set('4/4')
time_sig_choices = ['4/4', '3/4', '2/4']
time_sig_options = tk.OptionMenu(basic_win, time_sig, *time_sig_choices).grid(row = 0, column = 5)

### Tempo
tempo_label = tk.Label(basic_win, text="Tempo: ").grid(row = 1, column = 0)
tempo.set(120)
tempo_entry = tk.Entry(basic_win, textvariable = tempo).grid(row = 1, column = 1)

Melodies = [
    ("Chained Melody", "chained"),
    ("Layered Melody", "chained-combined"),
    ("Chord Changed", "chord-changes")
]

song_type_choice = tk.StringVar()
song_type_choice.set("chained")

i = 4
for type, value in Melodies:
    b = tk.Radiobutton(basic_win, text=type,variable=song_type_choice,value=value,
                       indicatoron=0, width = 25).grid(row=i, column=0, columnspan=2, sticky = "n,e,s,w", padx=5)
    i += 1
    #b.pack(fill="x")

### Generate Button
button = tk.Button(basic_win, text="Generate", command=generate).grid(row=10,column=0)

generating_noti = tk.Label(basic_win, textvariable = generating_string).grid(row=11, column = 0)

#### ADVANCED SECTION ####
### Chord changes options
chord_changes_label = tk.Label(advanced_win, text = "Chord Changes Style: ").grid(row=0, column = 0)
chord_changes.set("None")
changes_choices = ["None", "common", "church", "timeless", "flamenco","fifties","love"]
changes_options = tk.OptionMenu(advanced_win, chord_changes, *changes_choices).grid(row=0, column=1)

### Times to repeat chord changes
chord_repeats_label = tk.Label(advanced_win, text = "Times to repeat changes: ").grid(row=0, column=2)
num_chord_changes_repeat.set(1)
num_changes_rep_entry = tk.Spinbox(advanced_win, textvariable = num_chord_changes_repeat, width = 3, from_=1, to_=5).grid(row = 0, column = 3)

### Number of phrases
num_phrases_label = tk.Label(advanced_win, text = "Number of Phrases: ").grid(row = 1, column = 0)
num_phrases.set(1)
num_phrases_entry = tk.Spinbox(advanced_win, width = 3, textvariable = num_phrases, from_=1, to_=32).grid(row = 1, column = 1)

### Measure per phrase
num_measure_lable = tk.Label(advanced_win, text = "Number of measure per phrase: ").grid(row = 2, column = 0)
num_measure_per_phrase.set(4)
num_measures_entry = tk.Spinbox(advanced_win, width = 3, textvariable = num_measure_per_phrase, from_=1, to_=12).grid(row=2, column = 1)

### Number of ideas in a layered melody
num_ideas_label = tk.Label(advanced_win, text = "Number of layered ideas in a melody: ").grid(row = 3, column = 0)
num_ideas_in_layered_melody.set(3)
num_ideas_entry = tk.Spinbox(advanced_win, width = 3, textvariable = num_ideas_in_layered_melody, from_=1, to_ = 5).grid(row = 3, column = 1)

root.mainloop()


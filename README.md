# Smart MIDI Generator
Using a neural network, this program will generate a MIDI song based on a given scale and time signature.

## Requires:
numpy
midiutil

## How it works
Given a pre-generated scale, the program chooses a random note and a random length for it. Afterwards, it makes a choice
to either repeat/exploit or change/explore that note and rhythm. Once enough notes are generated to fill
a measure, it makes a choice to repeat that measure entirely, changes tones but maintain rhythms, or generate a completely new
measure. Once enough measures are created to fill a phrase, the next phrase begins its generation until all the
phrases in a song are generated.

After generating several potential songs, the program evaluates each of them and assigns them a score, using it and all the 
decisions made in the song creation to update the exploit/explore neural network, so that songs in the next generation 
theoretically score better. 

With several different groups of generations created, the program compares the best ones from each group, and takes the overall 
best one as the final, completed song idea.
__author__ = 'Matthew Quintana'

import random
import numpy
import os
from scale_data import *
from write_song_file import *
from collections import Counter

# Sigmoid function
def nonlin(x, deriv = False):
    if (deriv == True):
        return x*(1-x)
    return 1/(1+numpy.exp(-x))

def normalize_2Darray(array):
    rows = len(array)
    cols = len(array[0])

    for row in range(0, rows):
        sum = 0
        for col in range(0, cols):
            sum += abs(array[row][col])

        for col in range(0, cols):
            array[row][col] = abs(array[row][col])
            array[row][col] /= sum

### Number of beats per measure, in this case,
#   the typical four beats per measure where a quarter note represents one beat
time_sig = 4

### Number of measures per phrase
measures_per_phrase = 4

### How many phrases we are going to use in the generation
number_phrases = 1

### How many different musical "threads" should be in a phrase
number_layered_ideas = 3

### How many separate phrases to chain together
number_phrases_chained = 4

### Number of full combined phrases to chain together
number_combo_chains = 4

### Number of times we are going to repeat the chord change sequence
number_changes_repeats = 2

generations = 10
individuals = 10

### Boosting/dropping values of note length
length_boost_weights = [1.2, 1.3, .8]
#length_boost_weights = [1/3, 1/3, 1/3]
##      Structure [to multiply against notes of same length,
#                  to multiply against notes of close length,
#                  to multiply against notes of different length]

### Boosting/dropping values of note value
value_boost_weights = [.9, 1.2, .8]
##      Structure [to multiply against notes of same value,
#                  to multiply against notes of close value, - specifically the previous and next note in the scale
#                  to multiply against notes of different value]

#numpy.random.seed(1)

# Randomize the initial weights of the phrase neural network
#   This neural network will be used to decide whether a phrase
#   should repeat an idea, as in a previous measure.
phrase_syn = numpy.random.random((2,2))
# Normalize the weights so that they can work as probabilities
normalize_2Darray(phrase_syn)
weights_syn = 0

# Randomize the initial weights of the notes neural network
#   This neural network will be used to determine whether
#   a note should be repeated or if it should change in rhythm and/or tone.
note_syn = numpy.random.random((2,2))
# Normalize the weights so that they can work as probabilities
normalize_2Darray(note_syn)
note_wsyn = 0

### Exploit and explore weights
#   0 for exploit/repeat; 1 for explore
#   Exploit: repeat a previous idea
#   Explore: try a new idea
exploit_vs_explore = [0, 1]

# Set the probabilities of a decision being made to exploit or explore
# a note or a phrase idea.
# Probability       [Exploit,       Explore]
note_rhythm_exp =   [note_syn[0][0], note_syn[0][1]]
note_tone_exp   =   [note_syn[1][0], note_syn[1][1]]
phrase_note_exp =   [phrase_syn[0][0], phrase_syn[0][1]]
phrase_tone_exp =   [phrase_syn[1][0], phrase_syn[1][1]]

###############################################################
### Generate a certain amount of songs and return the best one
###############################################################
def create_songs(number_to_generate, scale_string, key):
    potential_songs = []
    all_phrase_decisions = []
    complete_measure_decisions = []
    best_eval = 0

    # Create the scale that the song generation will use based on it's name and the key it will be in
    # Ex: Generate the C scale in the minor key - generate_scale("C", minor_key)
    new_scale = generate_scale(scale_string, key)

    ### Generate all of the songs
    for i in range(number_to_generate):
        new_song, phrase_decisions, all_measure_decisions = neural_generate_midi_song(new_scale)
        # Return the song as well as the list of all decisions it made in relation to
        #   whether it changed notes in the measure and if it reused ideas from the previous measure.
        potential_songs.append(new_song)
        all_phrase_decisions.append(phrase_decisions)
        complete_measure_decisions.append(all_measure_decisions)
        # Add the newly created song to the larger set

    # Get the first song so that we have something to compare others to
    best_song = potential_songs[0]

    # For every song in our list
    for song, song_decisions, song_measure_decisions in zip(potential_songs, all_phrase_decisions, complete_measure_decisions):
        # Evaluate it and return its score
        evaluation = eval_function(song, new_scale)
        # Update the weights of the phrase neural network based on the song's score
        #   This will change the weights on if a future song will be more or less likely
        #   to repeat an idea from a previous measure.
        update_phrase_synapses(evaluation, song_decisions)
        # For every phrase in a song and the decisions made by it
        for phrase, phrase_measure_decisions in zip(song, song_measure_decisions):
            # And for every measure in each phrase as well as the inner decisions made
            for measure, single_measure_decisions in zip(phrase, phrase_measure_decisions):
                # Evaluate how well the measure did
                measure_eval = evaluate_measure(measure)
                # Based on the score, update the neural network in charge of individual note decisions
                update_note_synapses(measure_eval, single_measure_decisions)


        if (evaluation > best_eval):
            # If a song has scored better than the previous best
            best_song = song
            # Set it and update the top score
            best_eval = evaluation

    return best_song

#################################################
### Evaluate a single measure and give it a score
#################################################
def evaluate_measure(measure):
    measure_value = 0
    m_note_sum = 0
    rhythm_list = [note[2] for note in measure]
    value_list = [note[1] for note in measure]

    # See how many different note tones are used in the measure
    value_analysis = list(Counter(value_list).items())
    for note in value_analysis:
        if note[1] >= 4:
            # If a note is repeated more than four times in a measure, discourage it
            measure_value -= 10

    if 2 < len(value_analysis) < 5:
        # Encourage the use of different notes
        measure_value += 1
    else:
        # However not too many or too few in the same measure
        measure_value -= 1

    # See how many different note lengths are in the measure
    rhythm_analysis = list(Counter(rhythm_list).items())
    if len(rhythm_analysis) == 1:
        # Encourage the use of the same note length in the measure
        measure_value += 2
    elif len(rhythm_analysis) == 2:
        # But put a higher priority on one simple variation
        measure_value += 10
    else:
        measure_value -= 5

    # If a measure has a whole note and another note inside of it, then discourage
    if (len(rhythm_analysis) > 1) and len([note for note in rhythm_analysis if note[0] == 4.0]) > 0:
        measure_value -= 10

    # Determine which tone is the highest and lowest in the measure
    highest_tone = 0
    lowest_tone = 100
    for note in measure:
        m_note_sum += note[2]
        if (note[1] > highest_tone):
            highest_tone = note[1]
        if (note[1] < lowest_tone):
            lowest_tone = note[1]

    # Checking the distance between the lowest note and the highest note in the measure
    if (highest_tone - lowest_tone > 10):
        # Penalize any measures with a large distance between the lowest and highest note
        measure_value -= 10
    else:
        measure_value += 10

    # Reward for beginning measure notes that start exactly on the first beat
    if (measure[0][0]+1)%4 == 1:
        measure_value += 10
    else:
        measure_value -= 5

    # Reward measures that have a note sum that fits within the time signature
    # For example if the song is in 4/4 time, the length of notes in the measure should sum to 4 beats
    global time_sig
    if m_note_sum == time_sig:
        measure_value += 10
    else:
        # Penalize any measure that contains overflowing notes
        measure_value = -10
    return measure_value

#################################################
### Evaluate the entire song and give it a score
#################################################
def eval_function(song, scale):
    song_score = 0
    ### Check if the song begins and ends with tonic notes
    first_note = song[0][0][0]
    last_note = song[-1][-1][-1]
    if (first_note[1] == scale[0]) or (first_note[1] == scale[2]) or (first_note[1] == scale[4]) or \
            (first_note[1] == scale[7]):
        song_score += 5
    else:
        song_score -= 5

    if (last_note[1] == scale[0]) or (last_note[1] == scale[2]) or (last_note[1] == scale[4]) or (last_note[1] == scale[7]):
        song_score += 10
    else:
        song_score -= 10

    # If the last note in the song is at least two beats long
    if (last_note[2] >= 2):
        # Reward it
        song_score += 5
    else:
        # Otherwise penalize
        song_score -= 5
    ### Done checking start and end notes


    ### Evaluate each phrase in the song
    phrase_scores = []
    for phrase in song:
        phrase_score = 0
        # Measure evaluation
        measure_scores = []
        for measure in phrase:
            measure_value = evaluate_measure(measure)
            measure_scores.append(measure_value)
        ### END measure evaluation

        # Get the average score of the measures to set as the phrase score
        phrase_score = sum(measure_scores)/len(measure_scores)
        for score in measure_scores:
            if score < 0:
                # Put a major penalty on any negative scores
                phrase_score -= 100

        # Save the score to be used later
        phrase_scores.append(phrase_score)
    ## End evaluating all phrases

    ### Get sums/average of all four measure phrases to be returned
    song_score += sum(phrase_scores)/len(phrase_scores)
    return song_score

#################################################
### Update the weights in the note neural network
#################################################
def update_note_synapses(evaluation, decisions):
    global note_syn
    global note_wsyn
    highest_possible_score = 50  #31

    # Create a randomized weight array that determines the
    # influence of each decision on the final score.
    note_wsyn = numpy.random.random((len(decisions), 2))

    # Get the dot product of the decisions list and the
    # note synapse weights.
    L1 = nonlin(numpy.dot(decisions, note_syn))

    # Use it to multiply against the randomized weights
    L2 = nonlin(numpy.dot(L1.T, note_wsyn))

    # Get the amount of error made by the song score
    L2_error = highest_possible_score - abs(evaluation)

    # Get the error factor by multiplying the error by the
    # output of the matrix put through the sigmoid function.
    L2_delta = L2_error * nonlin(L2, True)

    # Find the error committed by the first layer of the network
    L1_error = L2_delta.dot(note_wsyn.T)

    # Backpropogate the error so that we find out how much each decision
    # affected the final outcome.
    L1_delta = L1_error.T * nonlin(L1, True)
    note_wsyn += L1.dot(L2_delta)

    # Update the note synapse weights to influence the next song made
    note_syn += numpy.asarray(decisions).T.dot(L1_delta)

    # Normalize the array so that it can be used for probabilities
    normalize_2Darray(note_syn)

###################################################
### Update the weights in the phrase neural network
###################################################
def update_phrase_synapses(evaluation, decisions):
    global weights_syn
    global phrase_syn
    highest_possible_score = 50 #51

    # Create a randomized weight array that determines the
    # influence of each decision on the final score.
    weights_syn = 2*numpy.random.random((len(decisions),2))-1
    normalize_2Darray(weights_syn)

    #print("Phrase synapse: \n", phrase_syn)
    #print("Weights sign: \n", weights_syn)

    #print("Decisions: \n ", decisions)
    # Get the dot product of the decisions list and the
    # phrase synapse weights.
    #print(numpy.dot(decisions, phrase_syn))
    L1 = nonlin(numpy.dot(decisions, phrase_syn))
    #print("L1: \n ", L1)

    # Use it to multiply against the randomized weights
    L2 = nonlin(numpy.dot(L1.T, weights_syn))
    #print("L2: \n", L2)

    # Get the amount of error made by the song score
    l2_error = highest_possible_score - abs(evaluation)
    #print("L2 Error: ", l2_error)

    # Get the error factor by multiplying the error by the
    # output of the matrix put through the sigmoid function.
    l2_delta_error = l2_error * nonlin(L2, True)
    #print("L2 Delta Error: \n", l2_delta_error)

    # Find the error committed by the first layer of the network
    l1_error = l2_delta_error.dot(weights_syn.T)
    #print("L1 Error: \n", l1_error)

    # Backpropogate the error so that we find out how much each decision
    # affected the final outcome.
    l1_delta_error = l1_error.T * nonlin(L1, True)
    #print("L1 Delta Error", l1_delta_error)

    weights_syn += L1.dot(l2_delta_error)
    #print("Weights Synapse: \n", weights_syn)
    normalize_2Darray(weights_syn)
    #print("    Normalized: \n", weights_syn)

    #print("Phrase Synapse Adjust: \n", numpy.asarray(decisions).T.dot(l1_delta_error))
    # Update the note synapse weights to influence the next song made
    phrase_syn += numpy.asarray(decisions).T.dot(l1_delta_error)
    #print("Phrase Synapse: \n", phrase_syn)

    # Normalize the array so that it can be used for probabilities
    normalize_2Darray(phrase_syn)
    #print("    Normalized: \n", phrase_syn)
    #print()

###################################################
### Generate a single song using the neural network
def neural_generate_midi_song(scale):
    time = 0
    w_scale = []
    for i in range(0, len(scale)):
        w_scale.append(1/len(scale))

    note_lengths = [.25, .5, 1, 2, 3, 4]
    w_note_lengths = [.05, .20, .25, .25, .20, .05]
    #w_note_lengths = [1/6, 1/6, 1/6,1/6,1/6,1/6]

    #w_note_lengths = []
    #for i in range(0, len(note_lengths)):
    #    w_note_lengths.append(1/len(note_lengths))
    weight_sum = 0


    for i in range(0, len(note_lengths)):
        w_note_lengths[i] /= sum(w_note_lengths)
        weight_sum = sum(w_note_lengths)

    song = []
    phrase_decisions = []
    all_measure_decisions = []
    ### Creating the song ##
    for i in range(0, number_phrases):
        phrase = []
        phrase_measure_decisions = []
        for j in range(0, measures_per_phrase):
            note_sum = 0
            one_measure = []
            single_measure_decision = []
            phrase_expl = numpy.random.choice(a = exploit_vs_explore, p=phrase_note_exp)

            # If we want to repeat the previous measure rhythm
            if phrase_expl == 0 and phrase:
                # If the phrase is not empty
                exploit_idea_index = random.randrange(0, len(phrase))
                repeated_idea_measure = phrase[exploit_idea_index]
                phrase_tone_expl = numpy.random.choice(a = exploit_vs_explore, p=phrase_note_exp)
                phrase_decisions.append([0, phrase_tone_expl])
                # In this case, the phrase is being repeated completely without different notes
                if phrase_tone_expl == 0:
                    for note in repeated_idea_measure:
                        one_measure.append((time, note[1], note[2]))
                        time += note[2]
                    # For every decision made in the last measure created
                    # Copy that same decisions in to the next measure being generated
                    for decision in phrase_measure_decisions[exploit_idea_index]:
                        single_measure_decision.append(decision)
                # The phrase in being repeated, but the notes can potentially change
                else:
                    for note in repeated_idea_measure:
                        note_tone = numpy.random.choice(a = scale, p=w_scale)
                        if (note_tone == note[1]):
                            single_measure_decision.append([0, 0])
                        else:
                            single_measure_decision.append([0, 1])
                        one_measure.append((time, note_tone, note[2]))
                        time += note[2]

            # If we want to create a new style of measure
            else:
                phrase_decisions.append([1,1])
                # Create a single measure in the phrase
                while note_sum < time_sig:
                    w_note_lengths = [.05, .20, .25, .25, .20, .05]

                    # Make the decision to either exploit or explore the rhythm of the next note
                    rhythm_expl = numpy.random.choice(a = exploit_vs_explore, p=note_rhythm_exp)
                    # Make the decisions to either exploit or explore the tone value of the next note
                    tone_expl = numpy.random.choice(a = exploit_vs_explore, p = note_tone_exp)
                    # Record the decision made
                    single_measure_decision.append([rhythm_expl, tone_expl])

                    # If we are exploiting/staying the same with the rhythm
                    if (rhythm_expl == 0):
                        # Check if the measure is empty or not
                        if one_measure:
                            # If the measure isn't empty, get the last note used and add a new one of it.
                            random_note_length = one_measure[-1][2]
                        else:
                            # Otherwise, if there's nothing to copy, just choose a random note length
                            random_note_length = numpy.random.choice(a=note_lengths, p=w_note_lengths)

                    # If the rhythm is going to change
                    else:
                        # Check if the measure actually has notes in it
                        if one_measure:
                            # If so, reduce the probability on the rhythm of the previous note chosen
                            #   and boost the probability of the other ones
                            for k in range(0, len(note_lengths)):
                                if (note_lengths[k] == one_measure[-1][2]):
                                    w_note_lengths[k] *= .1

                            # Get the new sum of weights for normalization
                            weight_sum = sum(w_note_lengths)

                            # Normalize the weights
                            for k in range(0, len(w_note_lengths)):
                                w_note_lengths[k] = (w_note_lengths[k]/weight_sum)
                            # Finally choose a note from the adjusted probabilities

                            # Choose a random note length based on the weights given
                            random_note_length = numpy.random.choice(a=note_lengths, p=w_note_lengths)
                        else:
                            # If the measure does not have any notes in it already, we can't do an exploitation
                            # So just do a random choice
                            random_note_length = numpy.random.choice(a=note_lengths, p=w_note_lengths)

                    # If we are exploiting or exploring with the note tone
                    if tone_expl == 0:
                        # 0 indicates that we are staying the same
                        if one_measure:
                            # If the measure is not empty
                            # Get the tone of the last value put in the measure
                            random_note_value = one_measure[-1][1]
                        else:
                            # If the measure IS empty, just choose a random note to begin
                            random_note_value = numpy.random.choice(a = scale, p=w_scale)
                    else:
                        # If an exploration is being made
                        # Check if the measure has notes in it
                        if one_measure:
                            # Find what note was used last in order to drop its probability
                            for k in range(0, len(scale)):
                                # If the notes match
                                if (scale[k] == one_measure[-1][2]):
                                    # Drop the probability of that note being used again
                                    w_scale[k] *= .1

                            # Normalize scale weights
                            scale_w_sum = sum(w_scale)
                            for k in range(0, len(w_scale)):
                                w_scale[k] = (w_scale[k]/scale_w_sum)

                            # Finally choose a note to be used
                            # Get a random note value from the scale based on weights

                            random_note_value = numpy.random.choice(a = scale, p=w_scale)
                        else:
                            # If the measure turns out to be emtpy
                            # Just choose a random note to begin with
                            random_note_value = numpy.random.choice(a = scale, p=w_scale)
                    # Add in the chosen note into the measure
                    one_measure.append((time, random_note_value, random_note_length))
                    # Adjust the time so that we don't overwrite notes
                    time += random_note_length
                    # Keep track of how filled up the measure is at this point
                    note_sum += random_note_length
                # End While loop
            # Add in the completed measure into the phrase
            phrase.append(one_measure)
            # Record the phrase decision made
            phrase_measure_decisions.append(single_measure_decision)
        # End create one phrase
        # Add in the newly created phrase into the song
        song.append(phrase)
        # Record the entire set of decisions made
        all_measure_decisions.append(phrase_measure_decisions)

        # Reset the note length weights to get a new style of phrase
        w_note_lengths = [.05, .25, .25, .25, .15, .05]

        # Reset the note value weights to get a new style of phrase
        w_scale = []
        for i in range(0, len(scale)):
            w_scale.append(1/len(scale))
    # End song creation
    return song, phrase_decisions, all_measure_decisions

######################################
### Run the program

########################################################################
### Generate several groups of songs and compare the best ones from each
########################################################################
def group_song_creation(num_groups, scale_name, key):
    best_songs = []
    new_scale = generate_scale(scale_name, key)
    best_val = 0
    for i in range(0, num_groups):
        best_group_song = create_songs(individuals, scale_name, key)
        best_songs.append(best_group_song)

    elite_song = best_songs[0]
    for song in best_songs:
        evaluation = eval_function(song, new_scale)
        if (evaluation > best_val):
            best_val = evaluation
            elite_song = song
    #print("Elite value:", best_val)
    return elite_song

##############################################################################
### Generate a single song by layering several different songs over each other
##############################################################################
def generate_combined_songs(scale_string, key):
    final_song = []
    for i in range(0, number_layered_ideas):
        new_song = group_song_creation(generations, scale_string, key)
        for phrase in new_song:
            final_song.append(phrase)
            # Append each phrase into the song list without adjusting for time
    # Return song list for writing later
    return final_song

#######################################################################################
### Generate a single song that has several different songs chained one after the other
#######################################################################################
def generate_chained_songs(scale_string, key):
    final_song = []
    time = 0

    # For every song that we have to chain together
    for i in range(0, number_phrases_chained):
        # Create a new song
        new_song = group_song_creation(generations, scale_string, key)
        for phrase in new_song:
            new_phrase = []
            for measure in phrase:
                new_measure = []
                for note in measure:
                    new_measure.append((time, note[1], note[2]))
                    # Adjust the time to keep incrementing
                    time += note[2]
                new_phrase.append(new_measure)
            # Append each phrase to the end of the song list
            final_song.append(new_phrase)
    # Return the song list for writing later.
    return final_song

##############################################################################
### Generate a song that has several layered songs chained one after the other
##############################################################################
def generate_chained_combined(scale_string, key):
    final_song = []
    time = 0
    offset = 0

    # For how many times that we have to chain layered melodies together
    for i in range(0, number_combo_chains):
        # Create a new song to be chained onto the end
        new_song = generate_combined_songs(scale_string, key)
        # Construct the song list to be used for writing later
        for phrase in new_song:
            new_phrase = []
            for measure in phrase:
                new_measure = []
                for note in measure:
                    new_measure.append((note[0]+offset, note[1], note[2]))
                new_phrase.append(new_measure)
            final_song.append(new_phrase)
        last_phrase_note = final_song[-1][-1][-1]
        # Set the offset to start the next chain at the end of the previous one.
        offset = last_phrase_note[0] + last_phrase_note[2]
    return final_song

###############################################
### Generate a song that includes chord changes
###############################################
def generate_chord_changed(scale_string, key, chord_changes):
    final_song = []
    time = 0
    offset = 0

    # Figure out the root note that we are starting from to base the chord changes
    base_scale = generate_scale(scale_string, key)

    # For every chord change that we are going to do
    for i in range(0, len(chord_changes)):
        # Based on the scale that is being used, find the root note of the next
        # chord to be used and its corresponding MIDI value
        tone_value = (base_scale[chord_changes[i][1] - 1] % 12) + 60
        # Truncate the tone to be within the scale if it goes over

        # Look up the corresponding name string of the MIDI value
        new_scale_string = rev_full_notes[tone_value]
        # Get the key type of the chord to be used in the generation
        new_key = chord_names[chord_changes[i][0]]
        # Generate the new "song" to be used as the chord changed section
        new_song = generate_combined_songs(new_scale_string, new_key)

        # Construct the song for writing later
        for phrase in new_song:
            new_phrase = []
            for measure in phrase:
                new_measure = []
                for note in measure:
                    new_measure.append((note[0]+offset, note[1], note[2]))
                new_phrase.append(new_measure)
            final_song.append(new_phrase)
        last_phrase_note = final_song[-1][-1][-1]
        # Use an offset so that we can chain the measures rather than layering them all together
        offset = last_phrase_note[0] + last_phrase_note[2]
    return final_song

##################################################################
### Generate a song with chord changes repeated several times over
##################################################################
def generate_chained_chord_changes(scale_string, key, chord_changes):
    # This method will generate a song that has a set of chord changes repeated
    # for as many times as instructed.

    final_song = []
    time = 0
    offset = 0

    # For every repetition of chord changes that we are going to do
    for i in range(0, number_changes_repeats):
        # Generate a song to be added in
        new_song = generate_chord_changed(scale_string, key, chord_changes)
        # Construct the new song list
        for phrase in new_song:
            new_phrase = []
            for measure in phrase:
                new_measure = []
                for note in measure:
                    new_measure.append((note[0]+offset, note[1], note[2]))
                new_phrase.append(new_measure)
            final_song.append(new_phrase)
        last_phrase_note = final_song[-1][-1][-1]
        # Set the offset so that the next song starts at the end of the last one
        offset = last_phrase_note[0] + last_phrase_note[2]
    return final_song

###################################################
### Create a song based on the input from the gui
###################################################
def outside_create(packed_data):

    numpy.random.seed()

    # Set the global time signature
    global time_sig
    time_sig = packed_data["time_sig"]

    global number_changes_repeats
    number_changes_repeats = packed_data["num_changes_repeats"]

    global number_phrases_chained
    number_phrases_chained = packed_data["num_phrases"]

    global number_combo_chains
    number_combo_chains = packed_data["num_phrases"]

    global measures_per_phrase
    measures_per_phrase = packed_data["num_measures_per_phrase"]

    global number_layered_ideas
    number_layered_ideas = packed_data["num_layered_ideas"]

    ## This part could be refactored immensely due to its use of globals.
    ## The best option might be to pass through the packed_data parameter
    ## through the other generation and evaluation functions.

    # Extract all of the data to be used
    type = packed_data["song_type"]
    key = chord_names[packed_data["key_name"]]
    scale_string = packed_data["scale_name"]
    chord_changes = packed_data["chord_changes"]
    tempo = packed_data["tempo"]

    # Check what type of song is going to be created
    if (type == "chained"):
        # Creating a sequence of notes an measures one after the other
        new_song = generate_chained_songs(scale_string, key)
    elif (type == "combined"):
        # Generating a layered sequence of notes for a single phrase
        new_song = generate_combined_songs(scale_string, key)
    elif (type == "chained-combined"):
        # Generating a layered sequence of notes for a certain number of phrases
        new_song = generate_chained_combined(scale_string, key)
    elif (type == "chord-changes"):
        # Generating a layered sequence of notes that adhere to a set of
        # chord changes.
        if (chord_changes != "None"):
            chord_changes = changes[chord_changes]
            new_song = generate_chained_chord_changes(scale_string, key, chord_changes)
        else:
            new_song = generate_chained_combined(scale_string, key)

    # Write the song to the file and open it.
    write_gui_song(new_song, tempo)
    os.system("start " + "gui_song.mid")
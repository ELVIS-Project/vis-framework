from vis.analyzers.indexers import noterest, interval, metre, offset, subsection
from vis.analyzers.experimenters import frequency, aggregator
from vis.models.indexed_piece import IndexedPiece
from vis.models.aggregated_pieces import AggregatedPieces
from pandas import pandas, DataFrame, Series
from difflib import SequenceMatcher
from collections import Counter
import numpy as np
import music21
import os

''' INFO/USEFULS

========== Terminology ==========
1.  Fingerprint
    1.1     Def: Two or four measures of monophonic material that identifies a strain of a piece
2.  Strain
    2.1     Def: A subsection of a piece - e.g. the A section, the B section etc
3.  Strong Beat
    3.1     Def: Offsets n*1.5 for all int n in 6/8 or 9/8 pieces, offsets n*1.0 for all int n in other pieces
    3.2     Notes on strong beats ('strong [beat] notes') are S1, S2... etc corresponding to offsets 0.0, 1.0, 2.0, ... or offsets 0.0, 1.5, 3.0, ... depending on above
    3.3     'Strong [beat] intervals' are Sx=>Sy, where Sx and Sy correspond to 3.2
4.  Weak Beat
    4.1     Def: all other offsets not categorised as a strong beat
    4.2     Notes on weak beats ('weak [beat] notes') are W1, W2 ... etc
    4.3     'Weak [beat] intervals' are generally Sx=>Wx, where Wx is the weak note associated with the note on Sx. 
            Technically, Sx is the offset == to Wx's offset %1.0 or %1.5, depending on 3.1.
            Rarely, this will be used to refer to  Wx=>Wy, where Wx and Wy correspond to 4.2
5.  Fingerprint Matrix
    5.1     Def: Matrix representation of the fingerprint. 
    5.2     Actual representation is contained in Laura's Workflow
6. Match, Matched, Matching
    6.1     Match: comparison between two lists (Match(X, Y))
    6.2     Matched: list of positive results from Match(X, Y) 
    6.3     Matching: Act of doing Match(X, Y)
    Note this means that 'List of Matching Strong Beats' makes no sense, whereas List of Matched Strong Beats is syntactically valid
7. Note
    7.1     Def: Scale degree, not note name.

========== Pandas indexing =========
print time_sigs['metre.TimeSignatureIndexer']['0'] # get 1st index: results of TimeSignatureIndexer, then 2nd index: part/voice 0
print time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0] # get 1st time sig...   
print time_sigs['metre.TimeSignatureIndexer']['0'].index[0] # get offset of 1st time sig... 
print time_sigs['metre.TimeSignatureIndexer'].index.values # get the names of the index for each row for TimeSignatureIndexer

========== Contour test set ==========
fp1 = results['Allard_1928_MoneyMusk_B.xml']
fp2 = results['Boivin_YEAR_MoneyMusk_B.xml']
fp3 = results['Potvin_198?_MoneyMusk_K.xml']
fp4 = results['Soucy_1927_MoneyMusk_D.xml']
fp5 = results['Boivin_YEAR_MoneyMusk_E.xml']

fp1 = results['Allard_1928_MoneyMusk_A.xml']
fp2 = results['Allard_1928_MoneyMusk_B.xml']

========= Old comparison =========
    match_count = 0
    matched_intervals = []
    #while list1 and list2:
    for l2_interval in list2:
        if list1[0] == l2_interval:
            match_count += 1
            matched_intervals.append(list1[0])
            #del list2[0:list2.index(l2_interval)]
            #list1.pop(0)
            continue
        #list1 = []

    print matched_intervals
    print match_count


    def compare_lists(list1, list2):
    print "List 1: " + str(list1)
    print "List 2: " + str(list2)
    match_count = 0
    matched_intervals = []
    l1_index = 0
    for l2_interval in list2:
        if not l1_index < len(list1):
            break 
        if list1[l1_index] == l2_interval:
            match_count += 1
            matched_intervals.append(list1[l1_index])
            l1_index +=1

    print "Matched intervals: " + str(matched_intervals)
    print "Count: " + str(match_count)


========== Old Diatonic to Tones converter ==========
# Translate diatonic intervals into intervals with tones... deprecated since addition of byTones setting
def intervals_to_tones(results):
    interval_dict = {
    'P1': 0.0,
    'm2': 0.5,
    'M2': 1.0,
    'm3': 1.5,
    'M3': 2.0,
    'P4': 2.5,
    'A4': 3.0,
    'd5': 3.0,
    'P5': 3.5,
    'm6': 4.0,
    'M6': 4.5,
    'm7': 5.0,
    'M7': 5.5,
    'P8': 0.0,
    '-m2': -0.5,
    '-M2': -1.0,
    '-m3': -1.5,
    '-M3': -2.0,
    '-P4': -2.5,
    '-A4': -3.0,
    '-d5': -3.0,
    '-P5': -3.5,
    '-m6': -4.0,
    '-M6': -4.5,
    '-m7': -5.0,
    '-M7': -5.5,
    '-P8': 0.0,
    '-d1': 0.5,
    }
    for key, df in results.items():
        for i, row in df.iterrows():
            for j, item in row.iteritems():
                if not isinstance(item, basestring) and np.isnan(item):
                    continue
                df.loc[i].loc[j] = interval_dict[item]

l1 = [1,2,3,4,5,6,7,9,4]
l2 = [2,4,6,8,10,12,4]

========= Old Results Formatter =========

# Convert indexer results to format Laura's algorithm expects
def prepare_results(results):
    for name, result in results.iteritems():
        # Transpose, slice bottom row, transpose --- i.e. slice off last column
        result = result.T.iloc[:-1].T
        result = shift_matrix(result)
        results[name] = result


=========== Old Mismatched-Strong weak comparison =========
if (this_index != len(matched_intervals)-1) and np.isnan(this_interval[0]):
    # If the following is a matched strong interval
    if not np.isnan(matched_intervals[this_index+1][0]):
        diff_1 = fp1r1[this_index][0] - fp1r3[this_index]
        diff_2 = fp2r1[this_index][0] - fp2r3[this_index]
        if diff_1 == diff_2:
            matched_weaks[this_index] = 1
        else:
            matched_weaks[this_index] = 0
    # If not
    else:
        # Find the previous matched interval
        previous_intervals = matched_intervals[:this_index]
        previous_match_index = 0
        for j in reversed(range(this_index)):
            if not np.isnan(previous_intervals[j][0]):
                previous_match_index = j
                break
        # Sets i to what Laura calls it... but off by one since she starts at 1
        j = previous_match_index
        i = this_index - j
        # Calculate the results using her formula
        model_result = fp1.iloc[2+i].tolist()[j] + fp1r1[this_index][0]
        print fp1.iloc[1+i].tolist()[j]
        print fp1r1[this_index][0]
        variant_result = fp2.iloc[2+i].tolist()[j] + fp2r1[this_index][0]
        print fp2.iloc[1+i].tolist()[j]
        print fp2r1[this_index][0]
        if model_result == variant_result:
            matched_weaks[this_index] = 1
        else:
            matched_weaks[this_index] = 0

'''

##################### Strong Beat Compares #####################

# LM: Non-int range
def my_range(start, step, stop):
    i = start
    while i < stop:
        yield i
        i += step    

# See if one list exists with interpolation in another
def compare_strong_unequal_lengths(fp1, fp2):
    # Take fp1 to be shorter fingerprint
    #https://docs.python.org/2/library/difflib.html
    fp1c1 = fp1.T.iloc[0].tolist()[1:]
    fp2c1 = fp2.T.iloc[0].tolist()[1:]

    if len(fp1c1) > len(fp2c1):
        temp = fp1c1
        fp1c1 = fp2c1
        fp2c1 = temp
    
    sm=SequenceMatcher(a=fp1c1,b=fp2c1)
    matched_intervals = []

    for (op, start1, end1, start2, end2) in sm.get_opcodes():
        #print (op, start1, end1, start2, end2)
        if op == 'equal':
            #This range appears in both sequences.
            for this_index, this_interval in enumerate(fp1c1[start1:end1]):
                matched_intervals.append([this_interval, start1+this_index, start2+this_index])
                #print matched_intervals

    print "Strong Beat Comparison (different lengths): " + str(matched_intervals)

    return matched_intervals


# Compare two lists by checking the same indices iteratively... works only on equi-length lists
def compare_strong_by_index(fp1, fp2):
    # LM: Extract Column_1 [1:end]: Intervals (0.0, 1.0), (0.0, 2.0), ..., (0.0, end of piece)
    fp1c1 = fp1.T.iloc[0].tolist()[1:]
    fp2c1 = fp2.T.iloc[0].tolist()[1:]

    print "Fingerprint_1 Column_1: " + str(fp1c1)
    print "Fingerprint_2 Column_1: " + str(fp2c1)

    if not len(fp1c1) == len(fp2c1):
        print "List lengths not equal"
        return None
    matched_intervals = []
    for i, val in enumerate(fp1c1):
        #if fp1c1[i] == "Rest":
        #    matched_intervals.append([np.nan, i, i])
        if fp1c1[i] == fp2c1[i]:
            matched_intervals.append([fp1c1[i], i, i])
        else:
            matched_intervals.append([np.nan, i, i])

    print "Strong Beat Comparison (equi-length): " + str(matched_intervals)

    return matched_intervals

##################### Contour Compares #####################

# Compare contours of two fingerprints -- return 1, 0.5, 0 depending on whether mismatched strong intervals have same/similar contours
def compare_contours(matched_intervals, fp1, fp2):
    ##### STRONG CONTOURS #####
    # Extract Row_3: Intervals (0.0, 1.0), (1.0, 2.0), ..., (n-1.0, n.0)
    fp1r3 = fp1.iloc[2].tolist()
    fp2r3 = fp2.iloc[2].tolist()

    # Consecutively misaligned indices (cmi) that need to be checked
    cmi = []
    for i in range(len(matched_intervals)-1):
        if np.isnan(matched_intervals[i][0]) and np.isnan(matched_intervals[i+1][0]):
            cmi.append([matched_intervals[i][1], matched_intervals[i][2]])

    matched_contour = [np.nan]*len(matched_intervals)

    # Similar-contour indicies (sci) where similarity, not identity, is observed 
    sci = [np.nan]*len(matched_intervals)

    # For each consecutively misaligned index (i.e. for each pair of misaligned intervals) in fingerprint 1, check in fingerprint 2
    for [this_index, that_index] in cmi:
        # Contour identity
        if fp1r3[this_index] == fp2r3[this_index]:
            matched_contour[this_index] = 1
        # Contour similarity
        elif abs(fp1r3[this_index] - fp2r3[this_index]) <= 0.5:
            matched_contour[this_index] = fp1r3[this_index] - fp2r3[this_index]
            # If we have a similarity, add that to the similar-contour indices
            sci[this_index] = fp1r3[this_index] - fp2r3[this_index]
        # No contour matching
        else:
            matched_contour[this_index] = 0

    # For each index in the list of similar-contour indices, set to nan if not consecutively similar with another index
    for i, this_index in enumerate(sci):
        # Have to check adjancency both forwards and backwards... TODO have to stop index out of range 
        if i == 0 and (sci[i] == sci[i+1]):
            continue
        elif i == (len(sci)-1) and (sci[i] == sci[i-1]):
            continue
        elif i == 0 or i == (len(sci)-1):
                       sci[i] = np.nan
        elif sci[i] == sci[i+1] or sci[i] == sci[i-1]:
            continue
        else:
            sci[i] = np.nan

    print "Strong Beat Contour Comparison: " + str(matched_contour)
    print "Consecutive Strong Beat Contour Similarity Comparison: " + str(sci)


    ##### WEAK CONTOURS #####
    # Extract Row_1
    fp1r1 = fp1.iloc[0].tolist()
    fp2r1 = fp2.iloc[0].tolist()

    weak_matched_contours = [np.nan]*len(matched_intervals)

    for this_index, this_contour in enumerate(matched_contour):
        if np.isnan(this_contour):
            continue
        elif this_index != (len(matched_contour)-1):
            # Refer to Laura's workflow... old code
            #if fp1r1[this_index][0] == fp2r1[this_index][0]:
            #    weak_matched_contours[this_index] = 1.0
            #elif abs(fp1r1[this_index][0]-fp2r1[this_index][0]) <= 0.5:
            #    weak_matched_contours[this_index] = 0.5
            first_weaks = fp1r1[this_index]
            second_weaks = fp2r1[this_index]

            # Swap depending on length
            if len(first_weaks) > len(second_weaks):
                temp = second_weaks
                second_weaks = first_weaks
                first_weaks = temp

            sm=SequenceMatcher(a=first_weaks,b=second_weaks)
            total_weak_overlaps_inorder = 0

            for (op, start1, end1, start2, end2) in sm.get_opcodes():
                #print (op, start1, end1, start2, end2)
                if op == 'equal':
                    #This range appears in both sequences... add the length of the range including length 0s (1 index)
                    total_weak_overlaps_inorder += (end1 - start1)

            total_weak_overlaps_inorder = float(total_weak_overlaps_inorder)/len(first_weaks)

            weak_matched_contours[this_index] = total_weak_overlaps_inorder
            #start_note_result = 0.5 if (abs(fp1r1[this_index][0]-fp2r1[this_index][0]) <= 0.5) else 0
            #end_note_result = 0.5 if (abs(fp1r1[this_index][0]-fp2r1[this_index][0]) <= 0.5) else 0
            #weak_matched_contours[this_index] = start_note_result + end_note_result


    print "Weak Beat Contour Comparison: " + str(weak_matched_contours)
    
    return[matched_contour, weak_matched_contours]

##################### Displaced Compares #####################

# Compare mismatched strong intervals of two fingerprints to their associated weak intervals
# Will return a list of any displacement of a note on a strong interval  
def compare_strong_displaced_weak(matched_intervals, fp1, fp2):
    # LM: Extract Column_1 [1:end]: Intervals (0.0, 1.0), (0.0, 2.0), ..., (0.0, end of piece)
    fp1c1 = fp1.T.iloc[0].tolist()[1:]
    fp2c1 = fp2.T.iloc[0].tolist()[1:]
    fp1r1 = fp1.iloc[0].tolist()
    fp2r1 = fp2.iloc[0].tolist()

    displacement = [np.nan]*len(matched_intervals)

    if len(fp1c1) == len(fp2c1):
        for this_index, this_interval in enumerate(matched_intervals):
            if np.isnan(this_interval[0]):
                # Get the element (x) at this_index in each of col1, col2 of the fingerprint
                fp1c1x = fp1c1[this_index]
                fp2c1x = fp2c1[this_index]
                fp1r1x = fp1r1[this_index]
                fp2r1x = fp2r1[this_index]
                displacement[this_index] = compare_strong_displaced_weak_helper(fp1c1x, fp2c1x, fp1r1x, fp2r1x)
            else:
                pass
    else:
        # TODO handle unequal lengths
        pass
    print "Displaced Strong to Weak Comparison: " + str(displacement)
    return displacement

def compare_strong_displaced_weak_helper(fp1c1x, fp2c1x, fp1r1x, fp2r1x):
    # Calculate 1st strong note to this weak beat for all weak beats in row 1
    fp1r1x = [weak + fp1c1x for weak in fp1r1x]
    fp2r1x = [weak + fp2c1x for weak in fp2r1x]

    # Check for strong beat displaced in weak beat set
    if (fp2c1x in fp1r1x) or (fp1c1x in fp2r1x):
        return 1
    else:
        return 0


##################### Weak Beat Compares #####################

def compare_matched_strong_associated_weaks(matched_intervals, fp1, fp2):
    fp1c1 = fp1.T.iloc[0].tolist()[1:]
    fp2c1 = fp2.T.iloc[0].tolist()[1:]
    fp1r1 = fp1.iloc[0].tolist()
    fp2r1 = fp2.iloc[0].tolist()

    matched_weaks = [np.nan]*len(matched_intervals)

    if len(fp1c1) == len(fp2c1):
        for this_index, this_interval in enumerate(matched_intervals):
            if np.isnan(this_interval[0]):
                continue
            first_weaks = fp1r1[this_index]
            second_weaks = fp2r1[this_index]
            matched_weaks[this_index] = weak_matching_helper(first_weaks, second_weaks)
    else:
        # TODO handle unequal lengths
        pass
    print "Weak Beats for Matched Strongs Comparison: " + str(matched_weaks)
    return matched_weaks

def compare_mismatched_strong_associated_weaks(matched_intervals, fp1, fp2):
    fp1c1 = fp1.T.iloc[0].tolist()[1:]
    fp2c1 = fp2.T.iloc[0].tolist()[1:]
    fp1r1 = fp1.iloc[0].tolist()
    fp2r1 = fp2.iloc[0].tolist()
    fp1r3 = fp1.iloc[2].tolist()
    fp2r3 = fp2.iloc[2].tolist()

    matched_weaks = [np.nan]*len(matched_intervals)

    if len(fp1c1) == len(fp2c1):
        for this_index, this_interval in enumerate(matched_intervals):
            # If this is not the last interval and is mismatched
            if np.isnan(this_interval[0]):
                first_weaks = [weak + fp1c1[this_index] for weak in fp1r1[this_index]]
                second_weaks = [weak + fp2c1[this_index] for weak in fp2r1[this_index]]
                matched_weaks[this_index] = weak_matching_helper(first_weaks, second_weaks)
            else:
                pass
    else:
        # TODO handle unequal lengths
        pass
    
    print "Weak Beats for Mismatched Strongs Comparison: " + str(matched_weaks)
    return matched_weaks

def weak_matching_helper(first_weaks, second_weaks):
    if set(first_weaks) & set(second_weaks):
        # Choose shorter list... 
        if len(first_weaks) > len(second_weaks):
            temp = second_weaks
            second_weaks = first_weaks
            first_weaks = temp
        # Total weak beats that match
        total_weak_overlaps =  float(len(list(Counter(first_weaks) & Counter(second_weaks))))/float(len(first_weaks))
        # Total weak beatst that match in-order
        # Match sequences   
        sm=SequenceMatcher(a=first_weaks,b=second_weaks)
        total_weak_overlaps_inorder = 0

        for (op, start1, end1, start2, end2) in sm.get_opcodes():
            #print (op, start1, end1, start2, end2)
            if op == 'equal':
                #This range appears in both sequences... add the length of the range including length 0s (1 index)
                total_weak_overlaps_inorder += (end1 - start1)

        total_weak_overlaps_inorder = float(total_weak_overlaps_inorder)/float(len(first_weaks))
        # Tuple representation:
        return [0.5*total_weak_overlaps, 0.5*total_weak_overlaps_inorder]
        #return 0.5*total_weak_overlaps + 0.5*total_weak_overlaps_inorder
    # Tuple representation:
    return [0, 0]
    #return 0


##################### Reversal Compare #####################

def compare_reversals(matched_intervals, fp1, fp2):
    # Compare the strong beats for reversals
    fp1c1 = fp1.T.iloc[0].tolist()[1:]
    fp2c1 = fp2.T.iloc[0].tolist()[1:]

    matched_strong_reversals = [np.nan]*len(matched_intervals)

    for this_index, this_interval in enumerate(matched_intervals):
        if this_index != len(matched_intervals) - 1 and np.isnan(this_interval[0]) and np.isnan(matched_intervals[this_index+1][0]):
            if fp1c1[this_index] == fp2c1[this_index+1] and fp1c1[this_index+1] == fp2c1[this_index]:
                matched_strong_reversals[this_index] = 1
    
    print "Strong Beat Reversal Comparison: " + str(matched_strong_reversals)

    # Compare the weak beats for reversals
    fp1r1 = fp1.iloc[0].tolist()
    fp2r1 = fp2.iloc[0].tolist()

    matched_weak_reversals = [np.nan]*len(matched_strong_reversals)

    for this_index, this_reversal in enumerate(matched_strong_reversals):
        if not np.isnan(this_reversal):
            # Refer to workflow

            # Calculate overlaps (nonordered / ordered).... For fp1 strong 1 and fp2 strong 2
            #if set(fp1r1[this_index]) & set(fp2r1[this_index+1]):
            first_weaks1 = fp1r1[this_index]
            second_weaks1 = fp2r1[this_index+1]
            first_result = weak_matching_helper(first_weaks1, second_weaks1)

            # Calculate overlaps (nonordered / ordered).... For fp1 strong 2 and fp2 strong 1
            #if set(fp2r1[this_index]) & set(fp1r1[this_index+1]):
            first_weaks2 = fp2r1[this_index]
            second_weaks2 = fp1r1[this_index+1]

            second_result = weak_matching_helper(first_weaks2, second_weaks2)

            #first_result = 0.5 if set(fp1r1[this_index]) & set(fp2r1[this_index+1]) else 0
            #second_result = 0.5 if set(fp2r1[this_index]) & set(fp1r1[this_index+1]) else 0

            matched_weak_reversals[this_index] = [first_result, second_result]

    print "Weak Beat Reversal Comparison: " + str(matched_weak_reversals)

    return [matched_strong_reversals, matched_weak_reversals]



##################### Parent Compare #####################

# Parent comparison function
def compare(fp1, fp2):
    print "Fingerprint 1: "
    print fp1
    print "Fingerprint 2: "
    print fp2

    # LM: Extract Column_1 [1:end]: Intervals (0.0, 1.0), (0.0, 2.0), ..., (0.0, end of piece)
    # Recursive call: will be i to j of i < n-1, j < n where n = max offsets
    fp1c1 = fp1.T.iloc[0].tolist()[1:]
    fp2c1 = fp2.T.iloc[0].tolist()[1:]

    comparison_results = []
    comparison_result_indices = []

    # LM: Do Strong-Strong comparison 
    if len(fp1.iloc[0]) == len(fp2.iloc[0]):
        matched_intervals = compare_strong_by_index(fp1, fp2)
    else:
        matched_intervals = compare_strong_unequal_lengths(fp1, fp2)
        return None

    comparison_result_indices.append('Strong Beat Comparison')
    comparison_results.append(matched_intervals)

   # LM: Do Matched-Strong weak comparison
    comparison_result_indices.append('Weak Beats Comparison (Matched Strongs)')
    comparison_results.append(compare_matched_strong_associated_weaks(matched_intervals, fp1, fp2))

    # LM: Do Mismatched-Strong weak comparison
    comparison_result_indices.append('Weak Beats Comparison (Mismatched Strongs)')
    comparison_results.append(compare_mismatched_strong_associated_weaks(matched_intervals, fp1, fp2))

    # LM: Do contour comparison 
    comparison_result_indices.append('Contour Comparison (Strongs)')
    comparison_result_indices.append('Contour Comparison (Weaks)')
    comparison_results.extend(compare_contours(matched_intervals, fp1, fp2))

    # LM: Do Strong-Weak displacement comparison 
    comparison_result_indices.append('Displacement Comparison (Strong-Weak)')
    comparison_results.append(compare_strong_displaced_weak(matched_intervals, fp1, fp2))

    # LM: Do Reversed-Strong comparison
    comparison_result_indices.append('Reversal Comparison (Strongs)')
    comparison_result_indices.append('Reversal Comparison (Weaks)')
    comparison_results.extend(compare_reversals(matched_intervals, fp1, fp2))

    # LM: Construct the results of the comparison
    comparison_results = DataFrame(comparison_results)
    comparison_results.index = comparison_result_indices
    comparison_results.columns = range(1, len(matched_intervals)+1)
    #comparison_results.T

    print comparison_results
    return None

# Used in the above to push results to the front of their Series object
def shift_matrix(df):
    for i in range(0, len(df.columns)):
        df.iloc[i] = df.iloc[i].shift(-i)
    return df

# Build dataframe of strong-beat intervals here:
def build_strong_intervals(piece, interval_settings, strong_beat_offsets, total_offsets):
    # LM: Build all intervals between all combinations of strong beats 
    # LM: Workflow - get notes & rests, take the fingerprint subsection, filter for strong beats, get horizontal intervals for each distance
    # Do this for horizontal intervals over 1.0 offset increments, 2.0 offset increments....
    # For i = 1.0 to the total allowable distance between two notes, which is the total number of offsets
    # Change this to 1.5 for 6/8 or 9/8 sigs
    strong_intervals_frame =[] 
    for i in my_range(strong_beat_offsets, strong_beat_offsets, total_offsets):
        interval_settings['intervalDistance'] = i
        strong_intervals = piece.get_data([noterest.NoteRestIndexer, subsection.SubsectionIndexer, offset.FilterByOffsetIndexer, interval.VariableHorizontalIntervalIndexer], interval_settings)
        strong_intervals = strong_intervals['interval.VariableHorizontalIntervalIndexer']['0']
        strong_intervals_frame.append(strong_intervals)

    # Build strong-beat frame
    strong_intervals_frame = DataFrame(strong_intervals_frame)
    strong_intervals_frame.index = my_range(strong_beat_offsets, strong_beat_offsets, total_offsets)

    return strong_intervals_frame

def build_weak_intervals(piece, interval_settings, strong_beat_offsets, total_offsets):
    # LM: Now build the weak intervals
    # LM: Workflow - get notes & rests, take the fingerprint subsection, get horizontal intervals for all consecutive notes
    all_intervals = piece.get_data([noterest.NoteRestIndexer, subsection.SubsectionIndexer, interval.HorizontalIntervalIndexer], interval_settings)
    # Have to ignore the last result because we start indexing intervals from the first strong beat.
    all_intervals = all_intervals['interval.HorizontalIntervalIndexer']['0'].iloc[:]
    # Length of weak_intervals is 1 shorter than total_offsets/strong_beat_offsets because we start indexing intervals from the first strong beat.
    # See line 251
    weak_intervals = [[np.nan]]*int((total_offsets)/strong_beat_offsets)
    for this_offset, this_interval in all_intervals.iteritems():
        # Ignore if this is an interval ending on the strong beat
        if this_offset % strong_beat_offsets == 0.0:
            continue
        # Find index in list using the closest strong beat
        closest_strong_beat = this_offset - (this_offset % strong_beat_offsets)
        this_index = int((closest_strong_beat)/strong_beat_offsets)
        # If no previous weak beat, set this interval
        if np.isnan(weak_intervals[this_index][-1]):
            weak_intervals[this_index] = [this_interval]
        # If there was a previous weak beat, add intervals accordingly
        elif weak_intervals[this_index][-1] >= 0:
            weak_intervals[this_index].append((weak_intervals[this_index][-1] + this_interval) % 6.0)
        else:
            weak_intervals[this_index].append((weak_intervals[this_index][-1] + this_interval) % -6.0)

    # Add weak intervals to the strong-beat frame
    weak_intervals = DataFrame(Series(weak_intervals))

    return weak_intervals

def remove_rests(fp):
    pass

def build_fingerprint_matrices(pathnames, number_of_fingerprints = 10000):
    # pathnames: List of paths to each piece for which a fingerprint matrix should be built
    # number_of_fingerprints: however many fingerprints you need
    results = {}

    for path in pathnames:
        # Setup for each piece
        print("Indexing " + path)
        piece = IndexedPiece(path)
        piece_stream = music21.converter.parseFile(path)

        # LM: Get time signature and determine strong beats
        time_sigs = piece.get_data([metre.TimeSignatureIndexer])
        # Assuming no time signature change in whole piece, assign offsets to strong beats
        if time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0] == '6/8' or time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0] == '9/8':
            strong_beat_offsets = 1.5
            measures = 2
        else:
            strong_beat_offsets = 1.0
            measures = 2
        # LM: Get total number of offsets
        numer, denom = time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0].split('/')
        # Two bars worth of offsets, ignoring anacrusis...
        # Add an extra strong beat at end 
        total_offsets = int(numer) * measures*4.0/int(denom) + strong_beat_offsets

        interval_settings['quarterLength'] = strong_beat_offsets
        interval_settings['intervalDistance'] = strong_beat_offsets
        interval_settings['subsection'] = (0.0, total_offsets)

        # LM: Build strong-interval frame
        strong_intervals = build_strong_intervals(piece, interval_settings, strong_beat_offsets, total_offsets)

        # LM: Build weak-interval frame
        weak_intervals = build_weak_intervals(piece, interval_settings, strong_beat_offsets, total_offsets)

        # LM: Assemble results
        # 1. Prepare strong_intervals -- had to change this due to change in representation... take off final column (start of new bar)
        # Take off second last column (cross-over bar):
        strong_intervals = strong_intervals.T.iloc[:-1].T
        strong_intervals = shift_matrix(strong_intervals)
        # Had to change this due to change in representation.... take off final row
        # strong_intervals = strong_intervals.iloc[:]
        
        # 2. Prepare weak_intervals:
        weak_intervals = weak_intervals.iloc[:]
        weak_intervals.index = my_range(strong_beat_offsets, strong_beat_offsets, total_offsets+strong_beat_offsets)

        # 3. Row of 0s --- added after discussion with Laura pertaining to fingerprint representation
        zeros = DataFrame(Series([0.0]*(len(weak_intervals))))
        zeros.index = (my_range(strong_beat_offsets, strong_beat_offsets, total_offsets+strong_beat_offsets))
        zeros = zeros.T

        # 4. Append 
        fingerprint_frame = pandas.concat([weak_intervals.T, zeros, strong_intervals])
        fingerprint_frame.index = (['w'] + fingerprint_frame.index.tolist()[1:])

        #piece_stream.show('musicxml', 'MuseScore')   
        #  DataFrame(Series([0.0]*(len(weak_intervals)+1))).reindex(range(1, len(weak_intervals)+1)).T
        results[os.path.basename(path)]=fingerprint_frame
            
        number_of_fingerprints -= 1
        if 0 == number_of_fingerprints:
            break

    return results

# Anything that should be chained together is here temporarily
def run():
    compare(results['Allard_1928_MoneyMusk_A.xml'], results['Allard_1928_MoneyMusk_B.xml'])

# Settings:
pandas.set_option('display.height', 1000)
pandas.set_option('display.max_rows', 500)
pandas.set_option('display.max_columns', 500)
pandas.set_option('display.width', 1000)

# Workflow for Risk project -- fingerprint horizontal interval indexer
# Will be used as the init later on
test_set_path = "../risk_test_set/"
pathnames = [ os.path.join(test_set_path, f) for f in os.listdir(test_set_path) if os.path.isfile(os.path.join(test_set_path, f)) and not f.startswith('.')]
interval_settings = {'quality': True, 'simple or compound': 'simple', 'byTones':True}

results = build_fingerprint_matrices(pathnames, 10000)

# LM: Run interpreter on command line
import readline 
import code
vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
shell.interact()




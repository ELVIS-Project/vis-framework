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
import pickle

''' INFO/USEFULS
==========================================================================================
============= SHIFT Project -- Similar Horizontal Intervals in Fiddle Tunes ==============

Laura Risk, Lillio Mok

Requirements: VIS on the risk_project branch


Winter 2015 TODOS:
Database -- see list
Ensure recursive comparison works
Unequal lengths -- add special case for doubled number of strong beats. Compare every other strong beat in longer fingerprint. Compare remaining 
    strong beats to weak beats in shorter fingerprint.
    1. Make new strong beat comparison method, align according to above description

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
    5.2     Details are in Laura's Workflow
6. Corresponding, Match, Matched, Matching
    6.1     Corresponding: The elements in two lists that are thought to musically 'align' with each other. Notes may correspond and be matched/mismatched.
    6.2     Match: comparison between two lists (Match(X, Y))
    6.3     Matched: list of positive results from Match(X, Y) 
    6.4     Matching: Act of doing Match(X, Y)
    Note this means that 'List of Matching Strong Beats' makes no sense, whereas List of Matched Strong Beats is syntactically valid
7. Note
    7.1     Def: Scale degree, not note name.

========== Pandas indexing =========
print time_sigs['metre.TimeSignatureIndexer']['0'] # get 1st index: results of TimeSignatureIndexer, then 2nd index: part/voice 0
print time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0] # get 1st time sig...   
print time_sigs['metre.TimeSignatureIndexer']['0'].index[0] # get offset of 1st time sig... 
print time_sigs['metre.TimeSignatureIndexer'].index.values # get the names of the index for each row for TimeSignatureIndexer
print time_sigs['metre.TimeSignatureIndexer'].columns.values # get the names of the column for each column from TimeSignatureIndexer

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


=========== Time Signature Modifier =========
    # Allowing for changes in time signature
    offset_boundaries = []
    offset_increments = []
    time_sig_measures = []
    print time_sigs
    for i in range(0, len(time_sigs)):
        print i
        time_sig_offset = time_sigs.index[i]
        print time_sig_offset
        this_time_sig = time_sigs['metre.TimeSignatureIndexer']['0'].loc[time_sig_offset]
        print this_time_sig
        if this_time_sig == '6/8' or this_time_sig == '9/8':
            offset_increments.append(1.5)
        else:
            offset_increments.append(1.0)
        offset_boundaries.append(float(time_sig_offset))
        print offset_increments
        print offset_boundaries
        numer, denom = this_time_sig.split('/')
        offsets_per_measure = float(numer) * 4.0/float(denom)

        if i == len(time_sigs)-1:
            time_sig_measures.append(None)
        else:
            time_sig_measures.append(float(time_sigs.index[i+1] - time_sigs.index[i])/offsets_per_measure)

    print offset_increments
    print offset_boundaries
    print time_sig_measures

    return None

'''

# LM: Non-int range
def my_range(start, step, stop):
    i = start
    while i < stop:
        yield i
        i += step    

class FingerprintComparer:

    similarity_matrix = None

    sim_pickle_path = None

    def __init__(self, fingerprint_matrices=None, sim_pickle_path=None):
        self.sim_pickle_path = sim_pickle_path
        self.similarity_matrix = self.build_similarity_matrix(fingerprint_matrices)
        self.dump_similarity_matrix()
    
    ##################### Strong Beat Compares #####################

    # See if one list exists with interpolation in another
    def compare_strong_unequal_lengths(self, fp1, fp2):
        # Take fp1 to be shorter fingerprint
        #https://docs.python.org/2/library/difflib.html
        fp1c1 = fp1.T.iloc[0].tolist()[1:]
        fp2c1 = fp2.T.iloc[0].tolist()[1:]

        if len(fp1c1) > len(fp2c1):
            temp = fp1c1
            fp1c1 = fp2c1
            fp2c1 = temp
        
        # Want first fingerprint to be longer
        sm=SequenceMatcher(a=fp1c1,b=fp2c1)
        matched_intervals = []

        for (op, start1, end1, start2, end2) in sm.get_opcodes():
            #print (op, start1, end1, start2, end2)
            if op == 'equal':
                #This range appears in both sequences.
                for this_index, this_interval in enumerate(fp1c1[start1:end1]):
                    matched_intervals.append([this_interval, start1+this_index, start2+this_index])
            if op == 'delete' and end1-start1 == end2-start2:
                for this_index in range(end1-start1):
                    matched_intervals.append([np.nan, start1+this_index, start2+this_index])

        #print "Strong Beat Comparison (different lengths): " + str(matched_intervals)

        return matched_intervals

    # Compare two lists by checking the same indices iteratively... works only on equi-length lists
    def compare_strong_by_index(self, fp1, fp2):
        # LM: Extract Column_1 [1:end]: Intervals (0.0, 1.0), (0.0, 2.0), ..., (0.0, end of piece)
        fp1c1 = fp1.T.iloc[0].tolist()[1:]
        fp2c1 = fp2.T.iloc[0].tolist()[1:]

        matched_intervals = []
        for i, val in enumerate(fp1c1):
            #if fp1c1[i] == "Rest":
            #    matched_intervals.append([np.nan, i, i])
            if fp1c1[i] == fp2c1[i]:
                matched_intervals.append([fp1c1[i], i, i])
            else:
                matched_intervals.append([np.nan, i, i])

        #print "Strong Beat Comparison (equi-length): " + str(matched_intervals)

        return matched_intervals


    ##################### Displacement Compares #####################

    # Compare mismatched strong intervals of two fingerprints to their associated weak intervals
    # Will return a list of any displacement of a note on a strong interval  
    def compare_strong_displaced_weak(self, matched_intervals, fp1, fp2):
        # LM: Extract Column_1 [1:end]: Intervals (0.0, 1.0), (0.0, 2.0), ..., (0.0, end of piece)
        fp1c1 = fp1.T.iloc[0].tolist()[1:]
        fp2c1 = fp2.T.iloc[0].tolist()[1:]
        fp1r1 = fp1.iloc[0].tolist()
        fp2r1 = fp2.iloc[0].tolist()

        displacement = [np.nan]*len(matched_intervals)

        for this_index, [this_interval, this_index_1, this_index_2] in enumerate(matched_intervals):
            if np.isnan(this_interval):
                # Get the element (x) at this_index in each of col1, col2 of the fingerprint
                fp1c1x = fp1c1[this_index_1]
                fp2c1x = fp2c1[this_index_2]
                fp1r1x = fp1r1[this_index_1]
                fp2r1x = fp2r1[this_index_2]
                displacement[this_index] = self.compare_strong_displaced_weak_helper(fp1c1x, fp2c1x, fp1r1x, fp2r1x)
            else:
                pass

        #print "Displaced Strong to Weak Comparison: " + str(displacement)
        return displacement

    def compare_strong_displaced_weak_helper(self, fp1c1x, fp2c1x, fp1r1x, fp2r1x):
        # Calculate 1st strong note to this weak beat for all weak beats in row 1
        fp1r1x = [weak + fp1c1x for weak in fp1r1x]
        fp2r1x = [weak + fp2c1x for weak in fp2r1x]

        # Check for strong beat displaced in weak beat set
        if (fp2c1x in fp1r1x) or (fp1c1x in fp2r1x):
            return 1
        else:
            return 0


    ##################### Weak Beat Compares #####################

    def compare_matched_strong_associated_weaks(self, matched_intervals, fp1, fp2):
        fp1c1 = fp1.T.iloc[0].tolist()[1:]
        fp2c1 = fp2.T.iloc[0].tolist()[1:]
        fp1r1 = fp1.iloc[0].tolist()
        fp2r1 = fp2.iloc[0].tolist()

        matched_weaks = [np.nan]*len(matched_intervals)

        for this_index, [this_interval, this_index_1, this_index_2] in enumerate(matched_intervals):
            if np.isnan(this_interval):
                continue
            first_weaks = fp1r1[this_index_1]
            second_weaks = fp2r1[this_index_2]
            matched_weaks[this_index] = self.weak_matching_helper(first_weaks, second_weaks)

        #print "Weak Beats for Matched Strongs Comparison: " + str(matched_weaks)
        return matched_weaks

    def compare_mismatched_strong_associated_weaks(self, matched_intervals, fp1, fp2):
        fp1c1 = fp1.T.iloc[0].tolist()[1:]
        fp2c1 = fp2.T.iloc[0].tolist()[1:]
        fp1r1 = fp1.iloc[0].tolist()
        fp2r1 = fp2.iloc[0].tolist()
        fp1r3 = fp1.iloc[2].tolist()
        fp2r3 = fp2.iloc[2].tolist()

        matched_weaks = [np.nan]*len(matched_intervals)


        for this_index, [this_interval, this_index_1, this_index_2] in enumerate(matched_intervals):
            # If this is not the last interval and is mismatched
            if np.isnan(this_interval):
                first_weaks = [weak + fp1c1[this_index_1] for weak in fp1r1[this_index_1]]
                second_weaks = [weak + fp2c1[this_index_2] for weak in fp2r1[this_index_2]]
                matched_weaks[this_index] = self.weak_matching_helper(first_weaks, second_weaks)
            else:
                pass

        #print "Weak Beats for Mismatched Strongs Comparison: " + str(matched_weaks)
        return matched_weaks

    def weak_matching_helper(self, first_weaks, second_weaks):
        if len(first_weaks) == 1 and len(second_weaks) == 1 and np.isnan(first_weaks[0]) and np.isnan(second_weaks[0]):
                return [1.0, 1.0]
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
            return [total_weak_overlaps, total_weak_overlaps_inorder]
            #return 0.5*total_weak_overlaps + 0.5*total_weak_overlaps_inorder
        # Tuple representation:
        return [0, 0]
        #return 0


    ##################### Contour Compares #####################

    # Compare contours of two fingerprints -- return 1, 0.5, 0 depending on whether mismatched strong intervals have same/similar contours
    def compare_contours(self, matched_intervals, fp1, fp2):
        ##### STRONG CONTOURS #####
        # Extract Row_3: Intervals (0.0, 1.0), (1.0, 2.0), ..., (n-1.0, n.0)
        fp1r3 = fp1.iloc[2].tolist()
        fp2r3 = fp2.iloc[2].tolist()

        # Consecutively mismatched indices (cmi) that need to be checked
        cmi = []

        # Similar-contour indicies (sci) where similarity, not identity, is observed 
        sci = [np.nan]*len(matched_intervals)

        # Compare up to the last matched interval... there is no interval after the last, so do not compute contour comparison
        for i in range(len(matched_intervals)-1):
            if np.isnan(matched_intervals[i][0]) and np.isnan(matched_intervals[i+1][0]):
                cmi.append([i, matched_intervals[i][1], matched_intervals[i][2]])

        matched_contour = [np.nan]*len(matched_intervals)
        matched_contour_extended = [[np.nan]*3]*len(matched_intervals)

        # For each consecutively misaligned index (i.e. for each pair of misaligned intervals) in fingerprint 1, check in fingerprint 2
        for [this_index, this_index_1, this_index_2] in cmi:
            # Contour identity
            if fp1r3[this_index_1] == fp2r3[this_index_2]:
                matched_contour[this_index] = 1
                matched_contour_extended[this_index] = [1, this_index_1, this_index_2]
            # Contour similarity
            elif abs(fp1r3[this_index_1] - fp2r3[this_index_2]) <= 0.5:
                matched_contour[this_index] = fp1r3[this_index_1] - fp2r3[this_index_2]
                matched_contour_extended[this_index] = [fp1r3[this_index_1] - fp2r3[this_index_2], this_index_1, this_index_2]
                # If we have a similarity, add that to the similar-contour indices
                sci[this_index] = fp1r3[this_index_1] - fp2r3[this_index_2]
            # No contour matching
            else:
                matched_contour[this_index] = 0
                matched_contour_extended[this_index] = [0, this_index_1, this_index_2]
        
        # For each index in the list of similar-contour indices, set to nan if not consecutively similar with another index
        # If sci is only length 1, then there can be no consecutively similar contours
        for i, this_index in enumerate(sci):
            # Have to check adjancency both forwards and backwards... TODO have to stop index out of range 
            if i == 0 and (len(sci) != 1) and (sci[i] == sci[i+1]):
                continue
            elif i == (len(sci)-1) and (len(sci) != 1) and (sci[i] == sci[i-1]):
                continue
            elif i == 0 or i == (len(sci)-1):
                sci[i] = np.nan  
            elif sci[i] == sci[i+1] or sci[i] == sci[i-1]:
                continue
            else:
                sci[i] = np.nan

        #print "Strong Beat Contour Comparison: " + str(matched_contour)
        #print "Consecutive Strong Beat Contour Similarity Comparison: " + str(sci)


        ##### WEAK CONTOURS #####
        # Extract Row_1
        fp1r1 = fp1.iloc[0].tolist()
        fp2r1 = fp2.iloc[0].tolist()

        weak_matched_contours = [np.nan]*len(matched_intervals)

        for this_index, [this_contour, this_index_1, this_index_2] in enumerate(matched_contour_extended):
            if np.isnan(this_contour):
                continue
            elif this_index != (len(matched_contour)-1):
                # Refer to Laura's workflow... old code
                #if fp1r1[this_index][0] == fp2r1[this_index][0]:
                #    weak_matched_contours[this_index] = 1.0
                #elif abs(fp1r1[this_index][0]-fp2r1[this_index][0]) <= 0.5:
                #    weak_matched_contours[this_index] = 0.5
                first_weaks = fp1r1[this_index_1]
                second_weaks = fp2r1[this_index_2]
                weak_matched_contours[this_index] = self.weak_matching_helper(first_weaks, second_weaks)[1]
                #start_note_result = 0.5 if (abs(fp1r1[this_index][0]-fp2r1[this_index][0]) <= 0.5) else 0
                #end_note_result = 0.5 if (abs(fp1r1[this_index][0]-fp2r1[this_index][0]) <= 0.5) else 0
                #weak_matched_contours[this_index] = start_note_result + end_note_result

        #print "Weak Beat Contour Comparison: " + str(weak_matched_contours)
        
        return[matched_contour, weak_matched_contours]


    ##################### Reversal Compare #####################

    # Detect reversal of strong-beat material ... will return 1 or 0 if detected for strong beats
    # Returns 2 fractions for weak beats: frac 1 = (nonordered weak-beat matches / ordered weak beats) in fp1 strong beat 1 reversed to fp2 
    # strong beat 2. 
    def compare_reversals(self, matched_intervals, fp1, fp2):
        # Compare the strong beats for reversals
        fp1c1 = fp1.T.iloc[0].tolist()[1:]
        fp2c1 = fp2.T.iloc[0].tolist()[1:]

        matched_strong_reversals = [np.nan]*len(matched_intervals)
        matched_strong_reversals_extended = [[np.nan]*3]*len(matched_intervals)

        for this_index, [this_interval, this_index_1, this_index_2] in enumerate(matched_intervals):
            if this_index != len(matched_intervals) - 1 and np.isnan(this_interval) and np.isnan(matched_intervals[this_index+1][0]):
                # Reversal condition - swapping of strong beats
                if fp1c1[this_index_1] == fp2c1[this_index_2+1] and fp1c1[this_index_1+1] == fp2c1[this_index_2]:
                    matched_strong_reversals[this_index] = 1
                    matched_strong_reversals_extended[this_index] = [1, this_index_1, this_index_2]
        
        #print "Strong Beat Reversal Comparison: " + str(matched_strong_reversals)

        ##### WEAK REVERSALS #####
        # Compare the weak beats for reversals
        fp1r1 = fp1.iloc[0].tolist()
        fp2r1 = fp2.iloc[0].tolist()

        matched_weak_reversals = [np.nan]*len(matched_strong_reversals)

        for this_index, [this_reversal, this_index_1, this_index_2] in enumerate(matched_strong_reversals_extended):
            if not np.isnan(this_reversal):
                # Refer to workflow

                # Calculate overlaps (nonordered / ordered).... For fp1 strong 1 and fp2 strong 2
                #if set(fp1r1[this_index]) & set(fp2r1[this_index+1]):
                first_weaks1 = fp1r1[this_index_1]
                second_weaks1 = fp2r1[this_index_2+1]
                first_result = self.weak_matching_helper(first_weaks1, second_weaks1)

                # Calculate overlaps (nonordered / ordered).... For fp1 strong 2 and fp2 strong 1
                #if set(fp2r1[this_index]) & set(fp1r1[this_index+1]):
                first_weaks2 = fp2r1[this_index_2]
                second_weaks2 = fp1r1[this_index_1+1]
                second_result = self.weak_matching_helper(first_weaks2, second_weaks2)

                #first_result = 0.5 if set(fp1r1[this_index]) & set(fp2r1[this_index+1]) else 0
                #second_result = 0.5 if set(fp2r1[this_index]) & set(fp1r1[this_index+1]) else 0

                matched_weak_reversals[this_index] = [first_result, second_result]

        #print "Weak Beat Reversal Comparison: " + str(matched_weak_reversals)

        return [matched_strong_reversals, matched_weak_reversals]


    ##################### Parent Compare #####################

    def similarity_measure(self, comparison_results):
        # Note: dependent on index labelling in comparison function... see __compare_recursive()

        # Length of the comparison results matrix -- not the same as the fingerprint lengths
        length = len(comparison_results.columns)

        # No results

        if length == 0:
            return 0.0
        
        # All of the following variables include the leading strong beat (SB1=>SB1)
        # Number of Truncations
        truncations = comparison_results.loc['Number of Truncations'].iloc[0]
        # Length of shorter FP in strong beats
        shorter_length = comparison_results.loc['Shorter Incipit Length'].iloc[0]
        # Length of longer FP in strong beats
        longer_length = comparison_results.loc['Longer Incipit Length'].iloc[0]
        # Number of matching strong beats that match (after trunctations) that are in the (not truncated) first half of shorter fingerprint
        matching_strongs_first_half = len(filter(lambda x: True if not np.isnan(x[0]) and (x[1] + truncations) <= shorter_length/2 else False,
            comparison_results.loc['Strong Beat Comparison'].tolist()))

        # Strong Beat Percentage
        matching_strongs = 0.0
        for [this_interval, fp1_index, fp2_index] in comparison_results.loc['Strong Beat Comparison'].tolist():
            matching_strongs = matching_strongs if np.isnan(this_interval) else matching_strongs + 1

        displaced_strongs = 0.0
        for result in comparison_results.loc['Displacement Comparison (Strong-Weak)'].tolist():
            displaced_strongs = displaced_strongs + 1 if (result == 1) else displaced_strongs

        strong_beat_parameter = (matching_strongs + displaced_strongs/2)/length
        
        # Weak Beat Percentage
        matching_weaks = 0.0
        for result in (comparison_results.loc['Weak Beats Comparison (Matched Strongs)'].tolist() + 
            comparison_results.loc['Weak Beats Comparison (Mismatched Strongs)'].tolist()):
            if (isinstance(result, list)) and result[0] != 0:
                matching_weaks += 1

        weak_beat_parameter = matching_weaks/length

        # Strong Beat Contours + Reversals
        value = 0.0
        for result in (comparison_results.loc['Contour Comparison (Strongs)'].tolist() + 
            comparison_results.loc['Reversal Comparison (Strongs)'].tolist()):
            if not np.isnan(result):
                value += result

        strong_contour_rev_parameter = value/length

        # Weak Beat Contours + Reversals
        value = 0.0
        for result in comparison_results.loc['Contour Comparison (Weaks)'].tolist():
            if not np.isnan(result):
                value += result

        for result in comparison_results.loc['Reversal Comparison (Weaks)'].tolist():
            if (isinstance(result, list)):
                fraction_1 = 0 if result[0][0] == 0 else float(result[0][0])/result[0][1]
                fraction_2 = 0 if result[1][0] == 0 else float(result[1][0])/result[1][1]
                value += (fraction_1 + fraction_2)/2

        weak_contour_rev_parameter = value/length

        return strong_beat_parameter + weak_beat_parameter + (strong_contour_rev_parameter + weak_contour_rev_parameter)/2

    def _compare(self, fp1, fp2):
        # LM: Extract Column_1 [1:end]: Intervals (0.0, 1.0), (0.0, 2.0), ..., (0.0, end of piece)
        # Recursive call: will be i to j of i < n-1, j < n where n = max offsets
        fp1c1 = fp1.T.iloc[0].tolist()[1:]
        fp2c1 = fp2.T.iloc[0].tolist()[1:]

        comparison_results = []
        comparison_result_indices = []

        if len(fp1c1) > len(fp2c1):
            temp = fp1
            fp1 = fp2
            fp2 = temp

        # LM: Do Strong-Strong comparison 
        # TODO: Add special case of doubled number of strong beats
        if len(fp1.iloc[0]) == len(fp2.iloc[0]):
            matched_intervals = self.compare_strong_by_index(fp1, fp2)
        else:
            matched_intervals = self.compare_strong_unequal_lengths(fp1, fp2)

        total_mismatch = 0

        for [this_interval, fp1_index, fp2_index] in matched_intervals:
            total_mismatch = total_mismatch + 1 if np.isnan(this_interval) else total_mismatch

        comparison_result_indices.append('Strong Beat Comparison')
        comparison_results.append(matched_intervals)

        # Do Strong-Weak displacement comparison 
        comparison_result_indices.append('Displacement Comparison (Strong-Weak)')
        comparison_results.append(self.compare_strong_displaced_weak(matched_intervals, fp1, fp2))

        # Do Matched-Strong weak comparison
        comparison_result_indices.append('Weak Beats Comparison (Matched Strongs)')
        comparison_results.append(self.compare_matched_strong_associated_weaks(matched_intervals, fp1, fp2))

        # Do Mismatched-Strong weak comparison
        comparison_result_indices.append('Weak Beats Comparison (Mismatched Strongs)')
        comparison_results.append(self.compare_mismatched_strong_associated_weaks(matched_intervals, fp1, fp2))

        # Do contour comparison 
        comparison_result_indices.append('Contour Comparison (Strongs)')
        comparison_result_indices.append('Contour Comparison (Weaks)')
        comparison_results.extend(self.compare_contours(matched_intervals, fp1, fp2))

        # Do Reversed-Strong comparison
        comparison_result_indices.append('Reversal Comparison (Strongs)')
        comparison_result_indices.append('Reversal Comparison (Weaks)')
        comparison_results.extend(self.compare_reversals(matched_intervals, fp1, fp2))

        # Construct the results of the comparison
        comparison_results = DataFrame(comparison_results)
        comparison_results.index = comparison_result_indices
        comparison_results.columns = range(1, len(matched_intervals)+1)
        #comparison_results.T

        return comparison_results

    # Parent comparison function
    def compare(self, fp1, fp2, verbose=False):
        max_calls = len(fp1.iloc[0]) if (len(fp1.iloc[0]) < len(fp2.iloc[0])) else len(fp2.iloc[0])
        best_similarity_measure = -1
        best_comparison_result = None
        fp1_truncated = fp1
        fp2_truncated = fp2

        if verbose:
            print "=========================================================================================================================="
            print "======================================================= Comparing: ======================================================="
            print "=========================================================================================================================="
            print "Fingerprint 1: "
            print fp1
            print "Fingerprint 2: "
            print fp2
            print ""

            # Round up after halving
        for i in range(int((max_calls+1)/2)):
            fp1_truncated = fp1.iloc[:-i].T.iloc[i:].T if i != 0 else fp1
            fp2_truncated = fp2.iloc[:-i].T.iloc[i:].T if i != 0 else fp2
            
            if verbose:
                print "=============== Truncation: " + str(i) + " ==============="
                print "Fingerprint 1: "
                print fp1_truncated
                print "Fingerprint 2: "
                print fp2_truncated
            
            comparison_result = self._compare(fp1_truncated, fp2_truncated)
            comparison_result.loc['Shorter FP Length'] = len(fp1.iloc[0]) if (len(fp1.iloc[0]) < len(fp2.iloc[0])) else len(fp2.iloc[0])
            comparison_result.loc['Longer FP Length'] = len(fp1.iloc[0]) if (len(fp1.iloc[0]) > len(fp2.iloc[0])) else len(fp2.iloc[0])
            comparison_result.loc['Shorter Incipit Length'] = len(fp1.iloc[0]) if (len(fp1.iloc[0]) < len(fp2.iloc[0])) else len(fp2.iloc[0])
            comparison_result.loc['Longer Incipit Length'] = len(fp1.iloc[0]) if (len(fp1.iloc[0]) > len(fp2.iloc[0])) else len(fp2.iloc[0])
            comparison_result.loc['Number of Truncations'] = i
            
            similarity_measure = self.similarity_measure(comparison_result)
            
            if verbose:
                print "------------ Comparison Results: -------------"
                print comparison_result
                print "------------ Similarity Measure: " + str(similarity_measure) + " -------------"
                print ""

            if similarity_measure > best_similarity_measure:
                best_similarity_measure = similarity_measure
                best_comparison_result = comparison_result
                #best_comparison_result.loc['Number of Truncations'] = i

        if verbose:
            print "======================================================= Best Result: ======================================================="
            print best_comparison_result
            print "Best Similarity Measure: " + str(best_similarity_measure)
            print "============================================================================================================================"
            print ""

        return best_comparison_result

    # build similarity matrix
    def build_similarity_matrix(self, fingerprint_matrices):
        if fingerprint_matrices == None:
            return None
        names = fingerprint_matrices.keys()
        similarity_matrix = DataFrame(index=names, columns=names)

        if self.sim_pickle_path is not None:
            if os.path.isfile(self.sim_pickle_path):
                print "Found pickled similarity matrix at '" + self.sim_pickle_path +"', importing..."
                with open(self.sim_pickle_path, 'rb') as sim_pickle:
                    similarity_matrix.update(pickle.load(sim_pickle))
            else:
                print "Warning: was asked to look for similarity matrix at '" + self.sim_pickle_path +"'"
                print "Couldn't find one -- new pickle file will be created."

        for name1, fp1 in fingerprint_matrices.iteritems():
            for name2, fp2 in fingerprint_matrices.iteritems():
                #print "Comparing: " + name1 + " and " + name2
                if name1 == name2:
                    similarity_matrix.loc[name1, name2] = -1
                elif np.isnan(similarity_matrix.loc[name1, name2]):      
                    comparison_result = self.compare(fp1, fp2)
                    similarity_measure = self.similarity_measure(comparison_result)
                    similarity_matrix.loc[name1, name2] = similarity_measure
                    similarity_matrix.loc[name2, name1] = similarity_measure

        return similarity_matrix

    def dump_similarity_matrix(self):
        print "Updating pickled similarity matrix at " + self.sim_pickle_path
        with open(self.sim_pickle_path, 'wb') as sim_pickle:
            pickle.dump(self.similarity_matrix, sim_pickle)
        print "Updated."

    def clean_pickle(self, path, pathnames):
        for index in [index for index in self.similarity_matrix.index.values if index not in pathnames]:
            self.similarity_matrix = self.similarity_matrix.drop(index, axis=0)
            self.similarity_matrix = self.similarity_matrix.drop(index, axis=1)
        self.dump_similarity_matrix()


##################### Fingerprint Matrix Builder #####################
class FingerprintBuilder:
    '''
    Builds fingerprints into their pandas DataFrame representations. Goes through music21, then vis, then some further pandas
    '''
    
    # Path to files containing pieces in xml format
    pathnames = ""
    # Path to pickled matrices
    fp_pickle_path = None
    # Max allowed number of fingerprints
    number_of_fingerprints = 0
    # Interval settings, typically will not allow this to be changed.
    interval_settings = {'quality': True, 'simple or compound': 'simple', 'byTones':True}
    # Built fingerprint matrices
    fingerprint_matrices = None
    
    def __init__ (self, test_set_path, fp_pickle_path=None, number_of_fingerprints=10000):
        self.fp_pickle_path = fp_pickle_path
        self.pathnames = [ os.path.join(test_set_path, f) for f in os.listdir(test_set_path) if os.path.isfile(os.path.join(test_set_path, f)) and not f.startswith('.')]
        self.number_of_fingerprints = number_of_fingerprints
        self.fingerprint_matrices = self.build_fingerprint_matrices()
        self.dump_fingerprints()

    # Used below to push results to the front of their Series object
    def __shift_matrix(self, df):
        for i in range(0, len(df.columns)):
            df.iloc[i] = df.iloc[i].shift(-i)
        return df

    # Build dataframe of strong-beat intervals here:
    def __build_strong_intervals(self, piece, interval_settings, strong_beat_offsets, total_offsets):
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

    def __build_weak_intervals(self, piece, interval_settings, strong_beat_offsets, total_offsets):
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

    def build_fingerprint_matrices(self):
        # pathnames: List of paths to each piece for which a fingerprint matrix should be built
        # number_of_fingerprints: however many fingerprints you need
        interval_settings = self.interval_settings

        fingerprint_matrices = {}
        
        # Load pickled fingerprints
        if self.fp_pickle_path is not None:
            if os.path.isfile(self.fp_pickle_path):
                print "Found pickled fingerprints at '" + self.fp_pickle_path +"', importing..."
                with open(self.fp_pickle_path, 'rb') as fp_pickle:
                    fingerprint_matrices = pickle.load(fp_pickle)
            else:
                print "Warning: was asked to look for pickled fingerprints at '" + self.fp_pickle_path +"'"
                print "Couldn't find any -- new pickle file will be created."

        number_of_fingerprints = self.number_of_fingerprints

        for path in self.pathnames:
            # Skip pickled fingerprints
            if os.path.basename(path) in fingerprint_matrices.keys():
                continue
            # Setup for each piece
            #print("Indexing " + path)
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
            strong_intervals = self.__build_strong_intervals(piece, interval_settings, strong_beat_offsets, total_offsets)

            # LM: Build weak-interval frame
            weak_intervals = self.__build_weak_intervals(piece, interval_settings, strong_beat_offsets, total_offsets)

            # LM: Assemble results
            # 1. Prepare strong_intervals -- had to change this due to change in representation... take off final column (start of new bar)
            strong_intervals = strong_intervals.T.iloc[:-1].T
            strong_intervals = self.__shift_matrix(strong_intervals)
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
            fingerprint_matrices[os.path.basename(path)]=fingerprint_frame
                
            number_of_fingerprints -= 1
            if 0 == number_of_fingerprints:
                print "Max Number of Fingerprints Reached"
                break

        return fingerprint_matrices

    def dump_fingerprints(self):
        if self.fp_pickle_path is not None:
            print "Updating pickled fingerprints at " + self.fp_pickle_path
            with open(self.fp_pickle_path, 'wb') as fp_pickle:
                pickle.dump(self.fingerprint_matrices, fp_pickle)
            print "Updated."

    def clean_pickle(self, path, pathnames):
        for key in [key for key in self.fingerprint_matrices.keys() if key not in pathnames]:
            del(self.fingerprint_matrices[key])
        self.dump_fingerprints()

##################### Database Matrix Builder #####################
class FingerprintDatabase:
    '''
    Will, for now, build and store pickled dataframes to store previous results... possible future extensions could include using Django or sqlite
    '''
        
    # fingerprint builder
    builder = None
    # fingerprint comparer
    comparer = None
    # Path to test xml files
    test_set_path = None
    # Path to pickles
    fp_pickle_path = None
    sim_pickle_path = None

    def __init__(self, test_set_path, pickle_path=None):
        self.test_set_path = test_set_path
        self.fp_pickle_path = None if pickle_path is None else os.path.join(pickle_path, 'pickled_fingerprints.p') 
        self.sim_pickle_path = None if pickle_path is None else os.path.join(pickle_path, 'pickled_sim_matrix.p')
        self.build()

    def build(self):
        print "------------ Building Database... ------------"
        print "Building Fingerprint Matrices"
        self.builder = FingerprintBuilder(self.test_set_path, self.fp_pickle_path)
        print "-- Done. --"
        print "Building Similarity Matrix"
        self.comparer = FingerprintComparer(self.builder.fingerprint_matrices, self.sim_pickle_path)
        print "-- Done. --"
        print ""

    def fingerprints(self):
        return self.builder.fingerprint_matrices.keys()

    def fingerprint_matrices(self):
        for name, fp in self.builder.fingerprint_matrices.iteritems():
            print "------------ Fingerprint: " + name + " ------------"
            print fp
            print ""

    def fingerprint_matrix(self, name):
        return self.builder.fingerprint_matrices[name]

    def similarity_matrix(self):
        return self.comparer.similarity_matrix

    def rankings_for(self, name, number=-1):
        #self.similarity_matrix.sort(columns=name)
        return self.comparer.similarity_matrix.sort(columns=name, ascending=False)[name][:number]

    def compare(self, name1, name2):
        return self.comparer.compare(self.builder.fingerprint_matrices[name1], self.builder.fingerprint_matrices[name2], True)

    def clean_pickle(self):
        if raw_input("Warning: was asked to remove entries not in " + self.test_set_path + " from pickled similarity matrix. Continue [YES/NO]?") == "YES":
            new_fps = [f for f in os.listdir(self.test_set_path) if os.path.isfile(os.path.join(self.test_set_path, f)) and not f.startswith('.')]
            print "Removing " + str([key for key in self.fingerprints() if key not in new_fps])
            self.builder.clean_pickle(self.test_set_path, new_fps)
            self.comparer.clean_pickle(self.test_set_path, new_fps)


# Settings:
pandas.set_option('display.height', 1000)
pandas.set_option('display.max_rows', 500)
pandas.set_option('display.max_columns', 500)
pandas.set_option('display.width', 1000)

# Workflow for Risk project -- fingerprint horizontal interval indexer
# Will be used as the init later on
test_set_path = "../rep_index/"
pickle_path = "../"
db = FingerprintDatabase(test_set_path, pickle_path)

# LM: Run interpreter on command line
import readline 
import code
vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
shell.interact()

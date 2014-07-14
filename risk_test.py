from vis.analyzers.indexers import noterest, interval, metre, offset, subsection
from vis.analyzers.experimenters import frequency, aggregator
from vis.models.indexed_piece import IndexedPiece
from vis.models.aggregated_pieces import AggregatedPieces
from pandas import DataFrame, Series
import numpy as np
import music21
import os

# LM: Non-int range
def my_range(start, step, stop):
    i = start
    while i < stop:
        yield i
        i += step    


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


def compare_by_index(list1, list2):
    print "List 1: " + str(list1)
    print "List 2: " + str(list2)
    if not len(list1) == len(list2):
        print "List lengths not equal"
        return None
    matched_intervals = []
    for i, val in enumerate(list1):
        if list1[i] == list2[i]:
            matched_intervals.append(list1[i])
        else:
            matched_intervals.append(np.nan)
    return matched_intervals


def compare(fp1, fp2):
    print "Fingerprint 1: "
    print fp1
    print "Fingerprint 2: "
    print fp2

    # LM: Extract Column 1: Intervals (0.0, 1.0), (0.0, 2.0), ..., (0.0, end of piece)
    # Recursive call: will be i to j of i < n-1, j < n where n = max offsets
    fp1c1 = fp1.T.iloc[0]
    fp2c1 = fp2.T.iloc[0]

    matched_list = compare_by_index(fp1c1, fp2c1)

    #Consecutively misaligned indeces that need to be checked
    cmi = []
    for i in range(len(matched_list)-1):
        if np.isnan(matched_list[i]) and np.isnan(matched_list[i+1]):
            cmi.append(i)

    


def intervals_to_tones(results):
    interval_dict = {
    'P1': 0.0,
    'm2': 0.5,
    'M2': 1.0,
    'm3': 1.5,
    'M3': 2.0,
    'P4': 2.5,
    'a4': 3.0,
    'd5': 3.0,
    'P5': 3.5,
    'm6': 4.0,
    'M6': 4.5,
    'm7': 5.0,
    'M7': 5.5,
    '-m2': -0.5,
    '-M2': -1.0,
    '-m3': -1.5,
    '-M3': -2.0,
    '-P4': -2.5,
    '-a4': -3.0,
    '-d5': -3.0,
    '-P5': -3.5,
    '-m6': -4.0,
    '-M6': -4.5,
    '-m7': -5.0,
    '-M7': -5.5,
    }
    for key, df in results.items():
        for i, row in df.iterrows():
            for j, item in row.iteritems():
                if not isinstance(item, basestring) and np.isnan(item):
                    continue
                df.loc[i].loc[j] = interval_dict[item]



def prepare_results(results, number_of_columns=8):
    for name, result in results.iteritems():
        # Transpose, slice bottom row, transpose --- i.e. slice off last column
        result = result.T.iloc[:-1].T
        result = shift_matrix(result)
        results[name] = result


def shift_matrix(df):
    for i in range(0, len(df.columns)):
        df.iloc[i] = df.iloc[i].shift(-i)
    return df

# Workflow for Risk project -- fingerprint horizontal interval indexer
''' INFO
    print time_sigs['metre.TimeSignatureIndexer']['0'] # get 1st index: results of TimeSignatureIndexer, then 2nd index: part/voice 0
    print time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0] # get 1st time sig...   
    print time_sigs['metre.TimeSignatureIndexer']['0'].index[0] # get offset of 1st time sig... 
    print time_sigs['metre.TimeSignatureIndexer'].index.values # get the names of the index for each row for TimeSignatureIndexer
'''
test_set_path = "../risk_test_set/"
pathnames = [ os.path.join(test_set_path, f) for f in os.listdir(test_set_path) if os.path.isfile(os.path.join(test_set_path, f)) and not f.startswith('.')]
print("Test set: ",  pathnames)
ind_ps = []
interval_settings = {'quality': True, 'simple or compound': 'simple', 'quarterLength': 1.0, 'intervalDistance': 1.0, 'subsection': (0.0, 8.0)}
results = {}

number_of_fingerprints = 4
count = 0
for path in pathnames:
    # Setup for each piece
    print("Indexing " + path)
    piece = IndexedPiece(path)
    piece_stream = music21.converter.parseFile(path)
    ind_ps.append(piece)

    # LM: Get time signature and determine strong beats
    time_sigs = piece.get_data([metre.TimeSignatureIndexer])
    # Assuming no time signature change in whole piece, assign offsets to strong beats
    if time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0] == '6/8' or time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0] == '9/8':
        interval_settings['quarterLength'] = 1.5
        measures = 4
    else:
        interval_settings['quarterLength'] = 1.0
        measures = 2

    # LM: Get total number of measures
    numer, denom = time_sigs['metre.TimeSignatureIndexer']['0'].iloc[0].split('/')
    # Two bars worth of offsets, ignoring anacrusis
    total_offsets = int(numer) * measures*4.0/int(denom)
    interval_settings['subsection'] = (0.0, total_offsets)

    fingerprint_frame =[] 
    # LM: Workflow - get notes & rests, take the fingerprint subsection, filter for strong beats, get horizontal intervals
    # Do this for horizontal intervals over 1.0 offset increments, 2.0 offset increments....
    # For i = 1.0 to the total allowable distance between two notes, which is the total number of offsets
    for i in my_range(1.0, 1.0, total_offsets):
        interval_settings['intervalDistance'] = i
        strong_intervals = piece.get_data([noterest.NoteRestIndexer, subsection.SubsectionIndexer, offset.FilterByOffsetIndexer, interval.VariableHorizontalIntervalIndexer], interval_settings)
        strong_intervals = strong_intervals['interval.VariableHorizontalIntervalIndexer']['0']
        fingerprint_frame.append(strong_intervals)

    fingerprint_frame = DataFrame(fingerprint_frame)
    fingerprint_frame.index = my_range(1.0, 1.0, total_offsets)

    print os.path.basename(path)
    print type(fingerprint_frame)
    print fingerprint_frame
    
    #piece_stream.show('musicxml', 'MuseScore')
    #raw_input("Press Enter to continue: ")
    results[os.path.basename(path)]=fingerprint_frame
    
    count += 1
    if count == number_of_fingerprints:
        break

print("Useful: " + u"a1r1 = results['Allard_1928_MoneyMusk_A.xml'].iloc[0].tolist()")
print("Useful: " + u"a2r1 = results['Boivin_YEAR_MoneyMusk_A.xml'].iloc[0].tolist()")


# LM: Run interpreter on command line
import readline 
import code
vars = globals().copy()
vars.update(locals())
shell = code.InteractiveConsole(vars)
shell.interact()


# aggregate results of all pieces
#agg_p = AggregatedPieces(ind_ps)
#result = agg_p.get_data([aggregator.ColumnAggregator], [], {}, ngram_freqs)
#result = DataFrame({'Frequencies': result})

'''
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



def build_stack(df):
    interval_stack = df['interval.VariableHorizontalIntervalIndexer']['0']
    #print interval_stack
    #print type(interval_stack)
    return interval_stack.tolist()
'''

import os
import pandas
from vis.workflow import WorkflowManager
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import noterest, interval, ngram, dissonancelocator, metre
from vis.analyzers.experimenters import frequency
from vis import workflow
from numpy import nan, isnan
import numpy
import six
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
import time
import pdb
from music21 import converter

import array

# get the path to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

def main():
    t0 = time.time()
    piece_path = "/Users/amor/Documents/Code/VIS/vis/tests/corpus/Kyrie.krn"
    # piece_path = '/Users/amor/Downloads/a3_Josquin_DeTousBiens_StrettoCanonTB.xml'
    # piece_path = "/Users/amor/Documents/Code/VIS/vis/tests/corpus/bwv77.mxl"
    ind_piece = IndexedPiece(piece_path)

    # # pdb.set_trace()
    setts = {'quality': True, 'simple or compound': 'simple'}
    horiz_setts = {'quality': False, 'simple or compound': 'compound'}

    # nr1 = time.clock()
    # note_rest = ind_piece.get_data([noterest.NoteRestIndexer], setts)
    # nr2 = time.clock()
    # print 'Time to run NoteRestIndexer: ' + str(nr2-nr1)


    # newnr1 = time.clock()
    # test_piece = converter.parse(piece_path)
    # parts = []
    # part_numbers = range(len(test_piece.parts))
    # for x in part_numbers:
    #     temp = list(test_piece.parts[x].flat.stripTies().notesAndRests)
    #     nr = []
    #     part_index = []
    #     for event in temp:
    #         part_index.append(event.offset)
    #         if event.name != 'rest':
    #             nr.append(event.nameWithOctave)
    #         else:
    #             nr.append('Rest')
    #     parts.append(pandas.Series(nr, index=part_index))
    #     newnr2 = time.clock()
    # new_nr = pandas.concat([s for s in parts], axis=1)
    # part_strings = []
    # for num in part_numbers:
    #     part_strings.append(unicode(num))
    # iterables = [['noterest.NoteRestIndexer'], part_strings]
    # new_nr_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # new_nr.columns = new_nr_multi_index
    # print 'New NoteRest Indexer Runtime: ' + str(newnr2 - newnr1)

    # # pdb.set_trace()


    # # New Duration Indexer
    # newdur1 = time.clock()
    # test_piece = converter.parse(piece_path)
    # part_durs = []
    # part_numbers = range(len(test_piece.parts))
    # for x in part_numbers:
    #     temp = list(test_piece.parts[x].flat.stripTies().notesAndRests)
    #     dur = []
    #     part_dur_index = []
    #     for event in temp:
    #         dur.append(event.quarterLength)
    #         part_dur_index.append(event.offset)
            
    #     part_durs.append(pandas.Series(dur, index=part_dur_index))
    #     newdur2 = time.clock()
    # new_dur = pandas.concat([s for s in part_durs], axis=1)
    # part_strings = []
    # for num in part_numbers:
    #     part_strings.append(unicode(num))
    # iterables = [['metre.DurationIndexer'], part_strings]
    # new_dur_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # new_dur.columns = new_dur_multi_index
    # print 'New Duration Indexer Runtime: ' + str(newdur2 - newdur1)


    double1 = time.clock()
    test_piece = converter.parse(piece_path)
    parts_nr = []
    parts_dur = []
    part_numbers = range(len(test_piece.parts))

    for x in part_numbers:
        temp = list(test_piece.parts[x].flat.stripTies().notesAndRests)
        nr = []
        dur = []
        part_index = []
        for event in temp:
            part_index.append(event.offset)
            event_dur = event.quarterLength
            dur.append(event_dur)
            if event.name != 'rest':
                nr.append(event.nameWithOctave)
            else:
                nr.append('Rest')

        parts_nr.append(pandas.Series(nr, index=part_index))
        parts_dur.append(pandas.Series(dur, index=part_index))
    double_nr = pandas.concat([s for s in parts_nr], axis=1)
    double_dur = pandas.concat([s for s in parts_dur], axis=1)
    part_strings = []
    for num in part_numbers:
        part_strings.append(unicode(num))
    iterables = [['noterest.NoteRestIndexer'], part_strings]
    double_nr_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    double_nr.columns = double_nr_multi_index

    iterables = [['metre.DurationIndexer'], part_strings]
    double_dur_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    double_dur.columns = double_dur_multi_index


    double2 = time.clock()
    print 'Double-Indexer Runtime: ' + str(double2 - double1)


    # New BeatStrength Indexer
    newbs1 = time.clock()
    test_piece = converter.parse(piece_path)
    part_bs = []
    part_numbers = range(len(test_piece.parts))
    for x in part_numbers:
        temp = list(test_piece.parts[x].flat.notesAndRests)
        bs = []
        part_bs_index = []
        for indx, event in enumerate(temp):
            bs.append(event.beatStrength)
            part_bs_index.append(event.offset)
        part_bs.append(pandas.Series(bs, index=part_bs_index))
    new_bs = pandas.concat([s for s in part_bs], axis=1)
    part_strings = []
    for num in part_numbers:
        part_strings.append(unicode(num))
    iterables = [['metre.NoteBeatStrengthIndexer'], part_strings]
    new_bs.columns = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    newbs2 = time.clock()
    print 'New BeatStrength Indexer Runtime: ' + str(newbs2 - newbs1)




    horiz = interval.HorizontalIntervalIndexer(double_nr, horiz_setts).run()

    vert_ints = interval.IntervalIndexer(double_nr, setts).run()
    dissonances = dissonancelocator.DissonanceIndexer(pandas.concat([horiz, double_dur, new_bs, vert_ints], axis=1)).run()
    # print dissonances



    # dissonances = ind_piece.get_data([noterest.NoteRestIndexer,
    #                                 interval.IntervalIndexer,
    #                                 dissonancelocator.DissonanceIndexer],
    #                                 setts)
    # print dissonances

    
    # dur1 = time.clock()
    # durations = ind_piece.get_data([metre.DurationIndexer], setts)
    # dur2 = time.clock()
    # print 'Time to run DurationIndexer: ' + str(dur2-dur1)
        
    # bs1 = time.clock()
    # beat_strengths = ind_piece.get_data([metre.NoteBeatStrengthIndexer], setts)
    # bs2 = time.clock()
    # print 'Time to run BeatStrengthIndexer: ' + str(bs2-bs1)


    # # This group_strengths code works but is not needed for dissonance detection.
    # group_strengths = pandas.DataFrame(index=beat_strengths.index, columns=dissonances['dissonance.DissonanceLocator'].columns, dtype=float)
    # beat_strengths.replace(nan, 0)
    # for y in group_strengths.columns:
    #     voices_in_group = y.split(',')
    #     group_data = []
    #     for z in group_strengths.index:
    #         strengths = [0] # Dummy zero is a hack to get around issues using max or nanmax with nans.
    #         for v in voices_in_group:
    #             if beat_strengths['metre.NoteBeatStrengthIndexer'][v].loc[z] is not nan:
    #                 strengths.append(beat_strengths['metre.NoteBeatStrengthIndexer'][v].loc[z])
    #         group_data.append(max(strengths))
    #     group_strengths[y] = group_data
    # iterables = [['metre.GroupBeatStrengthIndexer'], group_strengths.columns]
    # group_strengths.columns = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # # print group_strengths

    # combined_df = pandas.concat([dissonances, horiz, double_dur, new_bs], axis=1)
    # print combined_df

    t1 = time.time()
    print 'Time taken to run all indexers: '
    print t1 - t0

    # diss_types = dissonancelocator.DissonanceClassifier(combined_df).run()
    # print diss_types




    # group_durations = pandas.DataFrame()    # Debug, the logic shouldn't be the same as for group_strengths
    # groups = list(dissonances.columns)
    # for i, x in enumerate(groups):
    #     groups[i] = x[1]
    # for y in groups:
    #     voices_in_group = y.split(',')
    #     group_data = []
    #     for z in durations.index:
    #         duras = []
    #         for v in voices_in_group:
    #             duras.append(durations.loc[z][int(v)])     # Turning v into an int is extremely hacky.
    #         group_data.append(nanmax(duras))
    #     group_durations[y] = group_data
    # print group_durations

    t2 = time.time()

    workm = WorkflowManager([piece_path])
    workm.settings(None, 'voice combinations', '[[0, 1]]')
    workm.settings(None, 'count frequency', False)

    iterables = [[''], double_nr['noterest.NoteRestIndexer'].columns]
    d_types_multi_index_for_LilyPond = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    dissonances.columns = d_types_multi_index_for_LilyPond

    workm._result = [dissonances]
    workm.output('LilyPond', '/Users/amor/Documents/Code/VIS/test_output/combined_dissonances')

    t3 = time.time()
    print 'Time to produce score output: '
    print t3 - t2

if __name__ == "__main__":
    main()

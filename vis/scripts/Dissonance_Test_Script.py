
import os
import pandas
from vis.workflow import WorkflowManager
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import interval, dissonance, meter, noterest, offset
from vis.analyzers.experimenters import frequency
from vis import workflow
from numpy import nan, isnan
import numpy
import six
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
import time
import pdb
from music21 import converter, stream, expressions, note
import array

# get the path to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]

def main():
    # piece_path = "/home/amor/Code/vis-framework/vis/tests/corpus/Kyrie.krn"
    piece_path = "/home/amor/Code/vis-framework/vis/tests/corpus/bach.xml"
    # piece_path = "/home/amor/Code/vis-framework/vis/tests/corpus/bwv603.xml"
    # piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Reimenschnieder/1-026900B_.xml'
    #piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos2308.mei'
    # piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Sanctus.krn'
    ind_piece = IndexedPiece(piece_path)
    test_piece = ind_piece._import_score()
    test_parts = test_piece.parts

    # bwv603 = converter.parse(os.path.join(VIS_PATH, 'tests', 'corpus/bwv603.xml'))
    # test_part = [bwv603.parts[0], bwv603.parts[1], bwv603.parts[2], bwv603.parts[3]]

    setts = {'quality': True, 'simple or compound': 'simple'}
    horiz_setts = {'quality': False, 'simple or compound': 'compound'}

    t0 = time.time()
    actual = ind_piece.get_data([noterest.NoteRestIndexer])  
    
    # filter_setts = {'quarterLength': 2.0, 'method':None}
    # filtered_results = offset.FilterByOffsetIndexer(actual, filter_setts).run()
    # pdb.set_trace()
    dur_ind = meter.DurationIndexer(test_parts).run()
    bs_ind = meter.NoteBeatStrengthIndexer(test_parts).run()
    horiz = interval.HorizontalIntervalIndexer(actual, horiz_setts).run()
    vert_ints = interval.IntervalIndexer(actual, setts).run()

    # actual2 = actual.T
    # # actual = ind_piece.get_data([noterest.NoteRestIndexer]) #dur_indexer.run()['meter.DurationIndexer']
    # # actual = ind_piece.get_data([meter.NoteBeatStrengthIndexer]) #dur_indexer.run()['meter.DurationIndexer']
    # t1 = time.time()
    # print 'Noterest Indexer Runtime: ' + str(t1-t0)
    # pdb.set_trace()




    # basic1 = time.time()
    # parts_fm = []
    # parts_nr = []
    # # parts_dur = []
    # parts_bs = []
    # parts_ms = []
    # test_piece = converter.parse(piece_path)
    # part_numbers = range(len(test_piece.parts))
    # from vis.analyzers.indexers.noterest import indexer_func as nr_ind_func
    # from vis.analyzers.indexers.meter import duration_ind_func as dur_ind_func
    # from vis.analyzers.indexers.meter import beatstrength_ind_func as bs_ind_func
    # from vis.analyzers.indexers.fermata import indexer_func as fm_ind_func
    # for x in part_numbers:
    #     temp_part = test_piece.parts[x]
    #     fm = []
    #     fermata_index = []
    #     nr = []
    #     # dur = []
    #     bs = []
    #     part_index = []
    #     ms = []
    #     measure_index = []
    #     for event in temp_part.recurse():
    #         # pdb.set_trace()
    #         if 'GeneralNote' in event.classes:
    #             found_fm = False
    #             for expression in event.expressions:
    #                 if isinstance(expression, expressions.Fermata):
    #                     fm.append('Fermata')
    #                     found_fm = True
    #                     break
    #             if not found_fm:
    #                 fm.append(nan)
    #             # fm.append(fm_ind_func((event,)))
    #             for y in event.contextSites():
    #                 if y[0] is temp_part:
    #                     fermata_index.append(y[1])
    #             if hasattr(event, 'tie') and event.tie is not None and event.tie.type in ('stop', 'continue'):
    #                 # dur[-1] += event.quarterLength
    #                 continue
    #             nr.append(nr_ind_func((event,)))
    #             part_index.append(fermata_index[-1])
    #             # dur.append(dur_ind_func((event,)))
    #             bs.append(event.beatStrength)
    #             bs.append(bs_ind_func((event,)))
    #         elif 'Measure' in event.classes:
    #             ms.append(event.measureNumber)
    #             measure_index.append(event.offset)   

    #     parts_nr.append(pandas.Series(nr, index=part_index))
    #     # parts_dur.append(pandas.Series(dur, index=part_index))
    #     parts_bs.append(pandas.Series(bs, index=part_index))
    #     parts_ms.append(pandas.Series(ms, index=measure_index))
    #     parts_fm.append(pandas.Series(fm, index=fermata_index))

    # basic_nr = pandas.concat([s for s in parts_nr], axis=1)
    # # basic_dur = pandas.concat([s for s in parts_dur], axis=1)
    # basic_bs = pandas.concat([s for s in parts_bs], axis=1)
    # basic_ms = pandas.concat([s for s in parts_ms], axis=1)
    # basic_fm = pandas.concat([s for s in parts_fm], axis=1)
    
    # part_strings = []
    # for num in part_numbers:
    #     part_strings.append(str(num))
    
    # iterables = [['basic.NoteRestIndexer'], part_strings]
    # basic_nr_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # basic_nr.columns = basic_nr_multi_index

    # # iterables = [['basic.DurationIndexer'], part_strings]
    # # basic_dur_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # # basic_dur.columns = basic_dur_multi_index

    # iterables = [['basic.NoteBeatStrengthIndexer'], part_strings]
    # basic_bs_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # basic_bs.columns = basic_bs_multi_index

    # iterables = [['basic.MeasureIndexer'], part_strings]
    # basic_ms_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # basic_ms.columns = basic_ms_multi_index

    # iterables = [['fermata.FermataIndexer'], part_strings]
    # basic_fm_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # basic_fm.columns = basic_fm_multi_index


    # basic2 = time.time()
    # print 'Basic-Indexer Runtime: ' + str(basic2 - basic1)


    # horiz = interval.HorizontalIntervalIndexer(basic_nr, horiz_setts).run()
    # vert_ints = interval.IntervalIndexer(basic_nr, setts).run()
    dissonances = dissonance.DissonanceIndexer([bs_ind, dur_ind, horiz, vert_ints]).run()



    t1 = time.time()
    print 'Time taken to run all indexers: '
    print t1 - t0

    pdb.set_trace()


    # t2 = time.time()

    # workm = WorkflowManager([piece_path])
    # workm.settings(None, 'voice combinations', '[[0, 1]]')
    # workm.settings(None, 'count frequency', False)

    # iterables = [[''], basic_nr['basic.NoteRestIndexer'].columns]
    # d_types_multi_index_for_LilyPond = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # dissonances.columns = d_types_multi_index_for_LilyPond

    # workm._result = [dissonances]
    # workm.output('LilyPond', '/Users/amor/Documents/Code/VIS/test_output/combined_dissonances')

    # t3 = time.time()
    # print 'Time to produce score output: '
    # print t3 - t2

if __name__ == "__main__":
    main()


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
    #     part_strings.append(str(num))
    # iterables = [['noterest.NoteRestIndexer'], part_strings]
    # new_nr_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # new_nr.columns = new_nr_multi_index
    # print 'New NoteRest Indexer Runtime: ' + str(newnr2 - newnr1)



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
    #     part_strings.append(str(num))
    # iterables = [['meter.DurationIndexer'], part_strings]
    # new_dur_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # new_dur.columns = new_dur_multi_index
    # print 'New Duration Indexer Runtime: ' + str(newdur2 - newdur1)

    # # double1 = time.clock()
    # # parts_nr = []
    # # parts_dur = []
    # # test_piece = converter.parse(piece_path)
    # # part_numbers = range(len(test_piece.parts))
    # # for x in part_numbers:
    # #     temp = test_piece.parts[x].flat.stripTies().notesAndRests
    # #     nr = []
    # #     dur = []
    # #     part_index = []
    # #     for event in temp:
    # #         part_index.append(event.offset)
    # #         event_dur = event.quarterLength
    # #         dur.append(event_dur)
    # #         if event.name != r:
    # #             nr.append(event.nameWithOctave)
    # #         else:
    # #             nr.append(R)

    # #     parts_nr.append(pandas.Series(nr, index=part_index))
    # #     parts_dur.append(pandas.Series(dur, index=part_index))
    # # double_nr = pandas.concat([s for s in parts_nr], axis=1)
    # # double_dur = pandas.concat([s for s in parts_dur], axis=1)
    # # part_strings = []
    # # for num in part_numbers:
    # #     part_strings.append(str(num))
    # # iterables = [['noterest.NoteRestIndexer'], part_strings]
    # # double_nr_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # # double_nr.columns = double_nr_multi_index

    # double1 = time.clock()
    # parts_nr = []
    # parts_dur = []
    # test_piece = converter.parse(piece_path)
    # part_numbers = range(len(test_piece.parts))
    # for x in part_numbers:
    #     temp = test_piece.parts[x]
    #     nr = []
    #     dur = []
    #     part_index = []
    #     for event in temp.recurse():
    #         if gn not in event.classes:
    #             continue
    #         if hasattr(event, 'tie') and event.tie is not None and event.tie.type in ('stop', 'continue'):
    #             dur[-1] += event.quarterLength
    #             continue
    #         for y in event.contextSites():
    #             if y[0] is temp:
    #                 part_index.append(y[1])
    #         dur.append(event.quarterLength)
    #         if event.name != r:
    #             nr.append(event.nameWithOctave)
    #         else:
    #             nr.append(R)
    #     parts_nr.append(pandas.Series(nr, index=part_index))
    #     parts_dur.append(pandas.Series(dur, index=part_index))

    # double2 = time.clock()
    # print 'Double-Indexer Runtime: ' + str(double2 - double1)

    # double_nr = pandas.concat([s for s in parts_nr], axis=1)
    # double_dur = pandas.concat([s for s in parts_dur], axis=1)
    # part_strings = []
    # for num in part_numbers:
    #     part_strings.append(str(num))
    # iterables = [['noterest.NoteRestIndexer'], part_strings]
    # double_nr_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # double_nr.columns = double_nr_multi_index

    # iterables = [['meter.DurationIndexer'], part_strings]
    # double_dur_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # double_dur.columns = double_dur_multi_index



    # # New BeatStrength Indexer
    # newbs1 = time.clock()
    # test_piece = converter.parse(piece_path) # Why does this run faster when this line is reexecuted?
    # part_bs = []
    # part_numbers = range(len(test_piece.parts))
    # for x in part_numbers:
    #     bs = []
    #     part_bs_index = []
    #     part = test_piece.parts[x]
    #     for event in part.recurse():
    #         if gn not in event.classes:
    #             continue
    #         if hasattr(event, 'tie') and event.tie is not None and event.tie.type in ('stop', 'continue'):
    #             continue
    #         bs.append(event.beatStrength)
    #         for y in event.contextSites():
    #             if y[0] is part:
    #                 part_bs_index.append(y[1])
    #     part_bs.append(pandas.Series(bs, index=part_bs_index))
    # new_bs = pandas.concat([s for s in part_bs], axis=1)
    # part_strings = []
    # for num in part_numbers:
    #     part_strings.append(str(num))
    # iterables = [['meter.NoteBeatStrengthIndexer'], part_strings]
    # new_bs.columns = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # newbs2 = time.clock()
    # print 'New BeatStrength Indexer Runtime: ' + str(newbs2 - newbs1)



    # # This group_strengths code works but is not needed for dissonance detection.
    # group_strengths = pandas.DataFrame(index=beat_strengths.index, columns=dissonances['dissonance.DissonanceLocator'].columns, dtype=float)
    # beat_strengths.replace(nan, 0)
    # for y in group_strengths.columns:
    #     voices_in_group = y.split(',')
    #     group_data = []
    #     for z in group_strengths.index:
    #         strengths = [0] # Dummy zero is a hack to get around issues using max or nanmax with nans.
    #         for v in voices_in_group:
    #             if beat_strengths['meter.NoteBeatStrengthIndexer'][v].loc[z] is not nan:
    #                 strengths.append(beat_strengths['meter.NoteBeatStrengthIndexer'][v].loc[z])
    #         group_data.append(max(strengths))
    #     group_strengths[y] = group_data
    # iterables = [['meter.GroupBeatStrengthIndexer'], group_strengths.columns]
    # group_strengths.columns = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # # print group_strengths



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



    # mi4 = time.clock()
    # vis_m_ind = meter.MeasureIndexer(test_piece.parts[0]).run()
    # mi5 = time.clock()
    # print "Time taken to run old measure indexer: " + str(mi5-mi4)
    # pdb.set_trace()




    # fa1 = time.clock()
    # fermatas = ind_piece.get_data([fermata.FermataIndexer])
    # fa2 = time.clock()
    # print "Fermata runtime: " + str(fa2-fa1)


    # fa3 = time.clock() # This version of the fermata indexer runs about 5 times as fast.
    # test_piece = converter.parse(piece_path)
    # part_numbers = range(len(test_piece.parts))
    # parts_fm = []
    # for x in part_numbers:
    #     fm = []
    #     fermatas_index = []
    #     temp = test_piece.parts[x]
    #     for event in temp.recurse():
    #         if 'GeneralNote' in event.classes:
    #             found_fm = False
    #             for expression in event.expressions:
    #                 if isinstance(expression, expressions.Fermata):
    #                     fm.append('Fermata')
    #                     found_fm = True
    #                     break
    #             if not found_fm:
    #                 fm.append(nan)
    #             for y in event.contextSites():
    #                 if y[0] is temp:
    #                     fermatas_index.append(y[1])
    #     parts_fm.append(pandas.Series(fm, index=fermatas_index))
    # basic_fm = pandas.concat([s for s in parts_fm], axis=1)
    # part_strings = []
    # for num in part_numbers:
    #     part_strings.append(str(num))
    # iterables = [['fermata.FermataIndexer'], part_strings]
    # basic_fm_multi_index = pandas.MultiIndex.from_product(iterables, names = ['Indexer', 'Parts'])
    # basic_fm.columns = basic_fm_multi_index

    # fa4 = time.clock()
    # print "New Fermata indexer runtime: " + str(fa4 - fa3)


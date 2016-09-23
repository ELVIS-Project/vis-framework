
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
    piece_path = "/home/amor/Code/vis-framework/vis/tests/corpus/Kyrie.krn"
    # piece_path = "/home/amor/Code/vis-framework/vis/tests/corpus/bach.xml"
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
    actual = noterest.NoteRestIndexer(test_parts).run()
    
    # filter_setts = {'quarterLength': 2.0, 'method':None}
    # filtered_results = offset.FilterByOffsetIndexer(actual, filter_setts).run()
    # pdb.set_trace()
    dur_ind = meter.DurationIndexer(test_parts).run()
    bs_ind = meter.NoteBeatStrengthIndexer(test_parts).run()
    horiz = interval.HorizontalIntervalIndexer(actual, horiz_setts).run()
    # ind_piece._analyses['noterest'] = actual
    # h_df = ind_piece._get_h_ints(settings=horiz_setts)
    vert_ints = interval.IntervalIndexer(actual, setts).run()
    dissonances = dissonance.DissonanceIndexer([bs_ind, dur_ind, horiz, vert_ints]).run()



    t1 = time.time()
    print('Time taken to run all indexers: ')
    print(t1 - t0)

    pdb.set_trace()

if __name__ == "__main__":
    main()


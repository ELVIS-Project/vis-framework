### Script meant to count the occurences of different types of notes in old notation
### by using Karen Desmond's annotated scores to figure out what the original notes
### values were.


"""
NOTES:

a plus symbol is found in event.articulations and is called a 'stop'
a triangular fermata, found in event.expressions, does not seem to be distinguished from regular ones

"""

import os
import pandas as pd
from vis.workflow import WorkflowManager
from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import interval, dissonance, meter, noterest, ngram
from vis.analyzers.experimenters import frequency
from vis import workflow
from numpy import nan, isnan
import numpy
import six
import time
import pdb
from music21 import converter, stream, expressions, note
import array
from vis.analyzers.indexers.noterest import indexer_func as nr_ind_func
import multiprocessing as mp

# get the path to the 'vis' directory
import vis
VIS_PATH = vis.__path__[0]


t1 = time.time()
sers = []
pathnames = [
             # '/home/amor/Code/vis-framework/vis/scripts/Karens_Pieces/garison.mei',
             # '/home/amor/Code/vis-framework/vis/scripts/Karens_Pieces/qui_secuntur.xml'
             '/home/amor/Code/vis-framework/vis/scripts/Karens_Pieces/qui_secuntur.mei'
             ]

parts_nr = []
parts_dur = []
test_piece = converter.parse(pathnames[0])
part_numbers = range(len(test_piece.parts))

for voice in part_numbers:
    temp_part = test_piece.parts[voice]
    med_nr = []
    part_index = []
    post = None
    for event in temp_part.recurse():
        # if voice.set_trace()
        if 'Note' in event.classes or 'Rest' in event.classes:
            if hasattr(event, 'tie') and event.tie is not None and event.tie.type in ('stop', 'continue'):
                dur[-1] += event.quarterLength
                continue

            if event.fullName.endswith('Imperfect Longa Note'):
                stopped = False
                arts = [w.__str__() for w in event.articulations]
                for art in arts:
                    if 'Stopped' in art:
                        stopped = True
                if stopped:
                    post = 'Brevis Altera Note'
                else:
                    post = 'Imperfect Longa Note'
            elif event.quarterLength == 4.0:
                post = 'Semibrevis Note'
                # if 'staccato' in [x.name for x in event.articulations]:
                #     post = 'Major Semibrevis Note'
                # else:
                #     post = 'Minor Semibrevis Note'

            elif event.quarterLength.__str__() == '8/3':
                post = 'Semibrevis Note'

            elif 'Whole Tuplet' in event.fullName and event.quarterLength == 2.0:
                post = 'Semibrevis Note'

            elif event.fullName.endswith('Perfect Longa Note'):
                post = 'Perfect Longa Note'

            elif event.fullName.endswith('Breve Note'):
                post = 'Brevis Recta Note'

            else:
                post = nr_ind_func((event,))

            med_nr.append(post)
            for y in event.contextSites():
                if y[0] is temp_part:
                    part_index.append(y[1])
                    # if voice == 0 and 'Note' in event.classes and y[1] > 900:# and event.nameWithOctave == 'A4':
                    #     pdb.set_trace()

    parts_nr.append(pd.Series(med_nr, index=part_index))

med_nr = pd.concat([s for s in parts_nr], axis=1)

part_strings = [unicode(num) for num in part_numbers]

iterables = (('noterest.MedievalNoteRestIndexer',), part_strings)
med_nr_multi_index = pd.MultiIndex.from_product(iterables, names = ('Indexer', 'Parts'))
med_nr.columns = med_nr_multi_index



# new_indx = [int(val) for val in med_nr.index]
# df = med_nr
# df.index = new_indx



v_setts = {'quality': True, 'simple or compound': 'simple', 'direction': False}
h_setts = {'quality': False, 'horiz_attach_later': False, 'simple or compound': 'simple', 'direction': False}
n_setts = {'n': 3, 'horizontal': [('interval.HorizontalIntervalIndexer', '1'), ('interval.HorizontalIntervalIndexer', '2'), ('interval.HorizontalIntervalIndexer', '2')], 
    'vertical': [('interval.IntervalIndexer', '0,1'), ('interval.IntervalIndexer', '0,2'), ('interval.IntervalIndexer', '1,2')], 'mark_singles': False}


test_parts = test_piece.parts
# stream indexers
nr = noterest.NoteRestIndexer(test_parts).run()
dur = meter.DurationIndexer(test_parts).run()
beat_sth = meter.NoteBeatStrengthIndexer(test_parts).run()
measures = meter.MeasureIndexer(test_parts).run()

# series indexers
horiz = interval.HorizontalIntervalIndexer(nr, h_setts).run()
h_setts = {'quality': False, 'horiz_attach_later': False, 'simple or compound': 'simple', 'direction': False}
horiz_later = interval.HorizontalIntervalIndexer(nr, h_setts).run()
vert = interval.IntervalIndexer(nr, v_setts).run()
# comb_df = pd.concat([horiz_later, vert], axis=1)
# ngrams = ngram.NGramIndexer(comb_df, n_setts).run()

# interval n-grams
test_wm = WorkflowManager([os.path.join(VIS_PATH, 'scripts', 'Karens_Pieces/qui_secuntur.xml')])
test_wm.load('pieces')
test_wm.settings(0, 'voice combinations', 'all pairs')
test_wm.settings(0, 'n', 3)
test_wm.settings(None, 'count frequency', False)
test_wm.settings(0, 'continuer', '_')
ngrams = test_wm.run('interval n-grams')[0]

# durational n-grams
dur_ngram_list = []
dur_strings = dur.applymap(str)
for x in range(3):
    n_setts = {'n': 3, 'vertical': [('meter.DurationIndexer', str(x))], 'mark_singles': False}
    dur_ngram_list.append(ngram.NGramIndexer(pd.concat([dur_strings.iloc[:,x]], axis=1), n_setts).run())
dur_ngrams = pd.concat(dur_ngram_list, axis=1)

# counts
# freqs = pd.concat([frequency.FrequencyExperimenter(in_df).run()[0] for in_df in (nr, dur, beat_sth, horiz, vert, ngrams, dur_ngrams)], axis=1)
dfs = pd.concat((med_nr, nr, dur, beat_sth, measures, horiz, vert, ngrams, dur_ngrams), axis=1)

# dfs.to_csv('/home/amor/Code/vis-framework/vis/scripts/Karens_Pieces/indexer_data.csv')
# freqs.to_csv('/home/amor/Code/vis-framework/vis/scripts/Karens_Pieces/frequency_data.csv')

t2 = time.time()
print 'VIS Analysis took %f seconds.' % round((t2-t1), 2)
counts = med_nr.stack().stack().value_counts()
pdb.set_trace()

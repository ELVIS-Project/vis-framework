from vis.analyzers.indexers import noterest, interval, new_ngram, meter, active_voices
from vis.models.indexed_piece import IndexedPiece 
from vis.models.aggregated_pieces import AggregatedPieces
import pandas
import pdb
import time

import vis
VIS_PATH = vis.__path__[0]

# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos2308.mei'
# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/bwv2.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Kyrie.krn'
piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos0303a-Missa_De_beata_virgine-Kyrie.mei'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Lassus_Duets/Lassus_1_Beatus_Vir.xml'
ind_piece = IndexedPiece(piece_path)
# parts = ind_piece._import_score().parts

av_setts = {'show_all': True}
v_setts = {'quality': True, 'simple or compound': 'simple', 'directed': True, 'mp': False}
h_setts = {'quality': False, 'horiz_attach_later': False, 'simple or compound': 'simple', 'directed': True, 'mp': False}
n_setts = {'n': 5, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': [('0,4',)],
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_2 = {'n': 5, 'continuer': 'P1', 'vertical': 'all',
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_3 = {'n': 2, 'continuer': 'P1', 'vertical': [('0,4',)],
           'terminator': [], 'open-ended': False, 'brackets': False}

# pieces = (IndexedPiece(piece_path2), ind_piece)
# corpus = AggregatedPieces(pieces)
pdb.set_trace()

nr = noterest.NoteRestIndexer(parts).run()
dr = meter.DurationIndexer(parts).run()
ms = meter.MeasureIndexer(parts).run()
bs = meter.NoteBeatStrengthIndexer(parts).run()
t0 = time.time()
hz = interval.HorizontalIntervalIndexer(nr, h_setts).run()
hz.columns.set_levels(('Horiz_nsd',), level=0, inplace=True)
av = active_voices.ActiveVoicesIndexer(nr, av_setts).run()
av = pandas.concat([av]*5, axis=1, ignore_index=True)
av.columns=[('av', '0'), ('av', '1'), ('av', '2'), ('av', '3'), ('av', '4')]
t1 = time.time()
print(str(t1-t0))
vt = interval.IntervalIndexer(nr, v_setts).run()

ng = new_ngram.NewNGramIndexer((vt, hz), n_setts).run()
ng_2 = new_ngram.NewNGramIndexer((hz,), n_setts_2).run()
# ng_3 = new_ngram.NewNGramIndexer((dr,), n_setts_3).run()
h_setts = {'quality': True, 'horiz_attach_later': False, 'simple or compound': 'simple', 'directed': True, 'mp': False}
hz2 = interval.HorizontalIntervalIndexer(nr, h_setts).run()
hz2.columns.set_levels(('Horiz_qsd',), level=0, inplace=True)
t2= time.time()
big_df = pandas.concat((nr,dr,ms,bs,hz,hz2,av, ng_2), axis=1)
t3 = time.time()
print(str(t3-t2))

cond = big_df.loc[:, 'av'] < 3
pdb.set_trace()
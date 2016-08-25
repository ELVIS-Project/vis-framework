from vis.analyzers.indexers import noterest, interval, new_ngram, meter, dissonance, active_voices
from vis.models.indexed_piece import IndexedPiece 
from vis.models.aggregated_pieces import AggregatedPieces
import pandas
import pdb
import time

import vis
VIS_PATH = vis.__path__[0]

# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos2308.mei'
# piece_path2 = '/home/amor/Code/vis-framework/vis/tests/corpus/bwv2.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Kyrie.krn'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Lassus_Duets/Lassus_1_Beatus_Vir.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Josquin_Duets/Crucifixus.xml' #example of IR = half note
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Morley_Duets/7 Miraculous loves wounding.xml' # example of IR = quarter note

# Senfl Pieces:
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/AssumptaEst_normal.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/DumSteteritis_normal.xml'
piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/No01_Converte_nos Kopie.xml'

ind_piece = IndexedPiece(piece_path)
# ind_piece2 = IndexedPiece(piece_path2)
parts = ind_piece._import_score().parts
# parts2 = ind_piece2._import_score().parts

v_setts = {'quality': True, 'simple or compound': 'simple', 'directed': True, 'mp': False}
# v_setts_2 = {'quality': False, 'simple or compound': 'compound', 'directed': True, 'mp': False}
# h_setts = {'quality': False, 'horiz_attach_later': True, 'simple or compound': 'compound', 'directed': True, 'mp': False}
h_setts2 = {'quality': True, 'horiz_attach_later': True, 'simple or compound': 'compound', 'directed': True, 'mp': False}
n_setts = {'n': 3, 'continuer': '1', 'vertical': 'all',
           'terminator': [], 'open-ended': False, 'brackets': False}
n_setts_1 = {'n': 3, 'continuer': 'P1', 'vertical': 'all',
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_2 = {'n': 1, 'continuer': 'P1', 'vertical': [('0,3', '1,3', '2,3')],
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_3 = {'n': 2, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': [('0,3', '1,3', '2,3')],
           'terminator': ['Rest'], 'open-ended': False, 'brackets': True}
n_setts_4 = {'n': 3, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': 'all',
           'terminator': [], 'open-ended': False, 'brackets': False}

# pieces = (IndexedPiece(piece_path2), ind_piece)
# corpus = AggregatedPieces(pieces)
# pdb.set_trace()

nr = noterest.NoteRestIndexer(parts).run()
nr.columns = range(len(nr.columns))
nr_tc = nr.stack().value_counts()
nr_vc = pandas.concat([nr.iloc[:,v].value_counts() for v in range(len(nr.columns))], axis=1)

dr = meter.DurationIndexer(parts).run()
dr.columns = range(len(dr.columns))
dr_tc = dr.stack().value_counts()
dr_vc = pandas.concat([dr.iloc[:,v].value_counts() for v in range(len(dr.columns))], axis=1)

# Duration-weighted pitch counts for each voice
wnr_vc = pandas.DataFrame([dr[nr==x].sum() for x in nr_tc.index], index=nr_tc.index)
# for all voices combined
wnr_tc = wnr_vc.sum(axis=1)


ms = meter.MeasureIndexer(parts).run()
bs = meter.NoteBeatStrengthIndexer(parts).run()

# hz = interval.HorizontalIntervalIndexer(nr, h_setts).run()
hz2 = interval.HorizontalIntervalIndexer(nr, h_setts2).run()

# hz_tc = hz.stack().stack().value_counts()
# hz_vc = pandas.concat([hz.iloc[:,v].value_counts() for v in range(len(hz.columns))], axis=1)
hz2_tc = hz2.stack().stack().value_counts()
hz2_vc = pandas.concat([hz2.iloc[:,v].value_counts() for v in range(len(hz2.columns))], axis=1)

vt = interval.IntervalIndexer(nr, v_setts).run()
# vt2 = interval.IntervalIndexer(nr, v_setts_2).run()

vt_tc = vt.stack().stack().value_counts()
vt_vc = pandas.concat([vt.iloc[:,v].value_counts() for v in range(len(vt.columns))], axis=1)

# pdb.set_trace()

# ng = new_ngram.NewNGramIndexer((hz,), n_setts).run()
# ng_1 = new_ngram.NewNGramIndexer((hz2,), n_setts_1).run()
# ng_2 = new_ngram.NewNGramIndexer((vt,), n_setts_2).run()
# ng_3 = new_ngram.NewNGramIndexer((vt, hz,), n_setts_3).run()
ng_4 = new_ngram.NewNGramIndexer((vt, hz2,), n_setts_4).run()
# ng_4.to_csv('/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/Sample results.csv')

# Spot cadences missing ficta:
missing_ficta = ng_4[ng_4 == 'm7 P1 m6 -M2 P8'].dropna(how='all')

# nr2 = noterest.NoteRestIndexer(parts2).run()
# dr2 = meter.DurationIndexer(parts2).run()
# hz3 = interval.HorizontalIntervalIndexer(nr2, h_setts).run()
# vt3 = interval.IntervalIndexer(nr2, v_setts_2).run()

# ng_5 = new_ngram.NewNGramIndexer((vt3, hz3,), n_setts_4).run()
# ng_5.stack().stack().value_counts().to_csv('/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/Sample results2.csv')

# dissonances = dissonance.DissonanceIndexer([bs_ind, dur_ind, horiz, vert_ints]).run()


pdb.set_trace()
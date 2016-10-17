from vis.analyzers.indexers import noterest, interval, ngram, meter, dissonance #, active_voices
from vis.models import indexed_piece
# from vis.models.indexed_piece import IndexedPiece
# from vis.models.aggregated_pieces import AggregatedPieces
import pandas
import pdb
import time

import vis
VIS_PATH = vis.__path__[0]

# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos2308.mei'
# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/bwv2.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Kyrie.krn'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Lassus_Duets/Lassus_1_Beatus_Vir.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Josquin_Duets/Crucifixus.xml' #example of IR = half note
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Morley_Duets/7 Miraculous loves wounding.xml' # example of IR = quarter note
chopin_prelude = '/home/amor/Code/vis-framework/vis/scripts/prelude28-20.mid'

# Senfl_Buchner folder:
folder = '/home/amor/Code/vis-framework/vis/scripts/Senfl motets'
# Senfl Pieces:
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl motets/No03_LaudateDominum_ns_final.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/AssumptaEst_normal.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/DumSteteritis_normal.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/No01_Converte_nos Kopie.xml'

# Extremely short piece:
piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/test_fermata_rest.xml'


v_setts = {'quality': True, 'simple or compound': 'simple', 'directed': True}
# v_setts_2 = {'quality': False, 'simple or compound': 'compound', 'directed': True, 'mp': False}
# h_setts = {'quality': False, 'horiz_attach_later': True, 'simple or compound': 'compound', 'directed': True, 'mp': False}
h_setts2 = {'quality': False, 'horiz_attach_later': True, 'simple or compound': 'compound', 'directed': True, 'mp': False}
n_setts = {'n': 3, 'continuer': '1', 'vertical': 'all',
           'terminator': [], 'open-ended': False, 'brackets': False}
n_setts_1 = {'n': 3, 'continuer': 'P1', 'vertical': 'all',
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_2 = {'n': 1, 'continuer': 'P1', 'vertical': [('0,3', '1,3', '2,3')],
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_3 = {'n': 2, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': [('0,3', '1,3', '2,3')],
           'terminator': ['Rest'], 'open-ended': False, 'brackets': True}
n_setts_4 = {'n': 3, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': 'all',
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False, 'align': 'right'}
n_setts_5 = {'n': 3, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': 'all',
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
ip = indexed_piece.Importer(piece_path)
hz = ip.get_data('horizontal_interval')
# setts = {'use_title': True, 'run_lilypond':True, 'output_pathname': 'trialpath'}#, 'annotation_part': hz}
# ip.get_data('lilypond', data=ip._score, settings=setts)
# out_path = '/home/amor/new/vis-framework/vis/scripts/Success'
# setts = {'run_lilypond': True, 'output_pathname': out_path}
# ip.get_data('lilypond', data=[ip._score], settings=setts)
pdb.set_trace()
t0 = time.time()
# input_dfs = [ip.get_data('noterest'), ip.get_data('vertical_interval')]
# ob_setts = {'type': 'notes'}
# overbass = ip.get_data('over_bass', data=input_dfs, settings=ob_setts)
# ca_setts = {'length': 3}
# ca = ip.get_data('cadence', data=[overbass], settings=ca_setts)
# ag = indexed_piece.Importer(folder)
# di = ag.get_data(ind_analyzer='dissonance')
# ps = ip._get_part_streams()
# bs = ip._get_beat_strength()
# dr = ip._get_duration()
# ms = ip._get_measure()
# nr = ip._get_noterest()
# vz = ip._get_vertical_interval(h_setts2)
# hz = ip._get_horizontal_interval(v_setts)
# recursed = ip._get_m21_objs()
# mnr = ip._get_multistop()
# # vz = ip._get_vertical_interval(v_setts)
# av = active_voices.ActiveVoicesIndexer(nr).run()
# ng = ngram.NGramIndexer((vz, hz), n_setts_4).run()
t1 = time.time()
# ng2 = ngram.NGramIndexer((vz, hz), n_setts_5).run()
# t2 = time.time()
print(t1-t0)
# print(t2-t1)
pdb.set_trace()
# ind_piece2 = IndexedPiece(piece_path2)
# parts = ip._import_score().parts
# parts2 = ind_piece2._import_score().parts

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

# # Duration-weighted pitch counts for each voice
# wnr_vc = pandas.DataFrame([dr[nr==x].sum() for x in nr_tc.index], index=nr_tc.index)
# # for all voices combined
# wnr_tc = wnr_vc.sum(axis=1)


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

# ng = ngram.NGramIndexer((hz,), n_setts).run()
# ng_1 = ngram.NGramIndexer((hz2,), n_setts_1).run()
# ng_2 = ngram.NGramIndexer((vt,), n_setts_2).run()
# ng_3 = ngram.NGramIndexer((vt, hz,), n_setts_3).run()
ng_4 = ngram.NGramIndexer((vt, hz2,), n_setts_4).run()
# ng_4.to_csv('/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/Sample results.csv')

# Spot cadences missing ficta:
missing_ficta = ng_4[ng_4 == 'm7 P1 m6 -M2 P8'].dropna(how='all')

# nr2 = noterest.NoteRestIndexer(parts2).run()
# dr2 = meter.DurationIndexer(parts2).run()
# hz3 = interval.HorizontalIntervalIndexer(nr2, h_setts).run()
# vt3 = interval.IntervalIndexer(nr2, v_setts_2).run()

# ng_5 = ngram.NGramIndexer((vt3, hz3,), n_setts_4).run()
# ng_5.stack().stack().value_counts().to_csv('/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/Sample results2.csv')

# dissonances = dissonance.DissonanceIndexer([bs_ind, dur_ind, horiz, vert_ints]).run()


pdb.set_trace()
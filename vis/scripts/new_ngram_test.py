from vis.analyzers.indexers import noterest, interval, new_ngram
from vis.models.indexed_piece import IndexedPiece
import pandas as pd
import pdb
import time

import vis
VIS_PATH = vis.__path__[0]

piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos2308.mei'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Lassus_Duets/Lassus_1_Beatus_Vir.xml'
ind_piece = IndexedPiece(piece_path)
parts = ind_piece._import_score().parts

v_setts = {'quality': True, 'simple or compound': 'simple', 'directed': True}
h_setts = {'quality': True, 'horiz_attach_later': False, 'simple or compound': 'simple', 'directed': True}
n_setts = {'n': 2, 'horizontal': 'lowest', 'vertical': 'all pairs', 'terminator': ('Rest',)}

nr = noterest.NoteRestIndexer(parts).run()
vt = interval.IntervalIndexer(nr, v_setts).run()
hz = interval.HorizontalIntervalIndexer(nr, h_setts).run()
ng = new_ngram.NewNGramIndexer((vt, hz), n_setts).run()


pdb.set_trace()
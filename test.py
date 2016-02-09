
from vis.analyzers.indexers import noterest
from vis.models.indexed_piece import IndexedPiece
import music21


score = IndexedPiece('Ock1005a-Missa_De_plus_en_plus-Kyrie.mei')
test = score._import_score()
print(score.metadata('pieceRange'))
print(score.metadata('partRanges'))
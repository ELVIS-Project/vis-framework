from music21 import converter, graph
from collections import defaultdict
import sys

def main(argv):
    this, path = argv
    score = converter.parseFile(path)
    l = [(n.pitch.unicodeName, n.duration.quarterLength/score.duration.quarterLength) for n in score.flat.notes]
    d = defaultdict(float)
    for p, length in l: d[p] += length
    g = graph.GraphHistogram()
    g.setData(enumerate(int(v*100) for v in d.values()))
    g.setTicks('x', [(i+0.45, k) for k in d.keys()])
    g.process()

if __name__ == "__main__":
    main(sys.argv)
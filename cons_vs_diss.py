from music21 import converter, interval, note
from collections import Counter
import sys
from pylab import *

def main(argv):
    paths = argv[1:]
    scores = []
    for path in paths:
        try:
            scores.append(converter.parseFile(path))
        except:
            continue
    intervals = Counter()
    for score in scores:
        offsets = set()
        for n in score.flat.notes: offsets.add(n.offset)
        for offset in offsets:
            notes_by_part = {p.id: p.flat.getElementsByClass(note.Note).getElementsByOffset(offset) for p in score.parts}
            sounding_parts = [p for p,l in notes_by_part.items() if l]
            lowest = min(notes_by_part[p][0].pitch for p in sounding_parts)
            lowest_voice = [p for p in sounding_parts
                if notes_by_part[p][0].pitch == lowest][-1]
            intervs = [interval.Interval(
                notes_by_part[lowest_voice][0],
                notes_by_part[p][0]
            ).generic.semiSimpleDirected for p in sounding_parts if not p == lowest_voice]
            intervals.update(intervs)
    
    CONSONANTS = [1, 3, 5, 6, 8]
    DISSONANTS = [2, 4, 7]
    
    print dict(intervals)
    
    # make a square figure and axes
    figure(1, figsize=(6,6))
    ax = axes([0.1, 0.1, 0.8, 0.8])

    # The slices will be ordered and plotted counter-clockwise.
    labels = 'Consonant', 'Dissonant'
    fracs = [int(sum(float(v) for k,v in intervals.items() if k in CONSONANTS)/sum(intervals.values()) * 100),
             int(sum(float(v) for k,v in intervals.items() if k in DISSONANTS)/sum(intervals.values()) * 100)]
    explode= 0, 0

    pie(fracs, explode=explode, labels=labels,
        autopct='%1.1f%%', shadow=True)

    title('Consonant vs Dissonant', bbox={'facecolor':'0.8', 'pad':5})

    show()

if __name__ == "__main__":
    main(sys.argv)
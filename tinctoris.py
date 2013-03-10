#!/usr/bin/python
from controllers.importer import Importer
from controllers.analyzer import Analyzer
from models.analyzing import ListOfPieces
from PyQt4.QtCore import Qt
from music21.note import Note
from music21.interval import Interval
from itertools import chain
import csv
import sys

def piece_to_records(piece, tenor):
	'''
	INPUTS:
	piece - path to a music21-importable file
	tenor - index of the tenor voice in the file
	
	OUTPUT:
	A list of AnalysisRecord objects, one for each voice pair containing the tenor
	'''
	importer, analyzer = Importer(), Analyzer()
	importer.add_pieces([piece])
	pieces_list = importer.import_pieces(ListOfPieces())
	print 'pieces_list', pieces_list._pieces
	index = pieces_list.createIndex(0, ListOfPieces.parts_list)
	parts = range(len(pieces_list.data(index, Qt.DisplayRole)))
	parts.remove(tenor)
	index = pieces_list.createIndex(0, ListOfPieces.parts_combinations)
	analyzer._list_of_pieces = pieces_list
	analyzer.set_data(index, [[ind,tenor] for ind in parts])
	return analyzer.run_analysis()

def analyze(piece, tenor):
	'''
	INPUTS:
	piece - path to a music21-importable file
	tenor - index of the tenor voice in the file
	
	OUTPUT:
	a list of tuples (interval,
					  2-gram,
					  # of times the 2-gram occurs,
					  # of times/# of 2-grams starting with interval,
					  # of times/# of 2-grams with the same first and last interval,
					  # of times/# of 2-grams starting with interval and same melodic interval,
					  # of times/# of 2-grams with the same last interval,
					  # of times/# of 2-grams with the same melodic and final interval,
					  # of times/# of 2-grams with the same melodic interval)
	sorted by interval, for all the 2-grams appearing in the piece
	'''
	records = piece_to_records(piece, tenor)
	print 'records', records
	bigrams = []
	intervs = []
	for record in records:
		for first, next in zip(record,list(record)[1:]):
			_, (first_lower, first_upper) = first
			_, (next_lower, next_upper) = next
			try:
				first_vert = Interval(Note(first_lower), Note(first_upper)).generic.directed
				next_vert = Interval(Note(next_lower), Note(next_upper)).generic.directed
				horiz = Interval(Note(first_lower), Note(next_lower)).generic.directed
				bigrams.append((first_vert, horiz, next_vert))
				intervs.append(first_vert)
			except:
				continue
	intervs = sorted(set(intervs))
	histogram = {bigram:len([bg for bg in bigrams if bg==bigram])
				 for bigram in set(bigrams)}
	print 'histogram', histogram
	return list(chain(*[get_subtable(histogram, interv) for interv in intervs]))

def get_subtable(histogram, interval):
	'''
	INPUTS:
	histogram - a frequency histogram for bigrams in a fixed piece
	interval - an interval occurring in that piece
	
	OUTPUT:
	a list of tuples of the form described in analyze(), but only containing
	bigrams beginning with `interval`.
	'''
	sub_hg = {bigram:freq for bigram,freq in histogram.iteritems()
				 if bigram[0]==interval}
	rows = []
	for bigram in sub_hg.iterkeys():
		freq = float(sub_hg[bigram])
		# same_ij is the number of bigrams in the piece which have the same
		# intervals at positions i and j (where 0 is the first vertical interval,
		# 1 is the horizontal interval and 2 is the second vertical interval)
		same_0 = sum(sub_hg.values())
		same_02 = sum(v for bg,v in sub_hg.iteritems() if bg[2]==bigram[2])
		same_01 = sum(v for bg,v in sub_hg.iteritems() if bg[1]==bigram[1])
		same_2s = [(bg,v) for bg,v in histogram.iteritems() if bg[2]==bigram[2]]
		print 'same_2s', same_2s
		same_2 = sum(v for bg,v in same_2s)
		same_12 = sum(v for bg,v in same_2s if bg[1]==bigram[1])
		same_1 = sum(v for bg,v in histogram.iteritems() if bg[1]==bigram[1])
		rows.append((interval, bigram, int(freq), freq/same_0, freq/same_02, freq/same_01,
		             freq/same_2, freq/same_12, freq/same_1))
	return rows

def main(*args):
	'''
	INPUTS:
	args - a list of music21-importable file names and the index of the tenor
	voice in each
	
	OUTPUT:
	Creates a CSV file containing various statistics about 2-grams where one of
	the voices is the designated tenor.
	'''
	args = args[1:]
	pairs = [(arg,int(next)) for i,(arg,next) in enumerate(zip(args,args[1:])) if i % 2 == 0]
	table = list(chain(*[analyze(*pair) for pair in pairs]))
	with open('results.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
		writer.writerow(['Interval', 'Bigram', 'Freq of bigram', 'freq/same_0',
						 'freq/same_02', 'freq/same_01', 'freq/same_2', 'freq/same_12', 'freq/same_1'])
		for row in table:
			writer.writerow(row)
		csvfile.close()

if __name__ == "__main__":
	main(*sys.argv)
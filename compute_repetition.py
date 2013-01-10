from controllers.importer import Importer
from controllers.analyzer import Analyzer
from models.analyzing import ListOfPieces
from elvis_repetition import A_e, A_o, stringify
from math import log
import csv
import sys

if __name__ == '__main__':
	pieces = sys.argv[1:]
	analyses = []
	
	for piece in pieces:
		importer, analyzer = Importer(), Analyzer()
		importer.add_pieces([piece])
		importer.import_finished.connect(analyzer.catch_import)
		print 'importing...'
		l = importer.import_pieces()
		print 'import finished.'
		analyzer.set_data(l.createIndex(0,ListOfPieces.parts_combinations), [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]])
		print 'analyzing...'
		analyses.append((piece,analyzer.run_analysis()))
		print 'analysis finished.'

	with open('results.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
		for piece, records in analyses:
			writer.writerow([piece])
			writer.writerow(['Parts', 'A_o', 'A_e (estimated)', 'I_r'])
			for record in records:
				s = stringify(record)
				n, d = A_o(s), A_e(s)
				part1, part2 = tuple(record.part_names())
				writer.writerow([str(part1)+" & "+str(part2), n, d, log(n/d)])
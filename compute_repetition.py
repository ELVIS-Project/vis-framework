from controllers.importer import Importer
from controllers.analyzer import Analyzer
from models.analyzing import ListOfPieces
from elvis_repetition import A_e, A_o, stringify
from math import log
import csv
import sys

def piece_to_records(piece):
	importer, analyzer = Importer(), Analyzer()
	importer.add_pieces([piece])
	importer.import_finished.connect(analyzer.catch_import)
	l = importer.import_pieces()
	analyzer.set_data(l.createIndex(0,ListOfPieces.parts_combinations), 
						[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]])
	return analyzer.run_analysis()

if __name__ == '__main__':
	pieces = sys.argv[1:]

	with open('results.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
		for piece in pieces:
			importer, analyzer = Importer(), Analyzer()
			importer.add_pieces([piece])
			importer.import_finished.connect(analyzer.catch_import)
			print 'importing', piece, '...'
			l = importer.import_pieces()
			print 'import finished.'
			info = list(l.iterateRows())
			analyzer.set_data(l.createIndex(0,ListOfPieces.parts_combinations), 
								[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]])
			print 'analyzing...'
			writer.writerow([info[0][1][1]])
			writer.writerow(['A_o', 'A_e (estimated)', 'I_r'])
			strs = [stringify(r)[0] for r in analyzer.run_analysis()]
			print strs
			n, d = A_o(*strs), A_e(*strs)
			writer.writerow([n, d, log(n/d)])
			print 'analysis finished.'
		print 'results written to "results.csv"'
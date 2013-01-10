from math import log
from random import random
from collections import defaultdict
from suffix_tree import SuffixTree
from music21.interval import Interval
from music21.note import Note
# NB: requires SuffixTree, from http://www.daimi.au.dk/~mailund/suffix_tree.html
'''
This module contains the statistical machinery required to apply a measure of repetition
discovered for use in genomics to strings. Also it can be used to convert vis
AnalysisRecords into strings, where the statistical computations are the same. One can use
`python elvis_repetition.py` to see a sample computation done to compare the repretition
of sample strings randomly generated with English-like and Dutch-like patterns, or in a 
shell or scope with vis AnalysisRecords:
>>> from elvis_repetition import I_r
>>> I_r(record)
will give the index of repetition, where `record` is an AnalysisRecord in the local namespace.
'''

def I_r(record):
	s = stringify(record)
	return log(A_o(s)/A_e(s))

def A_o(s):
	t = SuffixTree(s)
	return sum(n.parent.stringDepth + 1 for n in t.leaves) - 1

def A_e(s):
	m = markov(s)
	ret = 0
	diff = 1000.0
	n = 0
	while diff > 0.01:
		print 'iterating monte carlo', ret, diff
		r = random_chain(m,len(s))
		a = float(A_o(r) + n*ret)/(n+1)
		diff = abs(a - ret)
		ret = a
		n += 1
	return ret
	
def markov(s):
	print 'computing transition matrix'
	d = {}
	for ch in set(s):
		dd = defaultdict(float)
		nexts = [j for i,j in zip(s,s[1:]) if i==ch]
		for next in nexts:
			dd[next] += 1.0/len(nexts)
		d[ch] = dict(dd)
	return d

def random_chain(matrix, length):
	def add_char(so_far):
		dont_try = [[None] for i in range(length)]
		while len(so_far) < length:
			print so_far
			dist = None
			if len(so_far) == 0:
				dist = [(key, 1.0/len(matrix.keys())) for key in matrix.keys()]
			else:
				dist = matrix[so_far[-1]].items()
			if dist:
				ch = None
				while ch in dont_try[len(so_far)]:
					if [key for key,prob in dist if key not in dont_try[len(so_far)]]:
						k = random()
						e = enumerate(dist)
						land = [s for i,(s,p) in e if 0 < k - sum(pr for _,pr in dist[:i]) <= p]
						ch = land[0]
					else:
						so_far = so_far[:-1]
				so_far += ch
			else:
				dont_try[len(so_far)-1].append(so_far[-1])
				so_far = so_far[:-1]
		return so_far
	s = add_char('')
	return s

def stringify(record):
	tokens = []
	for first, next in zip(record,list(record)[1:]):
		_, (first_lower, first_upper) = first
		_, (next_lower, next_upper) = next
		first_vert = Interval(Note(first_lower), Note(first_upper)).generic.semiSimpleDirected
		next_vert = Interval(Note(next_lower), Note(next_upper)).generic.semiSimpleDirected
		horiz = Interval(Note(first_lower), Note(next_lower)).generic.semiSimpleDirected
		tokens.append((first_vert, horiz, next_vert))
	trans = {tok:unichr(i+100) for i,tok in enumerate(set(tokens))}
	return "".join(trans[tok] for tok in tokens)

if __name__ == "__main__":
	st = '''	Lose away off why half led have near bed. At engage simple father of period others except. My giving do summer of though narrow marked at. Spring formal no county ye waited. My whether cheered at regular it of promise blushes perhaps. Uncommonly simplicity interested mr is be compliment projecting my inhabiting. Gentleman he september in oh excellent. 

	Speedily say has suitable disposal add boy. On forth doubt miles of child. Exercise joy man children rejoiced. Yet uncommonly his ten who diminution astonished. Demesne new manners savings staying had. Under folly balls death own point now men. Match way these she avoid see death. She whose drift their fat off. 

	She who arrival end how fertile enabled. Brother she add yet see minuter natural smiling article painted. Themselves at dispatched interested insensible am be prosperous reasonably it. In either so spring wished. Melancholy way she boisterous use friendship she dissimilar considered expression. Sex quick arose mrs lived. Mr things do plenty others an vanity myself waited to. Always parish tastes at as mr father dining at. 

	Carried nothing on am warrant towards. Polite in of in oh needed itself silent course. Assistance travelling so especially do prosperous appearance mr no celebrated. Wanted easily in my called formed suffer. Songs hoped sense as taken ye mirth at. Believe fat how six drawing pursuit minutes far. Same do seen head am part it dear open to. Whatever may scarcely judgment had. 

	He unaffected sympathize discovered at no am conviction principles. Girl ham very how yet hill four show. Meet lain on he only size. Branched learning so subjects mistress do appetite jennings be in. Esteems up lasting no village morning do offices. Settled wishing ability musical may another set age. Diminution my apartments he attachment is entreaties announcing estimating. And total least her two whose great has which. Neat pain form eat sent sex good week. Led instrument sentiments she simplicity. 

	Passage its ten led hearted removal cordial. Preference any astonished unreserved mrs. Prosperous understood middletons in conviction an uncommonly do. Supposing so be resolving breakfast am or perfectly. Is drew am hill from mr. Valley by oh twenty direct me so. Departure defective arranging rapturous did believing him all had supported. Family months lasted simple set nature vulgar him. Picture for attempt joy excited ten carried manners talking how. Suspicion neglected he resolving agreement perceived at an. 

	So insisted received is occasion advanced honoured. Among ready to which up. Attacks smiling and may out assured moments man nothing outward. Thrown any behind afford either the set depend one temper. Instrument melancholy in acceptance collecting frequently be if. Zealously now pronounce existence add you instantly say offending. Merry their far had widen was. Concerns no in expenses raillery formerly. 

	By an outlived insisted procured improved am. Paid hill fine ten now love even leaf. Supplied feelings mr of dissuade recurred no it offering honoured. Am of of in collecting devonshire favourable excellence. Her sixteen end ashamed cottage yet reached get hearing invited. Resources ourselves sweetness ye do no perfectly. Warmly warmth six one any wisdom. Family giving is pulled beauty chatty highly no. Blessing appetite domestic did mrs judgment rendered entirely. Highly indeed had garden not. 

	No opinions answered oh felicity is resolved hastened. Produced it friendly my if opinions humoured. Enjoy is wrong folly no taken. It sufficient instrument insipidity simplicity at interested. Law pleasure attended differed mrs fat and formerly. Merely thrown garret her law danger him son better excuse. Effect extent narrow in up chatty. Small are his chief offer happy had. 

	Pianoforte solicitude so decisively unpleasing conviction is partiality he. Or particular so diminution entreaties oh do. Real he me fond show gave shot plan. Mirth blush linen small hoped way its along. Resolution frequently apartments off all discretion devonshire. Saw sir fat spirit seeing valley. He looked or valley lively. If learn woody spoil of taken he cause.'''
	dutch = '''	Tot bovenkant zes regentijd zee vernieuwd. Ze herhaling er behandeld in leeningen krachtige. Welvaart ten baksteen plaatsen staatjes goa dag een. Amboina zes rijkdom stammen aan bewogen met den. Varen gayah waren na de reeds. Oven de tijd af want lang. Te geheelen er na speurzin mogelijk bepaalde engelsch. 

	Ruwe per daar den veel. Ten dit concurrent van plotseling aanplanten inspanning zin vaartuigen economisch. Vroegeren wassching inlandsen onderling er de na. Heuvel gronds zoo kegels overal lossen oosten wat. Op ze noemt de beste sinds groen. Eronder bekoeld sap schepen dollars wat gebeurt ver. Ruimer breede op af zekere er. En ad metaal binnen om cijfer heuvel. Op vreemden menschen gestookt hellende hectaren ze veertien. 

	Maleische van engelsche kleederen sap gebruiken aan degelijke. Dit nadat zoo onder eigen ton kwala. Menschen zit opbrengt wij krachten dat hectaren. In bakje bezig in groot lange. Zooveel plantte ze geoogst en bereikt trekken. Dichtbij ze bordeaux op lateriet. 

	Met kostbare inwoners als middelen. Gewasschen en af is interesten ad ingesneden weelderige voorloopig. Centimes ze sembilan mijnwerk na gebracht behouden. Procede gekomen betreft ik rijkdom te in. Schatkist brandhout wijselijk nu al. Verkochten locomobiel traliewerk ze om plotseling vergissing er nu. Ze centraal schijnen voorziet stelling op. 

	Dik streng rijken steden bak een. Aan sunger met per weg lijnen lijden. Wonde eerst als wegen gif vindt lagen. Misschien dit prachtige nam verdiende was evenwicht. Het wat zoo europeanen opgebracht natuurlijk aanplanten uitgevoerd. Leelijk ze scholen in blijven ad. Kedona sap hoogte wouden per slotte heuvel openen. Na stam laag ik sago. Er is voet acre hout of zich. 

	Op bakje bezig op te de heele ijzer. Scheidden ik gelukkige of bevolking ongunstig al. Hoopen uit breede dienen ook zilver mollen herten. Hadden er eenige altijd er bakjes al. Het elk gerust openen zoo langen sakais zee eerste. Agentschap wij wat opgebracht insnijding lot intusschen hollanders mijnschool. Poeloe zullen are mee wie groene wat. 

	Klei op op toen half zout en. Rijkdommen voorloopig initiatief elk wie toe dal. Of zelf gaat te niet mier stad. Bezwarend te denkbeeld af ze plaatsing aanvoeren wijselijk evenwicht. Percent bewogen product ik na nu en tinmijn. Vast aan tin het zijn voet over een. Omgeving den wildrijk met veteraan schatten beletsel kostbaar ten. Getaxeerde nam lot met inspanning wonderbare productief. Singapore antwerpen vroegeren stoompomp of ze er bovenkant. 

	Langen meende werden andere waarin nam toe. Al wakkeren resident na uithoudt om meenemen onzuiver of. Vaartuigen buitendien kwartslaag al voorloopig op al en feestdagen. Geheel afzien ze wolken zouden de al arbeid na. Vestigen verbindt ze resident af schatten na. Of ze ingewanden uitgegeven millioenen om. Bij aan zand noch lot lage. 

	Te te mooren ze is daarin succes. Der gelukkige bijgeloof bedroegen stoompomp mekongdal had. Al op ontgonnen gelukkige gedeelten. Alluviale uitrollen prachtige nu er arabieren onderling er. Is rijk naam zijn om er. Ik in wetenschap vergrooten op nu plotseling. Uit mag ontginnen weg antwerpen australie geschiedt wij. Bladen mooren gif koffie leenen streek gezegd den tot hen. 

	Zit verbazende bevaarbaar ongunstige een ingewanden spoorwegen weelderige. Op forten er is soegei spelen dragen te. Tweemaal of maleiers indische gezegend nu ernstige af uitmaakt. Mijn werk arme er af zich op door geen. Elk dik zijde eerst drong toe. Volledige ook plaatsing kan ontgonnen goa schepping dat ingenieur regeering. Af aanraking er bepaalden ze de kleederen. Land in er daad en al zelf. Aanmerking uitgegeven van dat die verzamelen.'''
	n, d = A_o(dutch), A_e(dutch)
	a, c = A_o(st), A_e(st)
	print 'English:'
	print a, c, log(float(a)/c)
	print 'Dutch:'
	print n, d, log(float(n)/d)
	# OUTPUT
	# English:
	# 20979 16900.6494845 0.216169885162
	# Dutch:
	# 18914 15235.3064516 0.216286861385
	# wow, almost exactly the same index of repetition! Is this an inherent problem? I get a similar value for most written language,
	# but not for completely shuffled random strings.
#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: elvis_repetition.py
# Purpose: ?
#
# Copyright (C) 2012, 2013 Jamie Klassen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
"""
This module contains the statistical machinery required to apply a measure of repetition
discovered for use in genomics to strings. Also it can be used to convert vis
AnalysisRecords into strings, where the statistical computations are the same. One can use
`python elvis_repetition.py` to see a sample computation done to compare the repretition of
sample strings randomly generated with English-like and Dutch-like patterns, or in a shell or
scope with vis AnalysisRecords:
>>> from vis.models.analyzing import AnalysisRecord
>>> record = AnalysisRecord
>>> from vis.elvis_repetition import repetition_index
>>> repetition_index(record)
will give the index of repetition, where `record` is an AnalysisRecord in the local namespace.
"""

from math import log
from random import random
from collections import defaultdict
from suffix_tree import GeneralisedSuffixTree
from music21.interval import Interval, IntervalException
from music21.note import Note
# NB: requires SuffixTree, from http://www.daimi.au.dk/~mailund/suffix_tree.html


def repetition_index(record):
    """
    Compute the I_r for the given sample.
    :param record: an AnalysisRecord
    :return: the computed index of repetition
    """
    stringified = stringify(record)[0]
    return log(observed_a([stringified]) / a_expected([stringified]))


def observed_a(strings):
    """
    Observe the value of "a" from the samples as defined in our genomics paper.
    :param strings: sample strings
    :type strings: list of str
    :return: the computed value of "a".
    :rtype: int
    """
    tree = GeneralisedSuffixTree(list(strings))
    return sum(n.parent.stringDepth + 1 for n in tree.leaves) - 1


def a_expected(strings):
    """
    Compute the expected value of observed_a by generating a Markov model from the samples
    provided and iterating averages.
    :param strings: iterable of iterables of characters, the sample text to use.
    :return: The computed expected value of observed_a
    :type strings: list of str
    """
    markov_matrix = markov(strings)
    print markov_matrix
    print 'estimating expectation'
    ret = 0
    diff = 1000.0
    n = 0
    donts = [[[None] for _ in range(len(arg))] for arg in strings]
    while diff > 0.01:
        print '...'
        chains = [random_chain(markov_matrix, len(arg), donts[i]) for i, arg in enumerate(strings)]
        a_value = float(observed_a(chains) + n * ret) / (n + 1)
        diff = abs(a_value - ret)
        ret = a_value
        n += 1
    return ret


def markov(samples):
    """
    Compute the markov transition matrix from the given sample strings
    :param samples: the sample strings
    :return: the transition matrix
    :rtype: dict
    """
    print 'computing transition matrix'
    matrix = {}
    print samples
    for char in set("".join(samples)):
        print char
        row = defaultdict(float)
        for sample in samples:
            nexts = [j for i, j in zip(sample, sample[1:]) if i == char]
            print nexts
            for next_char in nexts:
                row[next_char] += 1.0
        matrix[char] = dict(row)
    return matrix


def random_chain(matrix, length, dont_try):
    """
    Generate a Markov chain.

    :param matrix: the transition matrix for this model
    :param length: the length of chain to be generated
    :param dont_try: an iterable of characters which should not be added to the chain
    :return: s -- the generated chain
    """

    def add_char(so_far):
        """
        Add a character at random to the given list, according to the transition matrix given.
        :param so_far: the string up to this point
        :return: the string, with the new random character appended
        """
        while len(so_far) < length:
            if len(so_far) == 0:
                dist = [(key, 1.0 / len(matrix.keys())) for key in matrix.keys()]
            else:
                dist = matrix[so_far[-1]].items()
            if dist:
                sensible = [(key, prob) for key, prob in dist if key not in dont_try[len(so_far)]]
                if sensible:
                    tot = sum(prob for key, prob in sensible)
                    dist = [(key, prob / tot) for key, prob in sensible]
                    key = random()
                    enum = enumerate(dist)
                    land = []
                    for i, (char, prob) in enum:
                        if 0 < key - sum(pr for _, pr in dist[:i]) <= prob:
                            land.append(char)
                    so_far += land[0]
                else:
                    dont_try[len(so_far) - 1].append(so_far[-1])
                    so_far = so_far[:-1]
            else:
                dont_try[len(so_far) - 1].append(so_far[-1])
                so_far = so_far[:-1]
        return so_far

    return add_char('')


def stringify(record):
    """
    Convert an AnalysisRecord into a string, by tokenizing the 2-grams.
    :param record: the AnalysisRecord to be transformed
    :return: the tokenized version
    :rtype: str
    """
    tokens = []
    for first, second in zip(record, list(record)[1:]):
        _, (first_lower, first_upper) = first
        _, (next_lower, next_upper) = second
        try:
            first_vert = Interval(Note(first_lower), Note(first_upper)).generic.directed
            next_vert = Interval(Note(next_lower), Note(next_upper)).generic.directed
            horiz = Interval(Note(first_lower), Note(next_lower)).generic.directed
            tokens.append((first_vert, horiz, next_vert))
        except IntervalException:
            continue
    trans = {tok: unichr(i + 100) for i, tok in enumerate(set(tokens))}
    return "".join(trans[tok] for tok in tokens), trans


def main():
    """
    Run the example query on english and dutch strings.
    """
    english = '''
    Lose away off why half led have near bed. At engage simple father of period
    others except. My giving do summer of though narrow marked at. Spring formal no county ye
    waited. My whether cheered at regular it of promise blushes perhaps. Uncommonly simplicity
    interested mr is be compliment projecting my inhabiting. Gentleman he september in oh excellent.
    Speedily say has suitable disposal add boy. On forth doubt miles of child. Exercise joy man
    children rejoiced. Yet uncommonly his ten who diminution astonished. Demesne new manners
    savings staying had. Under folly balls death own point now men. Match way these she avoid see
    death. She whose drift their fat off. She who arrival end how fertile enabled. Brother she
    add yet see minuter natural smiling article painted. Themselves at dispatched interested
    insensible am be prosperous reasonably it. In either so spring wished. Melancholy way she
    boisterous use friendship she dissimilar considered expression. Sex quick arose mrs lived. Mr
    things do plenty others an vanity myself waited to. Always parish tastes at as mr father
    dining at. Carried nothing on am warrant towards. Polite in of in oh needed itself silent
    course. Assistance travelling so especially do prosperous appearance mr no celebrated. Wanted
     easily in my called formed suffer. Songs hoped sense as taken ye mirth at. Believe fat how
     six drawing pursuit minutes far. Same do seen head am part it dear open to. Whatever may
     scarcely judgment had. He unaffected sympathize discovered at no am conviction principles.
     Girl ham very how yet hill four show. Meet lain on he only size. Branched learning so
     subjects mistress do appetite jennings be in. Esteems up lasting no village morning do
     offices. Settled wishing ability musical may another set age. Diminution my apartments he
     attachment is entreaties announcing estimating. And total least her two whose great has
     which. Neat pain form eat sent sex good week. Led instrument sentiments she simplicity.
    Passage its ten led hearted removal cordial. Preference any astonished unreserved mrs.
    Prosperous understood middletons in conviction an uncommonly do. Supposing so be resolving
    breakfast am or perfectly. Is drew am hill from mr. Valley by oh twenty direct me so.
    Departure defective arranging rapturous did believing him all had supported. Family months
    lasted simple set nature vulgar him. Picture for attempt joy excited ten carried manners
    talking how. Suspicion neglected he resolving agreement perceived at an. So insisted received
     is occasion advanced honoured. Among ready to which up. Attacks smiling and may out assured
     moments man nothing outward. Thrown any behind afford either the set depend one temper.
     Instrument melancholy in acceptance collecting frequently be if. Zealously now pronounce
     existence add you instantly say offending. Merry their far had widen was. Concerns no in
     expenses raillery formerly. By an outlived insisted procured improved am. Paid hill fine ten
      now love even leaf. Supplied feelings mr of dissuade recurred no it offering honoured. Am
      of of in collecting devonshire favourable excellence. Her sixteen end ashamed cottage yet
      reached get hearing invited. Resources ourselves sweetness ye do no perfectly. Warmly
      warmth six one any wisdom. Family giving is pulled beauty chatty highly no. Blessing
      appetite domestic did mrs judgment rendered entirely. Highly indeed had garden not.
    No opinions answered oh felicity is resolved hastened. Produced it friendly my if opinions
    humoured. Enjoy is wrong folly no taken. It sufficient instrument insipidity simplicity at
    interested. Law pleasure attended differed mrs fat and formerly. Merely thrown garret her law
     danger him son better excuse. Effect extent narrow in up chatty. Small are his chief offer
     happy had. Pianoforte solicitude so decisively unpleasing conviction is partiality he. Or
     particular so diminution entreaties oh do. Real he me fond show gave shot plan. Mirth blush
     linen small hoped way its along. Resolution frequently apartments off all discretion
     devonshire. Saw sir fat spirit seeing valley. He looked or valley lively. If learn woody
     spoil of taken he cause.
     '''
    dutch = '''
    Tot bovenkant zes regentijd zee vernieuwd. Ze herhaling er behandeld in leeningen krachtige.
    Welvaart ten baksteen plaatsen staatjes goa dag een. Amboina zes rijkdom stammen aan bewogen
    met den. Varen gayah waren na de reeds. Oven de tijd af want lang. Te geheelen er na speurzin
     mogelijk bepaalde engelsch. Ruwe per daar den veel. Ten dit concurrent van plotseling
     aanplanten inspanning zin vaartuigen economisch. Vroegeren wassching inlandsen onderling er
     de na. Heuvel gronds zoo kegels overal lossen oosten wat. Op ze noemt de beste sinds groen.
     Eronder bekoeld sap schepen dollars wat gebeurt ver. Ruimer breede op af zekere er. En ad
     metaal binnen om cijfer heuvel. Op vreemden menschen gestookt hellende hectaren ze veertien.
    Maleische van engelsche kleederen sap gebruiken aan degelijke. Dit nadat zoo onder eigen ton
    kwala. Menschen zit opbrengt wij krachten dat hectaren. In bakje bezig in groot lange.
    Zooveel plantte ze geoogst en bereikt trekken. Dichtbij ze bordeaux op lateriet. Met kostbare
     inwoners als middelen. Gewasschen en af is interesten ad ingesneden weelderige voorloopig.
     Centimes ze sembilan mijnwerk na gebracht behouden. Procede gekomen betreft ik rijkdom te
     in. Schatkist brandhout wijselijk nu al. Verkochten locomobiel traliewerk ze om plotseling
     vergissing er nu. Ze centraal schijnen voorziet stelling op. Dik streng rijken steden bak
     een. Aan sunger met per weg lijnen lijden. Wonde eerst als wegen gif vindt lagen. Misschien
     dit prachtige nam verdiende was evenwicht. Het wat zoo europeanen opgebracht natuurlijk
     aanplanten uitgevoerd. Leelijk ze scholen in blijven ad. Kedona sap hoogte wouden per slotte
      heuvel openen. Na stam laag ik sago. Er is voet acre hout of zich. Op bakje bezig op te de
      heele ijzer. Scheidden ik gelukkige of bevolking ongunstig al. Hoopen uit breede dienen ook
       zilver mollen herten. Hadden er eenige altijd er bakjes al. Het elk gerust openen zoo
       langen sakais zee eerste. Agentschap wij wat opgebracht insnijding lot intusschen
       hollanders mijnschool. Poeloe zullen are mee wie groene wat. Klei op op toen half zout en.
        Rijkdommen voorloopig initiatief elk wie toe dal. Of zelf gaat te niet mier stad.
        Bezwarend te denkbeeld af ze plaatsing aanvoeren wijselijk evenwicht. Percent bewogen
        product ik na nu en tinmijn. Vast aan tin het zijn voet over een. Omgeving den wildrijk
        met veteraan schatten beletsel kostbaar ten. Getaxeerde nam lot met inspanning wonderbare
         productief. Singapore antwerpen vroegeren stoompomp of ze er bovenkant. Langen meende
         werden andere waarin nam toe. Al wakkeren resident na uithoudt om meenemen onzuiver of.
         Vaartuigen buitendien kwartslaag al voorloopig op al en feestdagen. Geheel afzien ze
         wolken zouden de al arbeid na. Vestigen verbindt ze resident af schatten na. Of ze
         ingewanden uitgegeven millioenen om. Bij aan zand noch lot lage. Te te mooren ze is
         daarin succes. Der gelukkige bijgeloof bedroegen stoompomp mekongdal had. Al op
         ontgonnen gelukkige gedeelten. Alluviale uitrollen prachtige nu er arabieren onderling
         er. Is rijk naam zijn om er. Ik in wetenschap vergrooten op nu plotseling. Uit mag
         ontginnen weg antwerpen australie geschiedt wij. Bladen mooren gif koffie leenen streek
         gezegd den tot hen. Zit verbazende bevaarbaar ongunstige een ingewanden spoorwegen
         weelderige. Op forten er is soegei spelen dragen te. Tweemaal of maleiers indische
         gezegend nu ernstige af uitmaakt. Mijn werk arme er af zich op door geen. Elk dik zijde
         eerst drong toe. Volledige ook plaatsing kan ontgonnen goa schepping dat ingenieur
         regeering. Af aanraking er bepaalden ze de kleederen. Land in er daad en al zelf.
         Aanmerking uitgegeven van dat die verzamelen.'''
    num_d, denom_d = observed_a([dutch]), a_expected([dutch])
    num_e, denom_e = observed_a([english]), a_expected([english])
    print 'English:'
    print num_e, denom_e, log(float(num_e) / denom_e)
    print 'Dutch:'
    print num_d, denom_d, log(float(num_d) / denom_d)
    # OUTPUT
    # English:
    # 20979 16900.6494845 0.216169885162
    # Dutch:
    # 18914 15235.3064516 0.216286861385
    # wow, almost exactly the same index of repetition! Is this an inherent problem? I get a
    # similar value for most written language, but not for completely shuffled random strings.


if __name__ == "__main__":
    main()

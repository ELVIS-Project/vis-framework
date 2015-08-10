# Filename:               vis/analyzers/experimenters/dendrogram.py
# Purpose:                Experimenters related to hierarchical clustering.
#
# Copyright (C) 2015 Alexander Morgan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Alexander Morgan

Experimenters related to executing hierachical clustering analysis and dendrograms to illustrate
these clusterings. 
"""

# pylint: disable=pointless-string-statement
from os import path
import vis
from vis.analyzers import experimenter
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import pdb

class HierarchicalClusterer(experimenter.Experimenter):
    """
    Cluster VIS analysis profiles according to their similarity and output a dendrogram of the
    results using matplotlib and scipy. An "analysis profile" typically consists of all of the
    results of a given type of analysis, e.g. interval 2-grams, for a single piece. When the
    analysis profiles of two pieces are compared, the clustering algorithm determines how similar
    they are on the provided metric by evaluating to what extent they have the same percentage
    representation of each observation in the analysis profiles. Two pieces could theoretically
    have completely similar (shown as 0% dissimilar) analysis profileswhile still being different
    different pieces. This clustering process continues until all starting leaf nodes are clustered
    into one large group. The point of this type of analysis is to reveal latent structure in a
    dataset by showing how groups naturally form in the intermediary stages of clustering.

    All possible settings for the graph output have defaults. There are two sets of settings because
    the 'dendrogram_settings' get passed verbatim to the scipy function dendrogram(). For
    information about how these settings influence the dendrogram please see:
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html
    The 'graph_settings' consist of all other necessary settings to do cluster analysis and to
    produce a dendrogram. Each setting does the following:

    :param label_connections: if true display the percent dissimilarity of each dendrogram connection
    :type label_connections: boolean, defaults to True
    :param connection_string: controls the appearance of the label_connections if they are activated.
        The first character sets the color from this choice of eight colors:
        http://matplotlib.org/api/colors_api.html
        The second character sets the shape of the connection points from this list:
        http://matplotlib.org/api/markers_api.html
        If an empty string is passed but label_connections is still True, the number of each reading
        will still appear, but it will not be accompanied by a dot.
    :type connection_string: string of 0, 1, or 2 (most typical) characters in length.
    :param linkage_type: controls how clusters are compared for closeness and can be set to 'average',
        wherein the average distance of each point in one cluster to every point in the other cluster
        is taken to determine the disimilarity of those two clusters; 'single' where the closest two
        elements of two clusters is taken as the dissimilarity reading of the two clusters; or
        'complete' which takes the most dissimilar reading of any two elements, one from each cluster,
        to determine the distance of two clusters.
    :type linkage_type: string
    :param xlabel: assigns string to xlabel. If you want no label, pass an empty string.
    :type xlabel: string
    :param ylabel: assings string to ylabel. If you want no label, pass an empty string.
    :type ylabel: string
    :param title: assings string to dendrogram title. If you want no title, pass an empty string.
    :type title: string
    :param filename_and_type: set this to a filename ending in .pdf or .png if you want to save a
        pdf or a png of the dendrogram.
    :type filename_and_type: None will not save a file. Otherwise a string with the filename followed
        by either .pdf or .png.
    """
    default_graph_settings = {
                              'label_connections': True,
                              'connection_string': 'ro',
                              'linkage_type': 'average',
                              'xlabel': 'Analyses',
                              'ylabel': 'Percent Dissimilarity',
                              'title': '',
                              'filename_and_type': None # .pdf and .png are the only possible formats
                              }

    default_dendrogram_settings = {
                                   'p': 30,
                                   'truncate_mode': None,
                                   'color_threshold': 40,
                                   'get_leaves': True,
                                   'orientation': 'top',
                                   'labels': None,
                                   'count_sort': False,
                                   'distance_sort': False,
                                   'show_leaf_counts': True,
                                   'no_plot': False,
                                   'no_labels': False,
                                   'color_list': None,
                                   'leaf_font_size': None,
                                   'leaf_rotation': None,
                                   'leaf_label_func': None,
                                   'no_leaves': False,
                                   'show_contracted': False,
                                   'link_color_func': None,
                                   'ax': None,
                                   'above_threshold_color': 'b'
                                   }

    def __init__(self, sers, weights=(1.0,), graph_settings=None, dendrogram_settings=None):
        """
        :param sers: List of at least 1 list of analyses. Each internal list contains one analysis
            profile per piece in the set being compared. This analysis profile should be a series
            with the frequency of the events as the values and the names of the events as the index.
            More than one such list can be provided if you want to cluster pieces according to
            multiple types of analytical metrics. In the case of multiple analysis metrics, there
            must be the same exact number of series in each internal list. Each type of analysis 
            will be weighted according to the float multiplier at its same index position in the
            weights argument. See the weights argument documentation for an example.
        :type sers: list of lists of pandas.Series
        :param weights: Tuple containing the float multipliers for each type of analysis you include
            in the sers argument. The position of the float multipliers must correspond to that of
            its relevant analysis in the sers argument. For example, if you want to cluster a set of
            3 pieces based on their the metrics of interval 2-grams and individual part durations
            with weights of .75 and .25 respectively, you would need to pass sers and weights
            arguments in this format:
            ******
            sers = [[series_of_piece1_2grams, series_of_piece2_2grams, series_of_piece3_2grams,],
                    [series_of_piece1_durations, series_of_piece2_durations, series_of_piece2_durations,]]
            weights = (.75, .25)
            ******
            Note also that the analyses in the internal lists in sers must be in the same order.
        :type weights: Tuple of floats. The lengths of sers and weights must be the same. The sum of
            the elements in weights must equal 1.0.
        :param graph_settings: All settings that are not directly passed to the dendrogram() method.
            See the HierarchicalClusterer documentation string for more details.
        :type graph_settings: Dictionary
        :param dendrogram_settings: Settings passed directly to the dendrogram() method. See:
            http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html
        :type dendrogram_settings: Dictionary
        """
        self._sers = sers
        if round(sum(weights), 3) != 1.0:
            raise RuntimeWarning('The sum of the elements in the weights argument should equal 1.0')
        if len(sers) != len(weights):
            raise RuntimeWarning('There should be the same number of types of analysis in the sers \
                argument as there are floats in the weights argument.')
        self._weights = weights

        self._graph_settings = HierarchicalClusterer.default_graph_settings.copy()
        if graph_settings is not None:
            for k in graph_settings.keys(): # Make sure the user didn't pass any erroneous settings in graph_settings.
                if k not in HierarchicalClusterer.default_graph_settings:
                    raise RuntimeWarning(k + ' is not a possible graph setting. Please consult our \
                                         documentation for the file dendrogram.py')
            self._graph_settings.update(graph_settings)

        self._dendrogram_settings = HierarchicalClusterer.default_dendrogram_settings.copy()
        if dendrogram_settings is not None:
            for k in dendrogram_settings.keys(): # Make sure the use didn't pass any erroneous settings in dendrogram_settings.
                if k not in HierarchicalClusterer.default_dendrogram_settings:
                    raise RuntimeWarning(k + ' is not a possible dendrogram setting. Please see the \
                                         scipy documentation for a list of valid settings: \
                                         http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html')
            self._dendrogram_settings.update(dendrogram_settings)

        # super(HierarchicalClusterer, self).__init__(sers, (1.0,), None, None) # What would this do and why doesn't it work?
    
    def pair_compare(self):
        """
        Determines the dissimilarity of each analysis pairing and puts them in a "matrix" which is
        the upper half of a permutation matrix. For example, if you want to do a hierarchical
        clustering analysis on four pieces, you will have 6 unique pairing which will each get a
        dissimilarity score. Here's an explanatory diagram of four pieces, A B C and D:
        ********************
        * | A | B | C | D  *
        *-|---|---|---|----*
        *A| x | 31| 22| 61 *
        *-|---|---|---|----*
        *B| x | x | 17| 80 *
        *-|---|---|---|----*
        *C| x | x | x | 44 *
        *-|---|---|---|----*
        *D| x | x | x | x  *
        ********************
        These similarities would be represented in the matrix as a list in this order:
        [31, 22, 61, 17, 80, 44]. These results show that pieces B and C are the most similar based
        on the metric analyzed given that they have the lowest dissimilarity score. By contrast B
        and D are the most dissimilar. The algorithm makes its calculations based on the percent
        representation of each observation in each piece, so issues arising from inequalities in
        length are minimized. Also, comparing A to B will get the same score as comparing B to A,
        which is why only the upper half of the dissimilarity matrix is needed.
        """
        numPieces = len(self._sers[0])
        comparisons = numPieces*(numPieces-1)/2
        matrix = [0]*comparisons
        for i in range(len(self._sers)): # The outer loop is what allows multiple metrics to be mixed
            position = 0
            for j, ser1 in enumerate(self._sers[i][:-1]):
                for k, ser2 in enumerate(self._sers[i][j+1:]):
                    combined = ser1.add(ser2, fill_value=0)
                    a_total = sum(ser1)
                    b_total = sum(ser2)
                    c_total = float(sum(combined))
                    percA = a_total/c_total # out of 1, not out of 100
                    percB = b_total/c_total
                    dissimilarity = 100.0
                    for n in combined.index: # Each n is the name of an n-grams
                        a_ideal = combined.at[n] * percA
                        b_ideal = combined.at[n] * percB
                        a_val, b_val = 0, 0
                        if n in ser1.index:
                            a_val = ser1.at[n]
                        if n in ser2.index:
                            b_val = ser2.at[n]
                        a_acc = 1 - abs(a_val - a_ideal)/combined.at[n]
                        b_acc = 1 - abs(b_val - b_ideal)/combined.at[n]
                        n_perc = combined.at[n]/c_total
                        dissimilarity -= a_acc * b_acc * n_perc * 100
                    matrix[position] += dissimilarity * self._weights[i]
                    position += 1
        return matrix

    def run(self):
        """
        Used to execute the pair_comparison() analysis and draw a dendrogram to visualize the results.
        :returns: A dendrogram in the form of an interactive pylab window, or saved as a pdf or a png.
        """
        if self._dendrogram_settings['labels'] is None: # If the user hasn't provided labels, generate number strings starting from 1.
            self._dendrogram_settings['labels'] = []
            for x in range(len(self._sers[0])):
                self._dendrogram_settings['labels'].append(str(x+1))
        # linkage() organizes the dissimilarity matrix into a plotable structure.
        linkage_matrix = linkage(self.pair_compare(), self._graph_settings['linkage_type'])
        # 'Dendrogram' will be the name of the window if self._dendrogram_settings['no_plot']==False
        plt.figure('Dendrogram') 

        d_data = dendrogram(linkage_matrix, **self._dendrogram_settings)
        if self._graph_settings['label_connections']: # Add connection annotations if the user asked for them
            for i, d in zip(d_data['icoord'], d_data['dcoord']):
                x = 0.5 * sum(i[1:3])
                y = d[1]
                plt.plot(x, y, self._graph_settings['connection_string'])
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -8),
                             textcoords='offset points',
                             va='top', ha='center')

        # Apply labels. If you want to omit a label, pass an empty string ''.
        plt.xlabel(self._graph_settings['xlabel'])
        plt.ylabel(self._graph_settings['ylabel'])
        plt.title(self._graph_settings['title'])

        if self._graph_settings['filename_and_type'] is not None:
            plt.savefig(self._graph_settings['filename_and_type'])

        if not self._dendrogram_settings['no_plot']:
            plt.show()



# import os
# import pandas as pd
# from vis.models.indexed_piece import IndexedPiece
# from vis.analyzers.indexers import interval, dissonance, metre, noterest, ngram, offset
# from vis.analyzers.experimenters import frequency
# from numpy import nan, isnan, array
# import numpy
# import six
# from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
# import time
# import pdb
# from music21 import converter, stream, expressions, note
# import array
# from vis.analyzers.indexers.noterest import indexer_func as nr_ind_func
# import multiprocessing as mp
# import matplotlib.pyplot as plt
# from scipy.cluster.hierarchy import dendrogram, linkage

# # get the path to the 'vis' directory
# import vis
# VIS_PATH = vis.__path__[0]

# pL = [
#         'Lassus_Duets/Lassus_1_Beatus_Vir.xml',        # Lassus Duos
#         'Lassus_Duets/Lassus_2_Beatus_Homo.xml',
#         'Lassus_Duets/Lassus_3_Oculus.xml',
#         'Lassus_Duets/Lassus_4_justus.xml',
#         'Lassus_Duets/Lassus_5_Expectatio.xml',
#         'Lassus_Duets/Lassus_6_Qui_Sequitur_Me.xml',
#         'Lassus_Duets/Lassus_7_Justi.xml',
#         'Lassus_Duets/Lassus_8_Sancti_mei.xml',
#         'Lassus_Duets/Lassus_9_Qui_Vult.xml',
#         'Lassus_Duets/Lassus_10_Serve_bone.xml',
#         'Lassus_Duets/Lassus_11_Fulgebunt_justi.xml',
#         'Lassus_Duets/Lassus_12_Sicut_Rosa.xml',

#         # 'Morley_Duets/1 Goe yee my canzonets.xml',      # Morley Duos
#         # 'Morley_Duets/2 When loe by break of morning.xml',
#         # 'Morley_Duets/3 Sweet nymph.xml',
#         # 'Morley_Duets/5 I goe before my darling.xml',
#         # 'Morley_Duets/6 La Girandola.xml',
#         # 'Morley_Duets/7 Miraculous loves wounding.xml',
#         # 'Morley_Duets/8 Lo heere another love.xml',
#         # 'Morley_Duets/11 Fyre and Lightning.xml',
#         # 'Morley_Duets/13 Flora wilt thou torment mee.xml',
#         # 'Morley_Duets/15 In nets of golden wyers.xml',
#         # 'Morley_Duets/17 O thou that art so cruell.xml',
#         # 'Morley_Duets/19 I should for griefe and anguish.xml',

#         # 'Josquin_Duets/Agnus Dei.xml',                  # Josquin Duos
#         # 'Josquin_Duets/Crucifixus.xml',
#         # 'Josquin_Duets/Et incarnatus est.xml',
#         # 'Josquin_Duets/Missa_Ad_Fugam_Sanctus_version_2_Benedictus.xml',
#         # 'Josquin_Duets/Missa_Ad_fugam_Sanctus_version_2_Pleni.xml',
#         # 'Josquin_Duets/Missa_Ad_fugam_Sanctus_version_2_Qui_venit.xml',
#         # 'Josquin_Duets/Missa_Allez_regretz_I_Sanctus_Pleni.xml',
#         # 'Josquin_Duets/Missa_Ave_maris_stella_Sanctus_Benedictus.xml',
#         # 'Josquin_Duets/Missa_Ave_maris_stella_Sanctus_Qui_venit.xml',
#         # 'Josquin_Duets/Missa_Pange_lingua_Sanctus_Benedictus.xml',
#         # 'Josquin_Duets/Missa_Pange_lingua_Sanctus_Pleni_sunt_celi.xml',
#         # 'Josquin_Duets/Qui edunt me.xml'
#         ]



# opera = float(len(pL))
# f_setts = {'quarterLength': 2.0, 'method':'ffill'}
# v_setts = {'quality': False, 'simple or compound': 'simple'}
# h_setts = {'quality': False, 'horiz_attach_later': True, 'simple or compound': 'compound'}
# n_setts = {'n': 2, 'horizontal': [('interval.HorizontalIntervalIndexer', '1')],
#             'vertical': [('interval.IntervalIndexer', '0,1')], 'mark_singles': False}





#     def pair_compare(self, sers):
#         t1 = time.time()
#         # pair_comparisons = {}
#         matrix = []
#         numPieces = len(sers)
#         comparisons = numPieces*(numPieces-1)/2.0
#         count = 0
#         for j, ser1 in enumerate(sers[:-1]):
#             for k, ser2 in enumerate(sers[j+1:]):
#                 combined = ser1.add(ser2, fill_value=0)
#                 a_total = sum(ser1)
#                 b_total = sum(ser2)
#                 c_total = float(sum(combined))
#                 percA = a_total/c_total # out of 1, not out of 100
#                 percB = b_total/c_total
#                 similarity = 0.0
#                 count += 1
#                 for n in combined.index: # Each n is the name of an n-grams
#                     a_ideal = combined.at[n] * percA
#                     b_ideal = combined.at[n] * percB
#                     a_val, b_val = 0, 0
#                     if n in ser1.index:
#                         a_val += ser1.at[n]
#                     if n in ser2.index:
#                         b_val += ser2.at[n]
#                     a_acc = 1 - abs(a_val - a_ideal)/combined.at[n]
#                     b_acc = 1 - abs(b_val - b_ideal)/combined.at[n]
#                     n_perc = combined.at[n]/c_total
#                     similarity += a_acc * b_acc * n_perc * 100
#                 # pair_comparisons[','.join((str(j+1), str(j+k+2)))] = 100 - similarity
#                 matrix.append(100 - similarity)
#             print '%d percent done with n-gram profile comparisons' % (count/comparisons*100)
#         t2 = time.time()
#         print 'Pair Comparisons took %f seconds.' % round((t2-t1), 2)
#         # self.pair_comparisons = pair_comparisons
#         self.matrix = matrix




# query = HierClus()
# sers = query.run_vis(pL, opera, f_setts, h_setts, v_setts, n_setts)
# query.pair_compare(sers)


# query.dendrogram_maker(query.matrix)
# pdb.set_trace()


# matrix = [38.194908723754992, 41.971036331759343, 40.454774502393484, 38.012251196774962, 34.468125960061528, 41.284686992694795, 39.847081394541263, 39.452435760076753, 41.713369963370042, 44.773058381012916, 39.110588129818993, 43.487427286255404, 43.171077659714044, 44.673507258734467, 41.144735606274203, 35.343750331498057, 41.718220211840269, 44.860157699443434, 42.676703702871414, 45.11315900021004, 41.916034333313668, 35.392825844666405, 40.822137778108136, 39.308470709728226, 39.884058842392179, 42.129784520472704, 45.202853753990063, 39.66468969398656, 37.847744450119947, 36.74332503434065, 37.018799885010793, 34.832995163877456, 33.780489809335862, 41.777478701438142, 39.732987180543532, 36.27793082338539, 38.041960811559768, 41.806033823079282, 40.266651338079853, 41.799420664805169, 46.80201056523731, 39.37950097768443, 40.622622327167754, 46.180448436150193, 48.672915888824953, 38.991350446428555, 34.547873212645925, 39.671344286514767, 36.04068047337288, 44.546588722725083, 41.07260122984114, 42.693031869610763, 41.331673472505301, 35.74298960219437, 43.88177452353505, 38.86854210367234, 42.343122413945935, 40.153502327206873, 48.182539682539598, 42.884369019418514, 40.940737833594994, 48.360126078708603, 41.279143475572077, 40.600668312499742, 43.44869387148789, 42.638547477866958]
# Lassus_titles = ['1: Beatus Vir', '2: Beatus Homo', '3: Oculus', '4: Justus', '5: Expectatio', '6: Qui sequitur me', '7: Justi', '8: Sancti mei', '9: Qui vult', '10: Serve bone', '11: Fulgebunt justi', '12: Sicut Rosa']

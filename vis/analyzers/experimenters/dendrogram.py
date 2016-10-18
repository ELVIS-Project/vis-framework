# Filename:               vis/analyzers/experimenters/dendrogram.py
# Purpose:                Experimenters related to hierarchical clustering.
#
# Copyright (C) 2015, 2016 Alexander Morgan
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
import pandas as pd
from vis.analyzers import experimenter
import subprocess
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt


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
    Note that if graph_settings['interactive_dendrogram'] == False and
    graph_settings['filename_and_type'] is None dendrogram_setting['no_plot'] will automatically be
    set to True. If neither of those two conditions obtain, dendrogram_settings['no_plot'] will
    automatically be set to False.

    The 'graph_settings' consist of all other necessary settings to do cluster analysis and to
    produce a dendrogram. Each setting does the following:

    :param label_connections: if True, display the percent dissimilarity of each dendrogram
        connection.
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
    :param interactive_dendrogram: controls whether or no to produce a matplotlib interactive
        dendrogram. This is similar to the dendrogram_settings['no_plot'] setting but because of the
        added rendering in the form of axis labels, label connection annotations, etc. this switch
        is also necessary. If you don't want to produce an interactive dendrogram set this to False.
        The matplotlib dendrogram window is "interactive" in that you can zoom in and alter other
        aspects of the graph unlike the .pdf and .png formats which are immutable.
    :type interactive_dendrogram: boolean
    :param filename_and_type: set this to a filename ending in .pdf or .png if you want to save a
        pdf or a png of the dendrogram. If you don't add either type but do include a filename, the
        default type is .png.
    :type filename_and_type: None will not save a file. Otherwise a string with the filename
        followed by either .pdf or .png.
    :param return_data: Return just the data of the connections. If you don't want to spend time
        rendering the dendrogram too then you should set graph_settings['label_connections']: False,
        graph_settings['interactive_dendrogram']: False, and graph_settings['filename_and_type']:
        None. Setting interactive_dendrogram to False and filename_and_type to None will
        automatically set dendrogram_settings['no_plot']:True. The settings return_data,
        interactive_dendrogram, and filename_and_type are all kept separate so that the user can
        theoretically produce an interactive dendrogram, a static file, and return the data of the
        output as well, though I can't imagine that anyone would actually want to do all three at
        the same time. Any combination of the three outputs is also possible.
    :type return_data: boolean
    """
    default_graph_settings = {
                              'label_connections': True,
                              'connection_string': 'ro',
                              'linkage_type': 'average',
                              'xlabel': 'Analyses',
                              'ylabel': 'Percent Dissimilarity',
                              'title': '',
                              'interactive_dendrogram': True,
                              'filename_and_type': None, # .pdf and .png (default) are the only possible formats
                              'return_data': False
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

    _UNEQUAL_SERS_WEIGHTS = 'There should be the same number of types of analysis in the sers argument as there are floats in the weights argument.'
    _UNEQUAL_ANALYSES = 'All internal lists in sers must be of the same length, i.e. include the same pieces in each analysis metric.'
    _INVALID_WEIGHTS = 'Each element of this tuple should be >=0 and <=1 and the sum of the elements in the weights argument should equal 1.0'
    _INVALID_GRAPH_SETTING = ' is not a valid graph setting. Please consult our documentation for the file dendrogram.py'
    _INVALID_DENDRO_SETTING = ' is not a valid dendrogram setting. Please see the scipy documentation for a list of valid settings: \
                                http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html'

    def __init__(self, sers, settings={}):
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
        if 'weights' in settings:
            weights = settings['weights']
        else:
            weights = (1.0,)
        if 'graph_settings' in settings:
            graph_settings = settings['graph_settings']
        else:
            graph_settings = None
        if 'dendrogram_settings' in settings:
            dendrogram_settings = settings['dendrogram_settings']
        else:
            dendrogram_settings = None
        
        if len(sers) != len(weights):
            raise RuntimeWarning(HierarchicalClusterer._UNEQUAL_SERS_WEIGHTS)
        if len(sers) > 1:
            for lyst in sers[1:]:
                if len(lyst) != len(sers[0]):
                    raise RuntimeWarning(HierarchicalClusterer._UNEQUAL_ANALYSES)
        if round(sum(weights), 3) != 1 or max(weights) > 1 or min(weights) < 0:
            raise RuntimeWarning(HierarchicalClusterer._INVALID_WEIGHTS)
        self._sers = sers
        self._weights = weights

        self._graph_settings = HierarchicalClusterer.default_graph_settings.copy()
        if graph_settings is not None:
            for k in graph_settings.keys(): # Make sure the user didn't pass any erroneous settings in graph_settings.
                if k not in HierarchicalClusterer.default_graph_settings:
                    raise RuntimeWarning(k + HierarchicalClusterer._INVALID_GRAPH_SETTING)
            self._graph_settings.update(graph_settings)

        self._dendrogram_settings = HierarchicalClusterer.default_dendrogram_settings.copy()
        if dendrogram_settings is not None:
            for k in dendrogram_settings.keys(): # Make sure the use didn't pass any erroneous settings in dendrogram_settings.
                if k not in HierarchicalClusterer.default_dendrogram_settings:
                    raise RuntimeWarning(k + HierarchicalClusterer._INVALID_DENDRO_SETTING)
            self._dendrogram_settings.update(dendrogram_settings)
        # Don't spend time rendering the graph if you're not going to produce visual output.
        if not self._graph_settings['interactive_dendrogram'] and self._graph_settings['filename_and_type'] is None:
            self._dendrogram_settings['no_plot'] = True
        else:
            self._dendrogram_settings['no_plot'] = False

        self._plotter_path = path.join(vis.__path__[0], 'scripts')

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
        # Notes from discussion with Gabriel: normalize each observation for the total of that
        # observation in the pair. Then calculate distance in n-dimensional space with n =
        # number of types of observations.
        numPieces = len(self._sers[0])
        comparisons = int(numPieces*(numPieces-1)/2)
        matrix = [0]*comparisons
        for i in range(len(self._sers)): # The outermost loop is what allows multiple metrics to be mixed
            position = 0
            df = pd.concat(self._sers[i], axis=1, ignore_index=True) # put all the analysis profiles in this metric in a dataframe
            df = df.replace(to_replace='NaN', value=0)
            df = df.div(list(df.sum())) # make the df show the percent out of 1 that each analysis observation is of its piece
            for j in df.columns[:-1]:
                for k in df.columns[j+1:]:
                    # get the percent out of 1 that each pair has in common for all observations
                    similarity = sum(list(map(min, df.iloc[:, j], df.iloc[:, k])))
                    # apply the weight assigned to this analysis metric and make percent out of 100
                    matrix[position] += (1 - similarity) * self._weights[i] * 100
                    position += 1 # keep track of which pair comparison we're going to next in case we need to come back for another metric
        return matrix

    def run(self):
        """
        Used to execute the pair_compare() analysis and render a dendrogram to visualize the
        results and/or return the data used to produce the dendrogram.
        :returns: A dendrogram in the form of an interactive pylab window, and/or saved as a pdf or
        a png, and/or the data used to produce the dendrogram.
        """
        if self._dendrogram_settings['labels'] is None: # If the user hasn't provided labels, generate number strings starting from 1.
            self._dendrogram_settings['labels'] = []
            for x in range(len(self._sers[0])):
                self._dendrogram_settings['labels'].append(str(x+1))
        # linkage() organizes the dissimilarity matrix into a plotable structure.
        linkage_matrix = linkage(self.pair_compare(), self._graph_settings['linkage_type'])
        if self._graph_settings['return_data']:
            d_data = dendrogram(linkage_matrix, **self._dendrogram_settings)
            return d_data
        if not self._dendrogram_settings['no_plot']:
            plt.figure('Dendrogram') 
            d_data = dendrogram(linkage_matrix, **self._dendrogram_settings)
            # Add connection annotations if the user asked for them
            if self._graph_settings['label_connections']:
                for i, d in zip(d_data['icoord'], d_data['dcoord']):
                    x = 0.5 * sum(i[1:3])
                    y = d[1]
                    plt.plot(x, y, self._graph_settings['connection_string'])
                    plt.annotate("%.3g" % y, (x, y), xytext=(0, -8), textcoords='offset points',
                                 va='top', ha='center')
            # Apply labels. If you want to omit a label, pass an empty string ''.
            plt.xlabel(self._graph_settings['xlabel'])
            plt.ylabel(self._graph_settings['ylabel'])
            plt.title(self._graph_settings['title'])
            # If the user provided a filepath, export as a .png (default) or .pdf.
            if self._graph_settings['filename_and_type'] is not None:
                plt.savefig(self._graph_settings['filename_and_type'])
            # If the user wants an interactive matplotlib dendrogram, make it.
            if self._graph_settings['interactive_dendrogram']:
                plt.show()
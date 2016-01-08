#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/analyzers/experimenters/barchart.py
# Purpose:                Experimenters that generate bar charts.
#
# Copyright (C) 2014 Christopher Antila
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
.. codeauthor:: Christopher Antila <christopher@antila.ca>

The experimenters in this module all generate bar charts. Currently the only class is
:class:`RBarChart`, which uses ``Rscript`` to run a script in the R programming language.
"""

# pylint: disable=pointless-string-statement

from os import path
import subprocess
import pandas
import vis
from vis.analyzers import experimenter


class RBarChart(experimenter.Experimenter):
    """
    Use ``Rscript`` to run a bar-chart-generating script in the R programming language.
    """

    RSCRIPT_PATH = '/usr/bin/Rscript'
    """
    Full pathname to the ``Rscript`` program. If this doesn't work on your system, you'll have a
    hard time getting :class:`RbarChart` to work.
    """

    OUTPUT_TYPES = ('eps', 'ps', 'tex', 'pdf', 'jpeg', 'tiff', 'png', 'bmp', 'svg')
    """
    R additionally supports the ``'wmf'`` format, which is for Windows only. However, since VIS
    will likely never run on Windows, and since Windows also supports all the other formats, we
    do not allow ``'wmf'`` in this experimenter.
    """

    possible_settings = ('pathname', 'column', 'type', 'token', 'nr_pieces')
    """
    Only the ``'pathname'`` setting is required. For default values, refer to the descriptions below
    and the values in :const:`default_settings`.

    :keyword str 'pathname': The pathname to use for the outputted file.
    :keyword str 'column': The column of the :class:`DataFrame` to choose for outputting. If the
        data you wish to include in the chart is not in the ``'freq'`` column, use this setting to
        determine which column is used instead.
    :keyword str 'type': The output type, chosen from :const:`OUTPUT_TYPES`.
    :keyword str 'token': The "token" to pass onto the bar chart script, telling it what type of
        object is being displayed. This should either be a string ending with ``'-gram'``, the
        word ``'interval'`` or ``'objects'``, which is the default. Refer to the note below.
    :keyword 'nr_pieces': The number of pieces whose results are represented in the outputted
        chart. If present, the R script uses this to write "for X pieces" in the chart's title.
        The default is ``None``, which does not include this statement.
    :type 'nr_pieces': str or int

    .. note:: About the ``'token'`` Setting.

        The ``'token'`` setting is modified and sent forward to the R script, which uses it to
        determine the type of object portrayed on the chart. If the token is set to ``'interval'``,
        the R script will print that "Intervals" are being displayed; if the token is set to a
        string ending with ``'-gram'``, the script will print that whatever-grams are being
        displayed; if the token is set to ``None``, the script will print that "Objects" are being
        displayed.
    """

    default_settings = {'column': 'freq', 'type': 'png', 'token': 'objects', 'nr_pieces': None}
    """
    Deafult values for the optional settings.
    """

    _MISSING_SETTINGS = 'RBarChart is missing a required setting.'
    _INVALID_TYPE = 'Invalid output type: {}'
    _RSCRIPT_FAILED = 'Error during call to R: {} (return code: {})'

    def __init__(self, index, settings=None):
        """
        :param index: The experimental results with which to make a bar chart. Either you must
            provide the ``'column'`` setting or the results must be in the ``'freq'`` column.
        :type index: :class:`pandas.DataFrame`

        :param dict settings: A dictionary with settings. You must include the ``'pathname'`` and
            ``'column'`` settings, while the others are optional.

        :raises: :exc:`RuntimeError` if required settings are not present.
        :raises: :exc:`RuntimeError` if given an invalid ``'type'`` setting.
        """

        # Check all required settings are present in the "settings" argument.
        if 'pathname' not in settings:
            raise RuntimeError(RBarChart._MISSING_SETTINGS)

        # Make sure 'type' is valid
        if 'type' in settings:
            if settings['type'] not in RBarChart.OUTPUT_TYPES:
                raise RuntimeError(RBarChart._INVALID_TYPE.format(settings['type']))

        self._settings = RBarChart.default_settings.copy()
        self._settings.update(settings)
        if self._settings['nr_pieces'] is not None:
        	self._settings['nr_pieces'] = str(self._settings['nr_pieces'])

        # set the path to the script
        self._r_bar_chart_path = path.join(vis.__path__[0], 'scripts', 'R_bar_chart.r')

        super(RBarChart, self).__init__(index, None)

    def run(self):
        """
        Produce the bar chart.

        :returns: The pathname of the outputted PNG file containing a bar chart.
        :rtype: string
        :raises: :exc:`RuntimeError` if the call to ``Rscript`` fails for any reason. The return
            code and command's output are included as the :attr:`RuntimeError.args[0]` attribute.
        """

        # properly set output paths
        stata_path = '{}.dta'.format(self._settings['pathname'])
        out_path = '{}.{}'.format(self._settings['pathname'], self._settings['type'])

        # set the token
        if self._settings['token'].endswith('-gram'):
            token = self._settings['token'][:self._settings['token'].find('-gram')]
        elif 'interval' == self._settings['token'].lower():
            token = 'int'
        else:
            token = 'things'

        # if a column was given, we have to (effectively) change the column name for the R script
        if self._settings['column'] != RBarChart.default_settings['column']:
            self._index = pandas.DataFrame({'freq': self._index[self._settings['column']]})

        # run relevant filters then save the DataFrame
        self._index.to_stata(stata_path)

        # prepare the call for subprocess
        if self._settings['nr_pieces'] is None:
            call_to_r = [RBarChart.RSCRIPT_PATH, '--vanilla', self._r_bar_chart_path, stata_path,
                        out_path, token]
        else:
            call_to_r = [RBarChart.RSCRIPT_PATH, '--vanilla', self._r_bar_chart_path, stata_path,
                        out_path, token, self._settings['nr_pieces']]

        # do the actual call to Rscript
        try:
            subprocess.check_output(call_to_r)
        except subprocess.CalledProcessError as cpe:
            raise RuntimeError(RBarChart._RSCRIPT_FAILED.format(cpe.output, cpe.returncode))

        return out_path

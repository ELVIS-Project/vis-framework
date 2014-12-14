#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/tests/test_barchart.py
# Purpose:                Tests for the "barchart" experimenter module.
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
"""Tests for the "barchart" experimenters."""

# allow "too many public methods" for TestCase
# pylint: disable=too-many-public-methods
# pylint: disable=protected-access

import os
import subprocess
import unittest
import six
if six.PY3:
    from unittest import mock
else:
    import mock
import pandas
import vis
from vis.analyzers.experimenters import barchart


class TestRBarChart(unittest.TestCase):
    """Tests for the barchart.RBarChart experimenter."""

    def test_init_1(self):
        """That __init__() initializes properly."""
        # NB: this test temporarily changes vis.__path__ to a predictable result, so we can ensure
        #     __init__() uses it correctly
        setts = {'pathname': 'so_path', 'type': 'svg', 'token': '4-gram', 'nr_pieces': 12}
        some_df = 'I am a DataFrame'
        actual_vis_path = vis.__path__  # save the actual __path__
        vis.__path__ = ['directory']  # replace with our __path__
        exp_chart_path = os.path.join(vis.__path__[0], 'scripts', 'R_bar_chart.r')

        exp = barchart.RBarChart(some_df, setts)

        vis.__path__ = actual_vis_path  # restore vis.__path__
        self.assertEqual(setts['pathname'], exp._settings['pathname'])
        self.assertEqual(setts['type'], exp._settings['type'])
        self.assertEqual(setts['token'], exp._settings['token'])
        self.assertEqual(str(setts['nr_pieces']), exp._settings['nr_pieces'])
        self.assertEqual(exp_chart_path, exp._r_bar_chart_path)

    def test_init_2(self):
        """That __init__() raises RuntimeError when 'pathname' isn't given."""
        setts = {'type': 'svg', 'token': '4-gram', 'nr_pieces': 12}
        some_df = 'I am a DataFrame'
        self.assertRaises(RuntimeError, barchart.RBarChart, some_df, setts)
        try:
            barchart.RBarChart(some_df, setts)
        except RuntimeError as runerr:
            self.assertEqual(barchart.RBarChart._MISSING_SETTINGS, runerr.args[0])

    def test_init_3(self):
        """That __init__() raises RuntimeError when 'type' is invalid."""
        setts = {'pathname': 'goof', 'type': 'html', 'token': '4-gram', 'nr_pieces': 12}
        some_df = 'I am a DataFrame'
        self.assertRaises(RuntimeError, barchart.RBarChart, some_df, setts)
        try:
            barchart.RBarChart(some_df, setts)
        except RuntimeError as runerr:
            self.assertEqual(barchart.RBarChart._INVALID_TYPE.format(setts['type']), runerr.args[0])

    @mock.patch('vis.analyzers.experimenters.barchart.pandas.DataFrame')
    @mock.patch('vis.analyzers.experimenters.barchart.subprocess.check_output')
    def test_run_1(self, mock_subpro, mock_df):
        """
        That run() works properly.
        - token: '4-gram'
        - nr_pieces: '12'
        - column: 'the Brahms column'
        """
        # NB: this test temporarily changes vis.__path__ to a predictable result, so we can ensure
        #     __init__() uses it correctly
        setts = {'pathname': 'so_path', 'type': 'svg', 'token': '4-gram', 'nr_pieces': 12,
                 'column': 'the Brahms column'}
        some_df = {'the Brahms column': 'some FAF Series', 'the Raisin column': 'some bread Series'}
        new_df = mock.MagicMock()
        mock_df.return_value = new_df
        actual_vis_path = vis.__path__  # save the actual __path__
        vis.__path__ = ['directory']  # replace with our __path__
        expected = '{}.{}'.format(setts['pathname'], setts['type'])
        expected_call = [barchart.RBarChart.RSCRIPT_PATH, '--vanilla',
                         os.path.join(vis.__path__[0], 'scripts', 'R_bar_chart.r'),
                         '{}.{}'.format(setts['pathname'], 'dta'), expected, '4', '12']

        actual = barchart.RBarChart(some_df, setts).run()

        vis.__path__ = actual_vis_path  # restore vis.__path__
        self.assertEqual(expected, actual)
        mock_subpro.assert_called_once_with(expected_call)
        new_df.to_stata.assert_called_once_with('{}.{}'.format(setts['pathname'], 'dta'))

    @mock.patch('vis.analyzers.experimenters.barchart.subprocess.check_output')
    def test_run_2(self, mock_subpro):
        """
        That run() reacts properly to a CalledProcessError.
        - token: 'interval'
        - nr_pieces: not given
        - type: 'pdf'
        """
        # NB: this test temporarily changes vis.__path__ to a predictable result, so we can ensure
        #     __init__() uses it correctly
        setts = {'pathname': 'so_path', 'type': 'pdf', 'token': 'interval'}
        some_df = mock.MagicMock(auto_spec=pandas.DataFrame())
        actual_vis_path = vis.__path__  # save the actual __path__
        vis.__path__ = ['directory']  # replace with our __path__
        expected = '{}.{}'.format(setts['pathname'], setts['type'])  # NB: we don't expect it though
        expected_call = [barchart.RBarChart.RSCRIPT_PATH, '--vanilla',
                         os.path.join(vis.__path__[0], 'scripts', 'R_bar_chart.r'),
                         '{}.{}'.format(setts['pathname'], 'dta'), expected, 'int']
        # parameters set the_cpe.returncode, .cmd, and .output
        the_cpe = subprocess.CalledProcessError(42, 'false_command', 'Such a bad command!')
        mock_subpro.side_effect = the_cpe
        exp_err_msg = barchart.RBarChart._RSCRIPT_FAILED.format(the_cpe.output, the_cpe.returncode)

        # ensure the error is raised
        self.assertRaises(RuntimeError, barchart.RBarChart(some_df, setts).run)

        vis.__path__ = actual_vis_path  # restore vis.__path__
        #mock_subpro.check_output.assert_called_once_with(expected_call)
        mock_subpro.assert_called_once_with(expected_call)

        # ensure the right message is given
        try:
            barchart.RBarChart(some_df, setts).run()
        except RuntimeError as err:
            self.assertEqual(exp_err_msg, err.args[0])

    @mock.patch('vis.analyzers.experimenters.barchart.subprocess.check_output')
    def test_run_3(self, mock_subpro):
        """
        That run() works properly.
        - token: not given
        - nr_pieces: '4000'
        """
        # NB: this test temporarily changes vis.__path__ to a predictable result, so we can ensure
        #     __init__() uses it correctly
        setts = {'pathname': 'so_path', 'type': 'svg', 'nr_pieces': 4000}
        some_df = mock.MagicMock(auto_spec=pandas.DataFrame())
        actual_vis_path = vis.__path__  # save the actual __path__
        vis.__path__ = ['directory']  # replace with our __path__
        expected = '{}.{}'.format(setts['pathname'], setts['type'])
        expected_call = [barchart.RBarChart.RSCRIPT_PATH, '--vanilla',
                         os.path.join(vis.__path__[0], 'scripts', 'R_bar_chart.r'),
                         '{}.{}'.format(setts['pathname'], 'dta'), expected, 'things', '4000']

        actual = barchart.RBarChart(some_df, setts).run()

        vis.__path__ = actual_vis_path  # restore vis.__path__
        self.assertEqual(expected, actual)
        mock_subpro.assert_called_once_with(expected_call)


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
R_BAR_CHART_SUITE = unittest.TestLoader().loadTestsFromTestCase(TestRBarChart)

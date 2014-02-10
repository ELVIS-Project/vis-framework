#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               scripts/R_bar_chart.r
# Purpose:                Use ggplot2 in R to produce a bar chart.
#
# Copyright (C) 2013 Christopher Antila
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
#------------------------------------------------------------------------------

# This program produces a bar chart from a Stata file.
#
# Call it like this:
#     ./R_bar_chart.r <stata_path> <png_path> <token> <pieces>
#
# The arguments:
# - stata_path: path to a Stata-format with results to plot
# - png_path: where to write the PNG-format chart
# - token: (optional) the type of object being plotted (see "Tokens" below)
# - pieces: (optional)  the number of pieces included in these results
#
# Tokens:
# - "int": meaning the data is Intervals
# - a number: meaning the data is n-grams where "n" is the number
# - "things": meaning the data is something else
#
# NOTE: the y-axis label is always "Frequency"

library('ggplot2')
library('foreign')

# fetch commandline arguments and load the data for plotting
args <- commandArgs(TRUE)
R.test.results <- read.dta(args[1])

# choose x-axis label
if (is.na(args[3])) x_label <- 'Object' else
    if ('int' == args[3]) x_label <- 'Interval' else
        if ('things' == args[3]) x_label <- 'Object' else
            x_label <- paste(args[3], '-Gram', sep='')

# choose the title
if (is.na(args[4])) chart_title <- paste(x_label, ' Frequency', sep='') else
    if ('1' == args[4]) chart_title <- paste(x_label, ' Frequency for One Piece', sep='') else
        chart_title <- paste(x_label, ' Frequency for ', args[4], ' Pieces', sep='')

# pluralize the x-axis label
x_label <- paste(x_label, 's', sep='')

# generate the bar chart
the_chart <- ggplot() +
geom_bar(aes(x=reorder(index, freq, function(x) x * -1), y=freq),
    data=R.test.results,
    stat="identity",
    colour = '#53869b',
    fill = '#53869b') +
scale_x_discrete(x_label) +
scale_y_continuous("Frequency") +
labs(title = chart_title) +
theme(axis.text.x = element_text(angle=90, vjust=0.5))

# save the bar chart
ggsave(args[2], plot=the_chart, width=7, height=7)

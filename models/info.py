#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: models/info.py
# Purpose: Holds the VisInfo class, which contains general useful information.
#
# Copyright (C) 2012 Jamie Klassen, Christopher Antila
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
Holds the VisInfo class, which contains general useful information.
"""
from conf import VIS_VERSION

class VisInfo(object):
   def __init__(self):
      self.title = "Information about vis"
      self.copyright = """
      <html>
      <head/>
      <body>
         <p>
            <span style=\" text-decoration: underline;\">vis {0}</span>
         </p>
         <p>
            Copyright (c) 2012, 2013 Christopher Antila, Jamie Klassen, Alexander Morgan
         </p>
         <p>
            This program is free software: you can redistribute it and/or modify<br/>it under
             the terms of the GNU General Public License as published by<br/>the Free Software
              Foundation, either version 3 of the License, or<br/>(at your option) any later
               version.
         </p>
         <p>
            This program is distributed in the hope that it will be
             useful,<br/>but WITHOUT ANY WARRANTY; without even the implied warranty
              of<br/>MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the<br/>GNU
               General Public License for more details.
         </p>
         <p>
            You should have received a copy
             of the GNU General Public License<br/>along with this program. If not, see
              &lt;http://www.gnu.org/licenses/&gt;.
         </p>
      </body>
      </html>
      """.format(VIS_VERSION)
      self.about = """
      <html>
      <head/>
      <body>
      <p>
         vis was written as part of McGill University\'s contribution to the ELVIS
          project.<br/>For more information about ELVIS, please refer to our 
          <a href=\"http://elvis.music.mcgill.ca/\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               web site
            </span>
         </a>.
      </p>
      <p>
         Funding for ELVIS was provided by the following organizations:<br/>- SSHRC (Social
          Sciences and Humanities Research Council) of Canada<br/>- NEH (National Endowment for
           the Humanities) of the United States of America<br/>- The Digging into Data
            Challenge
      </p>
      <p>
         vis is written in the Python programming language, and relies on the
          following<br/>software, all released under free licences:<br/>
         - <a href=\"http://mit.edu/music21/\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               music21<br/>
            </span>
         </a>
         - <a href=\"http://www.riverbankcomputing.co.uk/software/pyqt/download\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               PyQt4
            </span>
         </a>
         <br/>
         - <a href=\"http://www.oxygen-icons.org/\">
            <span style=\" text-decoration: underline; color:#0057ae;\">
               Oxygen Icons
            </span>
         </a>
      </p>
      </body>
      </html>
      """

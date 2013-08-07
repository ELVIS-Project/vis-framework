#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/indexed_piece.py
# Purpose:                Hold the model representing an indexed and analyzed piece of music.
#
# Copyright (C) 2013 Christopher Antila, Jamie Klassen
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
The model representing an indexed and analyzed piece of music.
"""

# Imports
from importlib import import_module
from inspect import getmembers, isdatadescriptor
import pkgutil
import re
import os
from music21 import converter
from vis.analyzers import indexers
from vis.analyzers import indexer


class IndexedPiece(object):
    """
    Holds the indexed data from a musical score.
    """

    # About the Data Model (for self._data)
    # =====================================
    # - All the indices are stored in a dict.
    # - Indices of the dict will be unicode()-format class names of the Indexer.
    # - how can we store multiple results from the same Indexer, generated with different settings?

    # - For an Indexer, the stored item will be a dict of pandas.Series objects.
    #    - Access a particular index by specifying the Indexer name, the settings, and either the
    #      index of the part in the Score object or a list of parts in a part combination.
    #      Examples:
    #      - self._data[u'NoteRestIndexer'][u'{}'][0]
    #         Notes-and-rests index of the highest part; Indexer has no settings.
    #         NB: since this is a single-part reference, it is a list. Indices are integers.
    #      - self._data[u'IntervalIndexer']
    #                  [u'{u'quality': False, u'simple or compound': u'simple'}']
    #                  [u'[0, 1]']
    #         Intervals index of the two highest parts.
    #         NB: since this lists part combinations, it is a dict. Indices are list-like strings.
    #    - Be aware that settings can be tricky to deal with, since a dict object does not always
    #      present its keys to str() in the same order. The only way to know whether specific
    #      settings are present in an IndexedPiece is to eval() the settings strings and compare
    #      them to another settings dict.
    #    - Each of the objects you get is a pandas.Series, where:
    #      - each element is an instance music21.base.ElementWrapper
    #      - each element has an "offset" corresponding to its place in the score
    #      - each element has its proper "duration" attribute

    # - For an Experimenter, results are stored in the same way as for an Indexer.
    #   There are two differences:
    #   - There is an additional part specification: u'all'. This may appear alongside or instead
    #     of other parts or part combinations.
    #   - The Experimenter's output may be either a pandas.Series or pandas.DataFrame.

    class Metadata:
        # TODO: docs
        def __init__(self, **kwargs):
            # TODO: docs
            data = {
                'pathname': None,
                'parts': None,
                'anacrusis': None,
                'alternative_title': None,
                'composer': None,
                'composers': None,
                'date': None,
                'locale_of_composition': None,
                'movement_name': None,
                'movement_number': None,
                'number': None,
                'opus_number': None,
                'title': None
            }
            data.update(kwargs)
            self.__dict__.update(data)

    def __init__(self, pathname):
        # TODO: docs
        super(IndexedPiece, self).__init__()
        self._metadata = self.__class__.Metadata(pathname=pathname)
        self._data = {}
        self._score = None
        self.indexers = []
        self._imported = False

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def __unicode__(self):
        pass

    def _import_score(self):
        """
        Import the score to music21 format. Uses multiprocessing, but blocks until the import is
        complete.

        Returns
        =======
        music21.stream.Score or Opus
            The score.
        """
        # TODO: actually write this method
        score = converter.parse(self.metadata('pathname'))
        if not self._imported:
            def convert(name):
                """
                converts camelCase strings (as properties in music21 are named) to snake-case
                strings (which are what Python idiom dictates we should use)

                Taken from :
                http://stackoverflow.com/
                questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
                :param name: a camelCase string
                :return: a snake-case string
                """
                s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
                return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
            # find all the properties (i.e. methods with the @property decorator)
            # for music21.metadata.Metadata which are also in our Metadata prototype
            for name, obj in getmembers(score.metadata.__class__, isdatadescriptor):
                if isinstance(obj, property) and hasattr(self._metadata, convert(name)):
                    self.metadata(convert(name), obj)

            self._imported = True
            self.add_index([u'NoteRestIndexer'], {})
        return score

    def metadata(self, field, value=None):
        # TODO: update doctest so that it actually works (e.g. the piece must be imported before
        #       calling metadata)
        """
        Get or set metadata about the piece, like filename, title, and composer.

        :param str field: The name of the field to be accessed or modified

        :param value: If not None, the new value to be assigned to ``field``

        :type value: object or None

        :returns: object -- the field accessed, or None -- if assigning a field or attempting to
            access a field that does not exist..

        >>> piece = IndexedPiece('a_sibelius_symphony.mei')
        >>> piece.metadata('composer')
        u'Jean Sibelius'
        >>> piece.metadata('year', 1919)
        >>> piece.metadata('year')
        1919
        >>> piece.metadata('parts')
        [u'Flute 1', u'Flute 2', u'Oboe 1', u'Oboe 2', u'Clarinet 1', u'Clarinet 2', ... ]
        """
        if not isinstance(field, basestring):
            raise TypeError("parameter 'field' must be of type 'basestring'")
        if value is None:
            if hasattr(self._metadata, field):
                return getattr(self._metadata, field)
            else:
                if not self._imported:
                    self._import_score()
                    return self.metadata(field, value)
        else:
            setattr(self._metadata, field, value)

    def add_index(self, which_indexers, which_settings=None):
        """
        Run one or more :py:class:`controllers.indexer.Indexer`s on the score and save the results.
        If any of the :py:class:`controllers.indexer.Indexer`s have already been run with the same
        settings, they will not be run again.

        Access the result with :py:meth:`get_parts`.

        :param which_indexers:
            the :py:class:`controllers.indexer.Indexer` subclasses to run on the IndexedPiece. You
            may safely provide either a list of basestrings or a single basestring. You must write
            these as the module name and class, as found in the indexers directory. For example:
            - u'noterest.NoteRestIndexer'
            - u'interval.IntervalIndexer'
        :type which_indexers: list of (str or unicode) or (str or unicode)

        :param which_settings:
            A dict of the settings to provide the :py:class:`controllers.indexer.Indexer`. Default
            is {}. This is the same for all Indexers in "which_indexers", so you may specify
            settings that apply only to one or some of the Indexers, but you may not specify
            different settings of the same name for different Indexers.
        :type which_settings: dict

        :returns: None

        :raises: RuntimeError -- if one of the specified :py:class:`controllers.indexer.Indexer`s
            (or one of its requirements) cannot be located, or if a required setting for one of the
            :py:class:`controllers.indexer.Indexer`s is absent. The exception is raised but only
            for the :py:class:`controllers.indexer.Indexer`s with problems. The others run as
            normal.

        :raises: TypeError -- if one of the strings in `which_indexers` does not correspond to a
            subclass of :py:class:`controllers.indexer.Indexer`.
        """

        if not which_settings:
            which_settings = {}
        if not isinstance(which_indexers, list):
            which_indexers = [which_indexers]

        # If one of the indexers doesn't exist, add its name to this list.
        missing_indexers = []
        missing_settings = []

        # Hold the music21 Score object, if we use it
        the_score = None

        # If one of the indexers requires another indexer, we'll run it automatically. If the user
        # specifies pre-requisite indexers out of order (i.e., which_indexers is
        # [u'IntervalIndexer', u'NoteRestIndexer']), then we'll find the NoteRestIndexer is already
        # calculated, and skip it.
        for this_indexer in which_indexers:
            if not isinstance(this_indexer, (str, unicode)):
                raise TypeError('Indexer names must be string or unicode')
            if hasattr(indexer, this_indexer):
                indexer_cls = getattr(indexer, this_indexer)
            else:
                found = False
                s = this_indexer.split('.')
                # iterate through the directory of indexers
                for _, name, ispkg in pkgutil.iter_modules(indexers.__path__):
                    if not ispkg:
                        mod = import_module('.' + name, package=indexers.__package__)
                        if hasattr(mod, this_indexer):
                            indexer_cls = getattr(mod, this_indexer)
                            found = True
                            break
                    else:
                        # we have an add-on indexer
                        indexer_cls = s[-1]
                        pkg = __import__(indexers.__package__ + '.' + '.'.join(s[:-1]), fromlist=[indexer_cls])
                        if hasattr(pkg, indexer_cls):
                            indexer_cls = getattr(pkg, indexer_cls)
                            found = True
                            break
                if not found:
                    try:
                        indexer_cls = __import__(this_indexer)
                        for n in s[1:]:
                            indexer_cls = getattr(indexer_cls, n)
                    except (ImportError, AttributeError):
                        missing_indexers.append(this_indexer)
                        continue

            # Make a dict of the settings relevant for this Indexer
            # We'll check all the possible settings for this Indexer. If the setting isn't given by
            # the user, we'll use the default; if there is no default, we can't use the Indexer.
            if not issubclass(indexer_cls, indexer.Indexer):
                missing_indexers.append(this_indexer)
                continue
            poss_sett = indexer_cls.possible_settings
            if poss_sett is None:
                poss_sett = {}
            def_sett = indexer_cls.default_settings
            if def_sett is None:
                def_sett = {}
            this_settings = {}
            for sett in poss_sett:
                if sett in which_settings:
                    this_settings[sett] = which_settings[sett]
                elif sett in def_sett:
                    this_settings[sett] = def_sett[sett]
                else:
                    this_settings = u'spoiled'
                    break
            if u'spoiled' == this_settings:
                missing_settings.append(this_indexer)
                continue

            # Does the Indexer require the Score?
            required_score = []
            if indexer_cls.requires_score:
                if the_score is None:
                    the_score = self._import_score()
                required_score = list(the_score.parts)
                # TODO: what about imports to Opus objects?
                # TODO: find and store metadata
            else:
                req_ind = indexer_cls.required_indices
                self.add_index(filter(lambda ind: not ind in self._data, req_ind), which_settings)

            # Do we already have this index with the same settings?
            # NOTE: we must do this *after* the Score import. If our indexer_cls is NoteRestIndexer,
            # we'll have to import the Score, and if it wasn't already imported, the NRI will run
            # automatically, but we wouldn't know to return it.
            if this_indexer in self._data:
                # Is there an index with the same settings?
                for each_setts in self._data[this_indexer].iterkeys():
                    if eval(each_setts) == this_settings:
                        this_settings = u'found'
                        break
            if u'found' == this_settings:
                continue

            # Run the Indexer and store the results
            indexer_instance = indexer_cls(required_score, this_settings)
            if this_indexer not in self._data:
                self._data[this_indexer] = {}
            self._data[this_indexer][unicode(this_settings)] = indexer_instance.run()

            # Be explicit about memory
            del indexer_instance
            del this_settings

        # If one of the Indexers doesn't exist
        if missing_indexers:
            msg = u'Unable to import requested Indexers: ' + unicode(missing_indexers)
            raise RuntimeError(msg)
        # If one of the Indexers is missing a required setting
        elif missing_settings:
            msg = u'Indexers missing required settings: ' + unicode(missing_indexers)
            raise RuntimeError(msg)

    def remove_index(self, index):
        """
        To save on memory, or for some other reason like it's suddenly invalied, remove certain
        information from this IndexedPiece.

        You might want to do this, for example, after parsing chords from a piano texture.

        :param index: the index to remove.
        :type index: basestring
        :returns: None
        """
        remove_me = self._data.get(index, None)
        if not remove_me is None:
            del self._data[index]

    def add_experiment(self, which_experimenters, which_settings=None):
        """
        Run an experimenter (or some experimenters) on the score and save the results. If the
        experimenter has already been run with the same settings, the previously-calculated
        results are returned.

        This method checks whether the required indexers have been run. If not, they will be run
        now, and the indices saved in this object, but not returned.

        Parameters
        ==========
        :param which_experimenters: list
            A list of the vis.controllers.experimenter.Experimenter subclasses to run.

        :param which_settings: dict
            A dict of the settings to provide the Experimenter. Default is {}.

        Returns
        =======
        pandas.Series or pandas.DataFrame :
            The result produced by the Experimenter subclass.

        Raises
        ======
        RuntimeException :
            If "which_experimenters" refers to an unknown Experimenter subclass, or the Experimenter
            subclass raises an exception.

        Side Effects
        ============
        Results from the Indexer, and any additional Indexer subclasses required for the
        "which_index" Indexer subclass, are saved in the IndexedPiece.
        """
        if not which_settings:
            which_settings = {}

    def remove_experiment(self, **args):
        """
        To save on memory, or for some other reason like it's suddenly invalied, remove certain
        information from this IndexedPiece.

        You might want to do this, for example, after re-calculating an index on which an
        Experimenter depends, but which you do not wish to recalculate.
        """
        pass

    def get_index(self, index, settings=None):
        """
        Get a list of an index of specific parts.

        :param index:
            The name of the index you want, as provided to "add_index()". This is the string-wise
            representation of the Indexer class's name.
        :type index: basestring

        :param settings: A dictionary of settings for the index.
        :type settings: dict

        :returns: The specified index with the given settings.
        :rtype: pandas.Series

        :raises: RuntimeError -- If the index has not yet been calculated, or if the parts or
            part combinations are invalid (i.e., the part index does not exist in the
            IndexedPiece or the part combination has not been calculated for this index).

        >>> piece = IndexedPiece('test_corpus/bwv77.mxl')
        >>> piece.metadata('parts')
        [u'Soprano', u'Alto', u'Tenor', u'Bass']
        >>> piece.add_index(u'NoteRestIndexer')
        >>> piece.get_index(u'NoteRestIndexer')
        [<Series with Soprano NoteRestIndexer>, <Series with Bass NoteRestIndexer>, ...]
        """
        if not index in self._data:
            raise RuntimeError('the index {0!r} has not been calculated'.format(index))
        indices = self._data[index]
        if settings is None:
            if 1 == len(indices):
                return indices.values()[0]
            settings = u'{}'
        if not settings in indices.keys():
            msg = 'the index {0!r} has not been calculated with the given settings'.format(index)
            raise RuntimeError(msg)
        return self._data[index][settings]

    @staticmethod
    def _find_part_names(the_score):
        """
        Return a list of part names in a score. If the score does not have proper names, return a
        list of enumerated parts.

        Parameters
        ==========
        :param the_score:
            The score in which to find the part names.
        :type the_score: music21.stream.Score

        Returns
        =======
        :returns: The title of the score.
        :rtype: list of unicode
        """
        # hold the list of part names
        post = []

        # First try to find Instrument objects. If that doesn't work, use the "id"
        for each_part in the_score.parts:
            instr = each_part.getInstrument()
            if instr is not None and instr.partName != u'':
                post.append(unicode(instr.partName))
            else:
                post.append(unicode(each_part.id))

        # Make sure none of the part names are just numbers; if they are, use
        # a part name like "Part 1" instead.
        for part_index in xrange(len(post)):
            try:
                int(post[part_index])
                # if that worked, the part name is just an integer...
                post[part_index] = u'Part ' + unicode(part_index + 1)
            except ValueError:
                pass

        return post

    @staticmethod
    def _find_piece_title(the_score):
        """
        Find the title of a Score. If there is none, return the filename without extension.

        Parameters
        ==========
        :param the_score:
            The score of which to find the title.
        :type the_score: music21.stream.Score

        Returns
        =======
        :returns: The title of the score.
        :rtype: unicode
        """
        post = u''

        # First try to get the title from a Metadata object, but if it doesn't
        # exist, use the filename without directory.
        if the_score.metadata is not None:
            post = the_score.metadata.title
        elif hasattr(the_score, 'filePath'):
            post = os.path.basename(the_score.filePath)
        else:  # if the Score was part of an Opus
            post = u'Unknown Piece'

        # Now check that there is no file extension. This could happen either if
        # we used the filename or if music21 did a less-than-great job at the
        # Metadata object.
        post = os.path.splitext(post)[0]

        return post

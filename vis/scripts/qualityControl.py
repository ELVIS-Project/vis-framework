from music21 import converter
from vis.analyzers.indexers import meter

convert_error = 'This piece could not be converted by music21.'
no_parts = 'This piece appears to have no parts.'
no_measures = 'This piece has at least one part, but no measures.'
only_one_part = 'This piece only has one part in its encoding so this check cannot be performed.'
uneven_measures = 'This piece\'s parts change measures at different offsets.'
passing_message = 'This piece was successfully converted and passed the measure-integrity test.'

class QualityControl(object):
    """
    Contains basic checks to see if a piece symbolic notation is probably notated correctly. Note 
    that there is no guarantee that all encoding mistakes will be found and this currently only 
    offers checks for the most egregious errors. These checks are intended for the SIMSSA Database. 
    Here's a sample of how to use this class to check the integrity of a piece's encoding. "Result" 
    will contain measure_checker()'s 2-tuple return value:

    >>> test = QualityControl()
    >>> result = test.measure_checker(path_to_piece_in_symbolic_notation)
    """
    def check_convert(self, path):
        """
        Makes sure that the piece passed can be converted by music21.

        returns: A 2-tuple of (True, list_of_piece's_parts) if the conversion was successfully 
            imported by music21, or a 1-tuple (False,) if the conversion failed.
        """
        try:
            piece = converter.parse(path)
            parts = piece.parts
            return (True, parts)
        except:
            return (False,)

    def measure_checker(self, path):
        """
        Makes sure that the different parts of the piece passed change measures at the same offsets. 
        There are some piece for which this is not the case, but this check is meant to identify 
        mistakes of this nature as the vast majority (if not all) of the pieces in the SIMSSA 
        Database should have parts that change measures at the same exact offsets.

        returns: A 2-tuple consisting of the boolean result of the test (True means the test was 
            passed or in the case of a 1-voice piece, not performable; False means the test was 
            failed) and a string containing a brief message explaining the result of the test.
        """
        temp = self.check_convert(path)
        if not temp[0]:
            return (False, convert_error)
        test_parts = temp[1]
        measures = meter.MeasureIndexer(test_parts).run()
        cols = len(measures.columns)
        if cols == 0:
            return (False, no_parts)
        elif path[-3:] not in ('mid', 'idi') and cols > 0 and len(measures.index) == 0:
            return (False, no_measures)
        elif cols == 1:
            return (True, only_one_part)
        else:
            first_col_vals = measures.iloc[:, 0].tolist()
            for col_num in range(1, cols):
                if first_col_vals != measures.iloc[:, col_num].tolist():
                    return (False, uneven_measures)
        return (True, passing_message)


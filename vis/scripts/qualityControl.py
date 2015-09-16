from vis.models.indexed_piece import IndexedPiece
from vis.analyzers.indexers import metre

no_parts_warning = 'This piece appears to have no parts.'
only_one_part = 'This piece only has one part in its encoding so this check cannot be performed.'
uneven_measures = 'This piece\'s parts change measures at different offsets.'
passing_message = 'This piece passed the measure-integrity test.'

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
        ind_piece = IndexedPiece(path)
        test_piece = ind_piece._import_score()
        test_parts = test_piece.parts
        measures = metre.MeasureIndexer(test_parts).run()
        cols = len(measures.columns)
        if cols == 0:
            return (False, no_parts_warning)
        elif cols == 1:
            return (True, only_one_part)
        else:
            first_col_vals = measures.iloc[:, 0].tolist()
            for col_num in range(1, cols):
                if first_col_vals != measures.iloc[:, col_num].tolist():
                    return (False, uneven_measures)
        return (True, passing_message)


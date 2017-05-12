_MAJOR = 3
_MINOR = 1
_PATCH = 0
__version__ = '{}.{}.{}'.format(_MAJOR, _MINOR, _PATCH)

# Easy way to get items from the built-in corpus
import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_corpus(path):
	"""
	Function to access built-in corpus.
	"""
    return os.path.join(_ROOT, 'corpus', path)
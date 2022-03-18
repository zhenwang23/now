import os as _os
import sys as _sys

__version__ = '0.0.1'
__resources_path__ = _os.path.join(
    _os.path.dirname(_sys.modules['src'].__file__), 'resources'
)

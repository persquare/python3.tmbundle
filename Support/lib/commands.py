import os
import sys

try:
    helper = os.path.join(os.environ['TM_PYTHON_HELPERS_BUNDLE_SUPPORT'], 'lib')
    if helper not in sys.path:
        sys.path[:0] = [helper]
except:
    errmsg = """
    The PythonHelpers bundle required, see<br/>
    <a href=https://github.com/persquare/PythonHelpers.tmbundle>
    github.com/persquare/PythonHelpers.tmbundle
    </a>
    """
    sys.stderr.write(errmsg)
    sys.exit(205)


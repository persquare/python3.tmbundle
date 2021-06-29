import os
import sys

try:
    import jedi
except:
    # Required module Jedi not installed, provide some helpful feedback.
    errmsg = """
    Jedi module is required, see<br/>
    <a href=https://pypi.org/project/jedi/>https://pypi.org/project/jedi/</a>
    """
    sys.stderr.write(errmsg)
    sys.exit(205)


def _get_line_column():
    line = os.environ['TM_LINE_NUMBER']
    col = os.environ['TM_COLUMN_NUMBER']
    return (int(line), int(col)-1)

def _get_script():
    """ Get the Jedi script object from the source passed on stdin"""
    source = sys.stdin.read()
    path = os.environ.get('TM_FILE_PATH')
    script = jedi.Script(code=source, path=path)
    return script

def _find_def(prev):
    import operator
    cmp_op = operator.lt if prev else operator.gt
    goto_line = 0 # There is no line zero, so use this as a bail-indicator
    try:
        line, col = _get_line_column()
    except:
        # Bail as there is no pure cursor
        # FIXME: Go through some hoops to figure out cursor location.
        return goto_line
    script = _get_script()
    context = script.get_context(line, col)
    current_line = context.line if context.type in ('class', 'function') else line
    defs = [d for d in script.get_names() if d.type in ('class', 'function')]
    for d in defs:
        if cmp_op(d.line, current_line):
            goto_line = d.line
            break

    return goto_line

def prev_def():
    return _find_def(prev=True)

def next_def():
    return _find_def(prev=False)

def completions():
    """Return a list of completion alternatives"""
    try:
        line, col = _get_line_column()
    except:
        # Bail as there is no pure cursor
        # FIXME: Go through some hoops to figure out cursor location.
        return []
    script = _get_script()
    completions = script.complete(line, col)
    return [c.name for c in completions]

def quickdoc():
    """Return a list with short docs"""
    try:
        line, col = _get_line_column()
    except:
        # Bail as there is no pure cursor
        # FIXME: Go through some hoops to figure out cursor location.
        return []
    script = _get_script()
    definitions = script.help(line, col)
    return [definition.docstring() for definition in definitions]


# if __name__ == '__main__':
#     help = quickdoc()
#     sys.stderr.write("\n\n".join(help))
#     sys.exit(205)





#!/usr/bin/env python3
# encoding: utf-8

"""
This module generates documentation for a TextMate bundle by parsing the .tmCommand files.
FIXME: The formatting is slightly messed up (underlined links, extra table header, etc.)
FIXME: Also parse bash/ruby/perl scripts for docstring equivalents
FIXME: List tab-triggers
"""

import os
import re
import json
from subprocess import Popen, PIPE

class TableBuilder(object):
    def __init__(self, *args):
        super(TableBuilder, self).__init__()
        self.headings = args
        self.rows = []

    def add_row(self, *args):
        self.rows.append(args)

    def render(self):
        lines = []
        lines.append(self._preamble())
        lines.append(self._heading())
        for contents in self.rows:
            lines.append(self._row(contents))
        lines.append(self._postamble())
        return '\n'.join(lines)


    def _preamble(self):
        return ''

    def _postamble(self):
        return ''

    def _heading(self):
        return ' '.join(['{}'.format(x) for x in self.headings])

    def _row(self, items):
        return ' '.join(['{}'.format(x) for x in items])


class HTMLTable(TableBuilder):
    """docstring for HTMLTable"""
    def _preamble(self):
        return '<table>'

    def _postamble(self):
        return '</table>\n\n'

    def _heading(self):
        return '<tr>' + ''.join(['<th>{}</th>'.format(x) for x in self.headings]) + '</tr>'

    def _row(self, items):
        return '<tr>' + ''.join(['<td>{}</td>'.format(x) for x in items]) + '</tr>'




def parse_keycode(keycode):
    # a => A
    # A => ⇧A
    # ~ => ⌥
    # ^ => ⌃
    # @ => ⌘
    # $ ⌅ ⎋ ⇥
    # *
    mappings = {
        '~':'⌥',
        '^':'⌃',
        '@':'⌘',
        '\x0A':'↩',
        '\x09':'⇥',
        '\x1B':'⎋',
        ' ':'␣'
    }
    printable = []
    shifted = False
    keycode = list(keycode)
    key = keycode.pop() # .decode('utf-8')
    key = mappings.get(key, key)
    printable.append(key.upper())
    if key >= 'A' and key <= 'Z':
        shifted = True

    while keycode:
        key = keycode.pop() # .decode('utf-8')
        printable.append(mappings.get(key, '¿'))

    if shifted:
        printable.append('⇧')

    printable.reverse()

    return printable

def commandlist(cmd_dir):

    def json_from_plist(path):
        try:
            p = Popen(['plutil', '-convert', 'json', path, '-o', '-'], stdout=PIPE, stderr=PIPE)
            res, err = p.communicate()
            return json.loads(res) if not err else {}
        except:
            return {}

    commands = [];
    for f in os.listdir(cmd_dir):
        path = os.path.join(cmd_dir, f)
        pl = json_from_plist(path)
        if not pl or pl.get('isDisabled', False):
            continue
        raw_combo = pl.get('keyEquivalent', '')
        name = pl.get('name', 'NONAME')
        docstring = extract_docstring(pl.get('command', ''))
        commands.append((raw_combo, name, docstring))

    return commands

def extract_docstring(string):
    LANG = r'^#!.+[/|\s+]([a-z]+)'
    match = re.match(LANG, string)
    if not match:
        return ''
    lang = match.group(1)
    if lang == 'python':
        return extract_python_docstring(string)
    elif lang in ['ruby', 'bash', 'sh']:
        return extract_comment_docstring(string)
    else:
        return ''

def extract_python_docstring(string):
    DOCSTRING = r'\s*#!.+?python.*?"""(.*?)"""'
    match = re.match(DOCSTRING, string, re.DOTALL)
    return match.group(1) if match else ''

def extract_comment_docstring(string):
    DOCSTRING = r'#!.+\n\n((?:\s*#.*\n)+)'
    match = re.match(DOCSTRING, string, re.MULTILINE)
    if not match:
        return ''
    lines = [line.lstrip('# \t') for line in match.group(1).split('\n')]
    return '\n'.join(lines)

def generate_keyboard_shortcut_docs(cmd_dir):
    # Auto-generate keyboard shortcut list
    tb = HTMLTable('Keys', 'Command', 'Comment')
    cmds = commandlist(cmd_dir)
    for (raw_combo, cmd_name, docstring) in cmds:
        if not raw_combo:
            continue
        combo = parse_keycode(raw_combo)
        combo_str = ''.join(combo)
        if not combo_str.strip():
            continue
        tb.add_row(combo_str, cmd_name, docstring)
    return tb.render()

def help_for_bundle():
    cmd_dir = os.path.join(os.environ['TM_BUNDLE_SUPPORT'], '../Commands')
    helptext = generate_keyboard_shortcut_docs(cmd_dir)
    return helptext





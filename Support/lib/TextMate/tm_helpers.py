#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
tm_helpers.py

A collection of useful helper functions and classes for writing
commands in Python for TextMate.
"""

import subprocess
import shlex
import re

def sh_escape(s):
    """ Escape `s` for the shell. """
    return re.sub(r"(?=[^a-zA-Z0-9_.\/\-\x7F-\xFF\n])", r'\\', s).replace("\n", "'\n'")


def sh(cmd):
    """ Execute `cmd` and capture stdout, and return it as a string. """
    result = ""
    # cmd = shlex.split(cmd)
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False, encoding='utf-8')

    # Old implementation
    # pipe = None
    # try:
    #     pipe   = popen(cmd)
    #     result = pipe.read()
    # finally:
    #     if pipe: pipe.close()

    return result



def defaults_read(domain, key):
    """
    Return defaults value stored for `key` in `domain`.

    The return value is always a string.
    Raises KeyError if `domain` and/or `key` doesn't exist.
    """
    try:
        value = subprocess.check_output(['defaults', 'read', domain, key], stderr=subprocess.DEVNULL, encoding='utf-8')
        return value.strip()
    except subprocess.CalledProcessError:
        pass
    raise KeyError(f"Unknown domain ({domain}) and/or key ({key})")


def defaults_write(domain, key, value):
    """
    Write defaults `value` for `key` in `domain`.

    The value is always stored as a string as obtained from `str(value)`.
    Raises Exception if `str(value)` cannot be written to `key` in `domain`.
    """
    try:
        subprocess.check_output(['defaults', 'write', domain, key, str(value)], encoding='utf-8')
        return
    except subprocess.CalledProcessError:
        pass
    raise Exception(f"Unable to write value ({value}) for key ({key}) in domain ({domain})")


# def current_word(pat, direction="both"):
#     """ Return the current word from the environment.
#
#         pat       – A regular expression (as a raw string) matching word characters.
#                     Typically something like this:  r"[A-Za-z_]*".
#         direction – One of "both", "left", "right".  The function will look in
#                     the specified directions for word characters.
#     """
#     word = ""
#     if "TM_SELECTED_TEXT" in env:
#         word = env["TM_SELECTED_TEXT"]
#     elif "TM_CURRENT_WORD" in env and env["TM_CURRENT_WORD"]:
#         line, x = env["TM_CURRENT_LINE"], int(env["TM_LINE_INDEX"])
#         # get text before and after the index.
#         first_part, last_part = line[:x], line[x:]
#         word_chars = compile_(pat)
#         m = word_chars.match(first_part[::-1])
#         if m and direction in ("left", "both"):
#             word = m.group(0)[::-1]
#         m = word_chars.match(last_part)
#         if m and direction in ("right", "both"):
#             word += m.group(0)
#     return word
#
# def env_python():
#     """ Return (python, version) from env.
#
#         Checks for the environment variable TM_FIRST_LINE and parses
#         it for a #!.  Failing that, checks for the environment variable
#         TM_PYTHON.  Failing that, uses "/usr/bin/env python".
#     """
#     python = ""
#     if "TM_FIRST_LINE" in env:
#         first_line = env["TM_FIRST_LINE"]
#         hash_bang = compile_(r"^#!(.*)$")
#         m = hash_bang.match(first_line)
#         if m:
#             python = m.group(1)
#             version_string = sh(python + " -S -V 2>&1")
#             if version_string.startswith("-bash:"):
#                 python = ""
#     if not python and "TM_PYTHON" in env:
#         python = env["TM_PYTHON"]
#     elif not python:
#         python = "/usr/bin/env python"
#     version_string = sh(python + " -S -V 2>&1")
#     version = version_string.strip().split()[1]
#     version = int(version[0] + version[2])
#     return python, version






if __name__ == '__main__':
    domain = "foo.bar.baz"
    defaults_write(domain, 'dummy', 42)
    value = defaults_read(domain, 'dummy')
    print(value)
    subprocess.check_output(['defaults', 'delete', domain])
    try:
        value = defaults_read(domain, 'dummy')
        print(value)
    except KeyError:
        print("OK, domain deleted")

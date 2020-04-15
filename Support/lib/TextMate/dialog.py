# For python3 compatibility
# from plistlib import plistlib.dumps, plistlib.loads
#
# Also see zk://150320082100

import os
import subprocess
import plistlib
import glob

dialog = os.environ['DIALOG']

def _call_dialog(command, *args):
    """ Call the Textmate Dialog process

    command is the command to invoke.
    args are the strings to pass as arguments
    a dict representing the plist returned from DIALOG is returned

    """
    popen_args = [dialog, command]
    popen_args.extend(args)
    result = subprocess.check_output(popen_args)
    return result

def register_images(imgdir):
    imglist = glob.glob(imgdir+'/*.png')
    imgnames = [os.path.basename(img).rsplit('.', 1)[0] for img in imglist]
    for (name, img) in zip(imgnames, imglist):
        _call_dialog('images', '--register', plistlib.dumps({name:img}))
    return imgnames

def present_popup(suggestions, typed='', extra_word_chars='_', return_choice=False):
    retval = _call_dialog('popup',
                          '--suggestions', plistlib.dumps(suggestions),
                          '--alreadyTyped', typed,
                          '--additionalWordCharacters', extra_word_chars,
                          '--returnChoice' if return_choice else '')
    return plistlib.loads(retval) if retval else {}

def present_menu(menu_items):
    selections = [{'title':item} for item in menu_items]
    retval = _call_dialog('menu', '--items', plistlib.dumps(selections))
    return plistlib.loads(retval) if retval else {}

def present_tooltip(text, is_html=False):
    _call_dialog('tooltip', '--html' if is_html else '--text', text)
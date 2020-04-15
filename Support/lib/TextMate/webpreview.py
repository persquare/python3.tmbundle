# encoding: utf-8
# python bindings for soryu's web-preview
import os
import urllib.parse

from .tm_helpers import defaults_read


def html_header(title, subtitle, html_head=None):
    h = HTMLOutput()
    return h.header(title=title, sub_title=subtitle, html_head=html_head)

def html_footer():
    h = HTMLOutput()
    return h.footer()


def collect_themes():
    screen = []
    printer = []
    seen = set() # FIXME: What is this used for?

    paths = os.environ.get('TM_THEME_PATH', '').split(':')
    if 'TM_BUNDLE_SUPPORT' in os.environ:
        paths.append(f"{os.environ['TM_BUNDLE_SUPPORT']}/css/")
    paths.append(f"{os.environ['HOME']}/Library/Application Support/TextMate/Themes/Webpreview/")

    for path in paths:
        try:
            _, dirnames, _ = next(os.walk(path))
        except StopIteration:
            continue
        for dirname in dirnames:
            if dirname != 'default':
                seen.add(dirname)
            if os.path.isfile(f"{path}/{dirname}/style.css"):
                screen.append({'name':dirname.capitalize(), 'class':dirname, 'path':f"{path}/{dirname}"})
            if os.path.isfile(f"{path}/{dirname}/print.css"):
                printer.append({'name':dirname.capitalize(), 'class':dirname, 'path':f"{path}/{dirname}"})

    return {'screen':screen, 'print':printer}


e_url = urllib.parse.quote

class HTMLOutput(object):
    """docstring for HTMLOutput"""
    def __init__(self):
        super(HTMLOutput, self).__init__()

    # media = [screen | print]
    def _styles(self, media):
        themes = self.themes[media]
        lines = [self._style(e_url(theme['path']), 'style' if media=='screen' else 'print', media) for theme in themes]
        html = "\n".join(lines)
        return html

    def _style(self, path, filename, media):
        html = f'  <link rel="stylesheet" href="file://{path}/{filename}.css" type="text/css" charset="utf-8" media="{media}">'
        return html

    def style_options(self):
        themes = self.themes['screen']
        lines = [f"""            <option value="{theme['class']}" title="{theme['path']}">{theme['name']}</option>""" for theme in themes if theme['class'] != 'default']
        html = "\n".join(sorted(lines))
        return html


    def screen_styles(self):
        return self._styles('screen')

    def print_styles(self):
        return self._styles('print')

    def find_theme(self, name):
        for theme in self.themes['screen']:
            if theme['class'] == name:
                return theme

    def saved_theme(self):
        try:
            theme = defaults_read('com.macromates.textmate.webpreview', 'SelectedTheme')
        except KeyError:
            theme = 'plain'
        return theme

    def header(self, window_title=None, page_title=None, title=None, sub_title=None, html_head=None, fix_href=False):

        self.window_title = window_title or title or 'Window Title'
        self.page_title = page_title or title or 'Page Title'
        self.sub_title = sub_title or os.environ.get('TM_FILENAME') or 'untitled'
        self.html_head = html_head or ''


        if fix_href and os.path.isfile(os.environ.get('TM_FILEPATH'), ''):
            self.html_head += f"\n<base href='file://{e_url(os.environ['TM_FILEPATH'])}'>\n"

        self.themes = collect_themes()

        self.active_theme = self.find_theme(self.saved_theme()) or self.find_theme('bright')
        if not self.active_theme:
            raise Exception("No web preview theme found.\nMake sure that the Themes bundle is enabled in Preferences → Bundles.")

        self.support_path = os.environ['TM_SUPPORT_PATH']


        html = f"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-type" content="text/html; charset=utf-8">
        <title>{self.window_title}</title>
        {self.screen_styles()}
        {self.print_styles()}
        <script src="file://{e_url(self.support_path)}/script/default.js" type="text/javascript" charset="utf-8"></script>
        <script src="file://{e_url(self.support_path)}/script/webpreview.js" type="text/javascript" charset="utf-8"></script>
        <script>var image_path = "file://{e_url(self.support_path)}/images/";</script>
        <script src="file://{e_url(self.support_path)}/script/sortable.js"   type="text/javascript" charset="utf-8"></script>
        <!-- Begin CSS and scripts -->
        {self.html_head} 
        <!-- End CSS and scripts -->      
    </head>

    <body id="tm_webpreview_body" class="{self.active_theme['class']}">
        <div id="tm_webpreview_header">
            <img id="gradient" src="file://{e_url(self.active_theme['path'])}/images/header.png" alt="header">
            <p class="headline">{self.page_title}</p>
            <p class="type">{self.sub_title}</p>
            <img id="teaser" src="file://{e_url(self.active_theme['path'])}/images/teaser.png" alt="teaser">
            <div id="theme_switcher">
              <form action="#" onsubmit="return false;">
                <div>
                  Theme:
                  <select onchange="selectTheme(event);" id="theme_selector">
        {self.style_options()}
                  </select>
                </div>
                <script type="text/javascript" charset="utf-8">
                  document.getElementById('theme_selector').value = '{self.active_theme['class']}';
                </script>
              </form>
            </div>
        </div>
    
        <div id="tm_webpreview_content" class="{self.active_theme['class']}">

"""
        return html

    def footer(self):
        html = """
        </div> <!-- tm_webpreview_content -->
    </body>
</html>
"""
        return html


# if __name__ == '__main__':
#     h = HTMLOutput()
#     with open('output.html', 'w') as fd:
#         print(h.header(title='TITLE', sub_title="SUBTITLE"), file=fd)
#         print("<pre>Hello World</pre>", file=fd)
#         print(h.footer(), file=fd, flush=True)
#
#     with open('ref.html', 'w') as fd:
#         print(html_header(title='TITLE', subtitle="SUBTITLE"), file=fd)
#         print("<pre>Hello World</pre>", file=fd)
#         print(html_footer(), file=fd, flush=True)
#
#     import subprocess
#     try:
#         output = subprocess.check_output(["diff", "-uw", "ref.html", "output.html"])
#         print(output)
#     except subprocess.CalledProcessError as err:
#         print(err.output)




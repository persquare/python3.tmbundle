import re
import signal
import urllib.parse

RE_INDENT = re.compile(r'(^\s*)(.*)$')

def make_div(cls, content):
    return f'<div class="{cls}">{content}</div>'

def make_span(cls, content):
    return f'<span class="{cls}">{content}</span>'
    
def make_txmt_link(filepath, line, content):
    return f'<a href="txmt://open?url=file://{filepath}&line={line}">{content}</a>'
    
def make_pid(pid):
    return f'<script>var PID = "{pid}"</script>'

def preserve_leading_indent(line):
    m = RE_INDENT.match(line)
    indent, tail = m.groups()
    line = f'{"&nbsp;"*len(indent)}{tail}'
    return line

def executor_css():
    css = '''
    <style type="text/css">

      div.executor .controls {
        text-align:right;
        float:right;
      }
      div.executor .controls a {
        text-decoration: none;
      }

      div.executor pre em
      {
        font-style: normal;
        color: #FF5600;
      }

      div.executor p#exception strong
      {
        color: #E4450B;
      }

      div.executor p#traceback
      {
        font-size: 8pt;
      }

      div.executor blockquote {
        font-style: normal;
        border: none;
      }

      div.executor table {
        margin: 0;
        padding: 0;
      }

      div.executor td {
        margin: 0;
        padding: 2px 2px 2px 5px;
        font-size: 10pt;
      }

      div.executor div#_executor_output {
        white-space: normal;
        -khtml-nbsp-mode: space;
        -khtml-line-break: after-white-space;
      }

      div#_executor_output .line.current {
        background: rgba(255, 240, 80, 0.25);
        outline: 1px solid rgba(255, 240, 80, 0.25);
      }
      div#_executor_output .out {

      }
      div#_executor_output .err {
        color: red;
      }
      div#_executor_output .test {
        font-weight: bold;
      }
      div#_executor_output .test.ok {
        color: green;
      }
      div#_executor_output .test.fail {
        color: red;
      }
      div#exception_report pre.snippet {
        margin:4pt;
        padding:4pt;
      }
      div#copytime {
        font-size: 10pt;
        float:left;
        display:inline;
      }
    </style>
'''
    return css


def executor_scripts():
    return '''
  <script type="text/javascript" charset="utf-8">
  function press(evt) {
     if (evt.keyCode == 67 && evt.ctrlKey == true) {
       if (typeof PID !== 'undefined') {
         TextMate.system("kill -s USR1 " + PID + ";", null);
       } else {
         console.log("PID is undefined");
       }
       evt.preventDefault();
     }
  }

  function click(evt) {
    if (event.target.tagName == 'A') {
      var line = event.target;
      while (line && !line.classList.contains('line')) line = line.parentElement;
      if (line) {
        Array.from(document.getElementsByClassName('line current')).forEach(function (el) {
          el.classList.remove('current');
        });
        line.classList.add('current');
      }
    }
  }
  function copyOutput(element) {
    output = element.innerText.replace(/(?:^| ) +/mg, function(match, offset, s) { return match.replace(/ /g, ' '); });
    cmd = TextMate.system('/usr/bin/pbcopy', function(){{}});
    cmd.write(output);
    cmd.close();
    document.getElementById('copytime').innerText = 'output copied to clipboard';
  }
  
  function toggle_visibility(element_id) {
    el = document.getElementById(element_id);
    cls = el.className;
    console.log(cls);
    el.className = (cls === 'show') ? 'hide' : 'show';
  }
  
  document.body.addEventListener("keydown", press, false);
  // document.body.addEventListener("click", click)
  </script>
'''


def executor_preamble():
    return f'''
<div class="executor"><!-- » python3 -u untitled.py -->
<!-- executor javascripts -->
{executor_scripts()}
<!-- end javascript -->

<!-- first box containing version info and script output -->
<pre>
<div id="_executor_output"> <!-- Script output -->
'''


def executor_postamble(status, duration, options=None):
    lines = [
        '</div>',
        '</pre>', 
        '<div class="controls">', 
        '''<div id="copytime"></div>&nbsp;&nbsp;<a href="#" onclick="copyOutput(document.getElementById('_executor_output'))">copy output</a>''']

    options = options or {}
    for key in options.get('controls', {}):
        lines.append(""" | <a href="javascript:TextMate.system('#{options[:controls][key]}')">#{key}</a>""")

    lines.append('</div><div id="exception_report" class="framed">')
    if status == -signal.SIGUSR1:
        msg = "Program interrupted by user"
    elif status < 0:
        msg = f"Program terminated by uncaught signal {signal.Signals(-status).name} ({-status})"
    else:
        msg = f"Program exited with code #{status}"
    
    lines.append(f"{msg} after {duration:.2f} seconds")
    lines.append('</div></div>')
    return "\n".join(lines)

#
# Test templates
#    
def test_css():
    css = '''
    <style type="text/css">

      div.executor .controls {
        text-align:right;
        float:right;
      }
      div.executor .controls a {
        text-decoration: none;
      }

      div.executor pre em
      {
        font-style: normal;
        color: #FF5600;
      }

      div.executor p#exception strong
      {
        color: #E4450B;
      }

      div.executor p#traceback
      {
        font-size: 8pt;
      }

      div.executor blockquote {
        font-style: normal;
        border: none;
      }

      div.executor table {
        margin: 0;
        padding: 0;
      }

      div.executor td {
        margin: 0;
        padding: 2px 2px 2px 5px;
        font-size: 10pt;
      }

      div.executor div#_executor_output {
        white-space: normal;
        -khtml-nbsp-mode: space;
        -khtml-line-break: after-white-space;
      }

      div#_executor_output .line.current {
        background: rgba(255, 240, 80, 0.25);
        outline: 1px solid rgba(255, 240, 80, 0.25);
      }
      div#_executor_output .out {

      }
      div#_executor_output .err {
        color: red;
      }
      div#_executor_output .test {
        // font-weight: bold;
      }
      div#_executor_output .test.ok {
        color: green;
      }
      div#_executor_output .test.fail {
        color: FireBrick;
      }
      div#_executor_output .test.xfail {
        color: orange;
      }
      div#_executor_output .test.xpass {
        color: SpringGreen;
      }
      div#_executor_output .test.skipped {
        color: blue;
      }
      
      div#exception_report pre.snippet {
        margin:4pt;
        padding:4pt;
      }
      div#copytime {
        font-size: 10pt;
        float:left;
        display:inline;
      }
      div#_executor_output .hide {
        display: none;
      }
      div#_executor_output .show {
        display: block;
      }
      
    </style>
'''
    return css

test_preamble = executor_preamble


def test_postamble(status):
    lines = [
        '</div>',
        '</pre>',
    ]

    lines.append('<div id="exception_report" class="framed">')
    if status == -signal.SIGUSR1:
        msg = "Program interrupted by user"
    elif status < 0:
        msg = f"Program terminated by uncaught signal {signal.Signals(-status).name} ({-status})"
    else:
        msg = f"Program exited with code #{status}"
    lines.append(msg)
    
    lines.append('</div>')
    return "\n".join(lines)
    
    
    
    
    

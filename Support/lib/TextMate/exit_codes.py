import sys

def discard():
  sys.exit(200)

def replace_text(out = None):
  if out:
      sys.stdout.write(out)
  sys.exit(201)

def replace_document(out = None):
  if out:
      sys.stdout.write(out)
  sys.exit(202)

def insert_text(out = None):
  if out:
      sys.stdout.write(out)
  sys.exit(203)

def insert_snippet(out = None):
  if out:
      sys.stdout.write(out)
  sys.exit(204)

def show_html(out = None):
  if out:
      sys.stdout.write(out)
  sys.exit(205)

# FIXME: Why is this writing to stderr?
def show_tool_tip(out = None):
  if out:
      sys.stderr.write(out)
  sys.exit(206)

def create_new_document(out = None):
  if out:
      sys.stdout.write(out)
  sys.exit(207)


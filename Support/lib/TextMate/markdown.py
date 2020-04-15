#!/usr/bin/env python3

import os

markdown = os.environ.get('TM_MARKDOWN', f"{os.environ[TM_SUPPORT_PATH]}/bin/Markdown.pl")

print(f"{os.environ[TM_SUPPORT_PATH]}/bin/Markdown.pl")
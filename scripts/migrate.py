#!/usr/bin/env python
# Loop through all of the content, converting everything from the hyde format
# into the lightning format.

# source format: (path is year/<filename>.html)
#---------------
# {% hyde
# title: <title>
# created: <YYYY-MM-DD HH:MM:SS>
# <YAML>
# %}
#
# {% block article %}
# <Markdown>
# {% endblock %}

# destination format: (path is year/<filename>/index.txt)
#--------------------
# <title>
# =======
# posted: <YYYY-MM-DD>
# <YAML>
#
# <Markdown>

import sys
import os
import re
import yaml
import time
import datetime
from distutils import dir_util

OUT_ROOT = './output/'
# Get the root path of hyde content.
ROOT = sys.argv[1]

OUT_TMPL = """%(title)s
%(sep)s
%(yaml)s

%(markdown)s
"""

def main():
  # Get all of the blog posts in the hyde root.
  files = get_files()
  # Make the directory for the new content.
  out = dir_util.mkpath(OUT_ROOT)
  # Reformat each blog post.
  for path in files:
    converted = convert(path)
    index_root = OUT_ROOT + os.path.splitext(path)[0] + '/'
    # Write out the reformatted blog post into the directory.
    dir_util.mkpath(index_root)
    f = open(index_root + 'index.txt', 'w');
    f.write(converted)


def get_files():
  """Gets the list of all hyde blog posts in the given directory."""
  files = []
  for dirpath, dirnames, filenames in os.walk(ROOT):
    for fname in filenames:
      if fname.endswith(".html"):
        # Get the file's path and modified time
        path = os.path.join(dirpath, fname)
        files.append(path)

  return files

def convert(path):
  """Converts a file at the given path to the new format."""
  # Open the file.
  contents = open(path, 'r').read()
  # Parse out the hyde metadata.
  yaml_str = get_tag_attribute(contents, 'hyde')
  metadata = yaml.load(yaml_str)
  # Parse out the markdown.
  markdown = get_tag_content(contents, 'block')
  # Convert the date formats.
  created = metadata['created']
  metadata['posted'] = convert_date(created)
  del metadata['created']
  # Extract the title.
  title = metadata['title']
  del metadata['title']
  return OUT_TMPL % {
    'yaml': yaml.safe_dump(metadata),
    'title': title,
    'markdown': markdown,
    'sep': '=' * len(title)
  }

def get_tag_attribute(string, tag):
  """Gets the tag's inline value {% tag ...this... %}"""
  # Find the tag in the string.
  tag_start = '{%% *%s' % tag
  tag_end = ' *%}'
  return get_substr_between(string, tag_start, tag_end)

def get_tag_content(string, tag):
  """Gets the tag's content {% tag %}...this...{% endtag %}"""
  tag_start = '{%% *%s *\w*? *%%}' % tag
  tag_end = '{%% *end%s *%%}' % tag
  return get_substr_between(string, tag_start, tag_end)

def get_substr_between(string, start, end):
  start_index = re.search(start, string).start()
  after_string = string[start_index:]
  end_index = re.search(end, after_string).start() + start_index

  return string[start_index + len(start):end_index]

def convert_date(dt):
  return dt.date()

if __name__ == '__main__':
  main()

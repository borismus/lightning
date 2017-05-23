import datetime
from itertools import tee, izip
from jinja2 import Template, Environment, FileSystemLoader
import re
import yaml

DEFAULT_TIME = datetime.time(9, 0)


def ComputePermalink(type_name, slug, created_date, permalink_template='{{slug}}'):
  """Returns the permalink for the given item."""
  permalink_data = {'slug': slug}
  # If there's date information associated, include it in the permalink data.
  if created_date:
    permalink_data = dict(permalink_data.items() + created_date.items())
  return '/' + RenderTemplateString(permalink_template, permalink_data)


def ParseSnip(content):
  """Return the snippet based on the content."""
  found = content.find('<!--more-->')
  if found >= 0:
    return content[:found]


def ParseDate(date):
  """Gets the permalink parameters based on the item's info."""
  try:
    t = datetime.datetime.combine(date, DEFAULT_TIME)
  except TypeError as e:
    return False

  return {
    'year': t.year,
    'month': t.month,
    'month_name': t.strftime('%b'),
    'day': t.day,
    'unix': int(time.mktime(t.timetuple())),
    'formatted': t.strftime(self.site_info['date_format']),
    'rfc': self.rfcformat(t)
  }


def GuessDate(path):
  """Based on the filesystem structure (eg. blah/2014/09/20/foo-bar.md),
  extracts the date."""
  regex = '.*\/([0-9]{4})\/([0-9]{2})\/([0-9]{2})\/.*'
  match = re.match(regex, path)
  if match:
    date_tuple = map(int, match.groups())
    date = datetime.datetime(*date_tuple)
    return ParseDate(date)


def GuessType(path):
  """Return the type. These are a bunch of defaults..."""
  if path.find('/pages/') >= 0:
    return 'page'
  elif path.find('/posts/') >= 0:
    return 'post'
  elif path.find('/drafts/') >= 0:
    return 'draft'
  elif path.find('/archives/') >= 0:
    return 'archive'
  if path.find('/links/') >= 0:
    return 'link'
  if path.find('/talks/') >= 0:
    return 'talk'
  if path.find('/projects/') >= 0:
    return 'project'


def GuessSlug(path):
  """Returns the slug."""
  if path.endswith('index.md'):
    # If it ends with index, get the second last path component.
    return path.split('/')[-2]
  else:
    # Otherwise, just get the filename.
    return path.split('/')[-1].split('.')[0]


def RenderTemplateString(template_string, data):
  template = Template(template_string)
  return template.render(data)


def FindSplitIndices(lines):
  """Given some lines representing a markdown file with multiple entries in it,
  find each split point."""

  def CodeLine(line):
    if line == '\n':
      return 'N'
    elif re.match('\w', line):
      return 'T'
    elif re.match('^===+$', line):
      return 'D'
    else:
      return '?'

  # Code lines: T if any text, N if new line, D if divider.
  coded_lines = [CodeLine(line) for line in lines]
  coded = ''.join(coded_lines)

  # Look for patterns of NTDN in the coded lines string. If such a pattern is
  # found, output the index.
  return [m.start() for m in re.finditer('NTDN', coded)]


def GetYamlMetadata(lines):
  # Extract the title.
  title = lines[0].strip()
  # Get the key: value pairs after the title.
  separator_index = lines.index('\n')
  yaml_lines = lines[2:separator_index]
  data = yaml.load(''.join(yaml_lines)) or {}
  data['title'] = title
  return data


def Pairwise(iterable):
  """Returns a pairwise iterated list."""
  a, b = tee(iterable)
  next(b, None)
  return list(izip(a, b))


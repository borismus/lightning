import datetime
from itertools import tee, izip
from jinja2 import Template, Environment, FileSystemLoader
import os
import re
import shutil
import time
import warnings
import yaml

DEFAULT_TIME = datetime.time(9, 0)
MAX_SLUG_LENGTH = 30


class Date:
  def __init__(self, datetime):
    self.datetime = datetime

  def GetDict(self):
    dt = self.datetime
    return {
      'year': dt.year,
      'month': dt.month,
      'month_name': dt.strftime('%b'),
      'day': dt.day,
      'unix': self.Unix(),
    }

  def Unix(self):
    return int(time.mktime(self.datetime.timetuple()))

  def Format(self, template):
    return self.datetime.strftime(template)

  def Rfc(self):
    dt = self.datetime
    if dt.tzinfo is None:
      suffix = "-00:00"
    else:
      suffix = dt.strftime("%z")
      suffix = suffix[:-2] + ":" + suffix[-2:]
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + suffix

  def __sub__(self, to_subtract):
    return self.Unix() - to_subtract.Unix()



def ComputePermalink(type_name, slug, created_date, permalink_template='{{slug}}'):
  """Returns the permalink for the given item."""
  permalink_data = {'slug': slug}
  # If there's date information associated, include it in the permalink data.
  if created_date:
    permalink_data = dict(permalink_data.items() +
        created_date.GetDict().items())
  return RenderTemplateString(permalink_template, permalink_data)


def ParseSnip(content):
  """Return the snippet based on the content."""
  found = content.find('<!--more-->')
  if found >= 0:
    return content[:found]


def ParseDate(date):
  """Gets the permalink parameters based on the item's info."""
  try:
    dt = datetime.datetime.combine(date, DEFAULT_TIME)
    return Date(dt)
  except TypeError as e:
    return None


def GuessDate(path):
  """Based on the filesystem structure (eg. blah/2014/09/20/foo-bar.md),
  extracts the date."""
  regex = '.*\/([0-9]{4})\/([0-9]{2})\/([0-9]{2})\/.*'
  match = re.match(regex, path)
  if match:
    date_tuple = map(int, match.groups())
    date = datetime.datetime(*date_tuple)
    return ParseDate(date)


def GuessType(path, mappings):
  """Return the type based on the path. The site config provides automatic
  mappings based on path."""
  for type_path, type_name in mappings.items():
    if path.find(type_path) >= 0:
      return type_name


def GuessSlugFromPath(path):
  """Returns the slug."""
  if path.endswith('index.md'):
    # If it ends with index, get the second last path component.
    return path.split('/')[-2]
  else:
    # Otherwise, just get the filename.
    return path.split('/')[-1].split('.')[0]


def GuessSlugFromTitle(title):
  """Return an automatically generated slug from title. Turn spaces into dashes,
  lowercase everything, limit length."""
  def IsValidChar(c):
    return c.isalnum() or c == '-'

  lower = title.lower()
  slug = lower.replace(' ', '-')
  slug = ''.join([c for c in slug if IsValidChar(c)])
  slug = re.sub("-+", "-", slug)
  return slug


def RenderTemplateString(template_string, data):
  template = Template(template_string)
  return template.render(data)


def RenderTemplate(template_root, filename, data):
  env = Environment(loader=FileSystemLoader(template_root))
  try:
    template = env.get_template(filename)
  except Exception:
    raise Exception('Failed to find template %s.' % filename)
  try:
    out = template.render(data)
  except Exception as e:
    raise Exception('Failed to render template %s: "%s".' % (filename, e))

  return out


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

  #warnings.warn(coded)

  # Look for patterns of NTDN in the coded lines string. If such a pattern is
  # found, output the index.
  return [m.start() for m in re.finditer('NTDN', coded)]


def GetYamlMetadata(lines):
  # Ignore empty leading lines.
  for i, line in enumerate(lines):
    if line == '\n':
      del lines[i]
    else:
      break

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


def CopyAndOverwrite(from_path, to_path):
  if os.path.exists(to_path):
    shutil.rmtree(to_path)
  shutil.copytree(from_path, to_path)


def DeletePath(path):
  """Remove file or directory at path."""
  if os.path.isfile(path):
    os.unlink(path)
  else:
    shutil.rmtree(path)

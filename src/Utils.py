import datetime
from dateutil import parser
from itertools import tee
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
    self.date_format = '%b'

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

  def Format(self, date_format=None):
    if not date_format:
      date_format = self.date_format
    return self.datetime.strftime(date_format)

  def Rfc(self):
    dt = self.datetime
    if dt.tzinfo is None:
      suffix = "-00:00"
    else:
      suffix = dt.strftime("%z")
      suffix = suffix[:-2] + ":" + suffix[-2:]
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + suffix

  def SetDateFormat(self, date_format):
    self.date_format = date_format

  def __sub__(self, to_subtract):
    return self.Unix() - to_subtract.Unix()

  @staticmethod
  def Now():
    return Date(datetime.datetime.now())



def ComputePermalink(type_name, slug, created_date, permalink_template='{{slug}}'):
  """Returns the permalink for the given item."""
  permalink_data = {'slug': slug}
  # If there's date information associated, include it in the permalink data.
  if created_date:
    permalink_data = dict(permalink_data.items())
    permalink_data.update(created_date.GetDict().items())
  return RenderTemplateString(permalink_template, permalink_data)


def ParseSnip(content):
  """Return the snippet based on the content."""
  found = content.find('<!--more-->')
  if found >= 0:
    return content[:found]


def ParseDate(date):
  """Gets the permalink parameters based on the item's info."""
  try:
    if type(date) == str:
      date_string = date
      date = parser.parse(date_string)
      #warnings.warn('Parsed %s into %s.' % (date_string, date))

    dt = datetime.datetime.combine(date, DEFAULT_TIME)
    return Date(dt)
  except TypeError as e:
    warnings.warn('Failed to parse date: %s.' % e)
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
  # print(f'GuessDate failed on {path}')


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
    raise Exception(f'Failed to find template {filename}.')
  try:
    out = template.render(data)
  except Exception as e:
    raise Exception(f'Failed to render template {filename}: "{e}".')

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
  return [m.start() for m in re.finditer('NTD', coded)]


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
  data = yaml.load(''.join(yaml_lines), Loader=yaml.SafeLoader) or {}
  data['title'] = title
  return data


def Pairwise(iterable):
  """Returns a pairwise iterated list."""
  a, b = tee(iterable)
  next(b, None)
  return list(zip(a, b))


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


def FixBrokenLinks(content, permalink):
  """Given content (HTML or RSS), this will make all relative links into
  absolute ones referring to the permalink."""
  links = re.findall(r'<a href="(.+?)"', content, re.DOTALL) + \
          re.findall(r'<img src="(.+?)"', content, re.DOTALL) + \
          re.findall(r'<audio src="(.+?)"', content, re.DOTALL) + \
          re.findall(r'<video src="(.+?)"', content, re.DOTALL)

  # If the links are relative, make them absolute.
  for link in set(links):
    # If it doesn't have http or / at the beginning, it's a relative URL.
    if not link.startswith('/') and not link.startswith('http') and not \
        link.startswith('mailto'):
      # If they are relative, rewrite them using the permalink
      absolute_link = os.path.join(permalink, link)
      content = content.replace(link, absolute_link)

      # warnings.warn(f'Made relative link {link} into absolute {absolute_link}.')

  return content

def FormatWikiLinks(html):
  """Given an html file, convert [[WikiLinks]] into *WikiLinks* just to ease
  readability."""
  wikilink = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]')
  return wikilink.sub(r'*\1*', html)

def ResolveWikiLinks(html):
  """Given an html file, convert [[WikiLinks]] into links to the personal wiki:
  <a href="https://z3.ca/WikiLinks">WikiLinks</a>"""
  wikilink = re.compile(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]')
  def linkify(match):
    wiki_root = 'https://z3.ca'
    wiki_name = match.group(1).replace('\n', ' ')
    wiki_slug = wiki_name.replace(' ', '_')
    return f'<a class="wiki" href="{wiki_root}/{wiki_slug}">{wiki_name}</a>'
  return wikilink.sub(linkify, html)


def StripHtmlTags(html):
  return re.sub('<[^<]+?>|\n', ' ', html)

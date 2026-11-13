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

from BuildException import BuildException

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
  regex = r'.*\/([0-9]{4})\/([0-9]{2})\/([0-9]{2})\/.*'
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


FRONT_MATTER_DELIMITER = '---'
FENCE = re.compile(r'^(```|~~~)')


def ParseFrontMatter(text, source='<string>', line_offset=0):
  """Splits text that starts with a YAML front matter block:

    ---
    title: My new post
    posted: 2012-03-01 9:00
    ---

    Just **testing**

  into (metadata dict, markdown body). Raises BuildException on malformed
  input rather than guessing."""
  where = f'{source}:{line_offset + 1}'
  lines = text.split('\n')
  if not lines or lines[0].rstrip() != FRONT_MATTER_DELIMITER:
    raise BuildException(f'{where}: expected file to start with "---" front '
        'matter.')
  try:
    close = next(i for i in range(1, len(lines))
        if lines[i].rstrip() == FRONT_MATTER_DELIMITER)
  except StopIteration:
    raise BuildException(f'{where}: front matter is missing its closing '
        '"---".')
  try:
    data = yaml.load('\n'.join(lines[1:close]), Loader=yaml.SafeLoader) or {}
  except yaml.YAMLError as e:
    raise BuildException(f'{where}: invalid YAML front matter: {e}')
  if type(data) != dict:
    raise BuildException(f'{where}: front matter must be a YAML mapping.')
  body = '\n'.join(lines[close + 1:]).lstrip('\n')
  return data, body


def FindEntryStarts(text):
  """Given the body of a multi-entry (class: split) file, returns the line
  index of each entry. An entry starts with a front matter block whose first
  key is title:

    ---
    title: Use of Weapons by Iain Banks
    ---

  A "---" line followed by anything else is an ordinary horizontal rule.
  Lines inside fenced code blocks are ignored."""
  lines = text.split('\n')
  starts = []
  in_fence = False
  for i, line in enumerate(lines):
    if FENCE.match(line):
      in_fence = not in_fence
    elif not in_fence and line.rstrip() == FRONT_MATTER_DELIMITER and \
        i + 1 < len(lines) and lines[i + 1].startswith('title:'):
      starts.append(i)
  return starts


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


RASTER_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp')

def FindFirstImage(html):
  """Returns the src of the first raster (non-SVG) image in the html, or None."""
  for src in re.findall(r'<img [^>]*src="([^"]+)"', html):
    if src.split('?')[0].lower().endswith(RASTER_IMAGE_EXTENSIONS):
      return src
  return None


def LazyLoadMedia(html):
  """Defers loading of every iframe and every image but the first, which is
  usually on screen when the page opens."""
  first, img, rest = html.partition('<img ')
  html = first + img + rest.replace('<img ', '<img loading="lazy" ')
  return html.replace('<iframe ', '<iframe loading="lazy" ')

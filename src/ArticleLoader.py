import markdown
import re
from urllib.parse import urljoin
import warnings
import yaml

from Article import *
from BuildException import BuildException
from Utils import *


class ArticleLoader:
  def __init__(self, site_config, is_metadata_only=False):
    self.site_config = site_config
    self.is_metadata_only = is_metadata_only


  def LoadAny(self, path):
    """Loads any type of article, and determines the type of the article later.
    This can return an Article, IndexArticle or SplitArticle.

    Type of article is determined by YAML header called class."""
    # Determine what the article type is based on the YAML metadata.
    data, _ = ParseFrontMatter(ReadFile(path), path)
    class_name = data['class'] if ('class' in data) else 'default'

    if class_name == 'index':
      return self.LoadIndexArticle(path)
    elif class_name == 'home':
      return self.LoadHomeArticle(path)
    elif class_name == 'split':
      return self.LoadSplitArticle(path)
    else:
      return self.LoadArticle(path)


  def LoadArticle(self, path):
    metadata = self.GetArticleMetadata(path)
    article = Article(**metadata)
    return article


  def LoadSplitArticle(self, path):
    """A split article is one file holding many entries (eg. a year of book
    reviews). The file's own front matter holds defaults like type; each entry
    then starts with its own front matter block beginning with title:. See
    FindEntryStarts."""
    text = ReadFile(path)
    _, body = ParseFrontMatter(text, path)
    header = text[:len(text) - len(body)]
    body_offset = header.count('\n')
    # The header becomes its own article which is never rendered, but its
    # type_name propagates to the entries.
    first_metadata = self.GetArticleMetadata(path, text=header,
        require_title=False)

    lines = body.split('\n')
    starts = FindEntryStarts(body)
    if not starts:
      raise BuildException(f'{path}: split file has no entries. Each entry '
          'starts with a "---" line followed by "title: ...".')
    stray = '\n'.join(lines[:starts[0]]).strip()
    if stray:
      raise BuildException(f'{path}:{body_offset + 1}: content before the '
          f'first entry: {stray[:60]!r}')

    articles = []
    for start, end in Pairwise(starts + [len(lines)]):
      entry = '\n'.join(lines[start:end])
      metadata = self.GetArticleMetadata(path, text=entry,
          line_offset=body_offset + start)
      # Autogenerate the slug from the title.
      metadata['slug'] = GuessSlugFromTitle(metadata['title'])
      metadata['type_name'] = first_metadata['type_name']
      metadata.update(self.GetPermalinkMetadata(metadata))
      articles.append(Article(**metadata))

    return SplitArticle(articles, **first_metadata)


  def GetIndexArticleMetadata(self, path):
    metadata = self.GetArticleMetadata(path)
    data = metadata['yaml']
    type_filter = ('filter' in data) and data['filter'] or '*'
    # Expect type_filter to be a list of filters.
    if type_filter and type(type_filter) != list:
      type_filter = [type_filter]

    metadata['type_filter'] = type_filter
    if 'limit' in data:
      metadata['limit'] = data['limit']
    return metadata


  def LoadIndexArticle(self, path):
    metadata = self.GetIndexArticleMetadata(path)
    return IndexArticle(**metadata)


  def LoadHomeArticle(self, path):
    metadata = self.GetIndexArticleMetadata(path)
    return HomeArticle(**metadata)


  def GetArticleMetadata(self, path, text=None, line_offset=0,
      require_title=True):
    """Parses markup from files like this:

      ---
      title: My new post
      type: post
      posted: 2012-03-01 9:00
      slug: my-new-post
      snip: A short summary of what's written in the post.
      ---

      Just **testing**

    into an dict bundle representing it.
    """
    source_path = path
    if text is None:
      text = ReadFile(path)

    data, markdown_body = ParseFrontMatter(text, source_path, line_offset)

    if 'title' not in data:
      if require_title:
        raise BuildException(f'{source_path}:{line_offset + 1}: front '
            'matter has no title.')
      data['title'] = GuessSlugFromPath(path)

    # Handle [[WikiLinks]].
    markdown_body = ResolveWikiLinks(markdown_body)
    content = self.is_metadata_only and '' or \
        LazyLoadMedia(GenerateHtmlFromMd(markdown_body))
    # If there's no snip specified, try to parse it before the <!--more--> tag.
    snip = self.is_metadata_only and '' or \
        'snip' in data and GenerateHtmlFromMd(data['snip']) or ParseSnip(content)

    # Save a bunch of properties.
    snip = snip or content
    title = str(data['title'])

    # Infer slug and type from path.
    slug = 'slug' in data and data['slug'] or GuessSlugFromPath(path)
    type_name = None

    # Get the type of guess it based on the path.
    if 'type' in data:
      type_name = data['type']
    elif self.site_config:
      type_name = GuessType(path, self.site_config.type_mapping) or \
          self.site_config.default_type

    date_created = None
    if 'posted' in data:
      # Parse the date if it's specified.
      date_created = ParseDate(data['posted'])
    else:
      # Otherwise, guess the date based on the directory structure.
      date_created = GuessDate(path)

    metadata = {
      'title': title,
      'content': content,
      'slug': slug,
      'snip': snip,
      'date_created': date_created,
      'type_name': type_name,
      'source_path': source_path,
      'meta_description': StripHtmlTags(snip).strip(),
      'yaml': data
    }
    permalink = self.GetPermalinkMetadata(metadata)
    metadata.update(permalink)
    metadata['first_image'] = self.GetFirstImageUrl(content,
        metadata['permalink'])
    return metadata


  def GetFirstImageUrl(self, content, permalink):
    """Absolute URL of the article's first raster image, for share previews."""
    src = FindFirstImage(content)
    if not src:
      return None
    domain = self.site_config and self.site_config.domain or ''
    return urljoin(domain + permalink.rstrip('/') + '/', src)


  def GetPermalinkMetadata(self, metadata):
    # Compute the permalink.
    slug = metadata['slug']
    permalink = slug
    type_name = metadata['type_name']
    date_created = metadata['date_created']
    if self.site_config:
      formats = self.site_config.permalink_formats
      permalink_template = type_name in formats and formats[type_name] \
          or '{{slug}}'
      permalink = ComputePermalink(type_name, slug, date_created,
          permalink_template=permalink_template)

    return {
      'permalink': '/' + permalink,
      'output_path': permalink,
    }


def GenerateHtmlFromMd(md):
  return markdown.markdown(md, extensions=['tables', 'fenced_code', 'footnotes'])


def ReadFile(path):
  with open(path, 'r') as f:
    return f.read()

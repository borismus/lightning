import markdown2
import re
import warnings
import yaml

from Article import *
from BuildException import BuildException
from Utils import *

DEFAULT_LIMIT = 10

class ArticleLoader:
  def __init__(self, site_config):
    self.site_config = site_config


  def LoadAny(self, path):
    """Loads any type of article, and determines the type of the article later.
    This can return an Article, IndexArticle or SplitArticle.

    Type of article is determined by YAML header called class."""
    # Determine what the article type is based on the YAML metadata.
    f = open(path, 'rU')
    lines = f.readlines()
    data = GetYamlMetadata(lines)
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
    """If we're dealing with a split article, we have to split the file into
    separate files, and handling each one separately, and then creating an
    Article for each and linking them together in a SplitArticle."""
    f = open(path, 'rU')
    lines = f.readlines()

    # Look for splits in the file, in the form \nTITLE\n=====\n\n.
    split_indices = FindSplitIndices(lines)

    # Separate the file based on split indices, and load an article for each.
    split_indices.append(len(lines) - 1)

    # The first part of the split article becomes its own article which is never
    # rendered. But we should propagate the type_name to the rest of the
    # articles.
    first_part = lines[0:split_indices[0]]
    first_metadata = self.GetArticleMetadata(path, lines=first_part)

    articles = []
    for start, end in Pairwise(split_indices):
      subset = lines[start:end]
      metadata = self.GetArticleMetadata(path, lines=subset)
      # Autogenerate the slug from the title.
      metadata['slug'] = GuessSlugFromTitle(metadata['title'])
      metadata['type_name'] = first_metadata['type_name']
      metadata.update(self.GetPermalinkMetadata(metadata))

      article = Article(**metadata)

      # Generate an auto-slug for each article, based on its title.
      #warnings.warn('Generated slug for article: %s.' % article.slug)

      articles.append(article)

    #warnings.warn('Creating SplitArticle with %s' % str([a.permalink for a in articles]))
    return SplitArticle(articles, **metadata)


  def GetIndexArticleMetadata(self, path):
    metadata = self.GetArticleMetadata(path)

    f = open(path, 'rU')
    lines = f.readlines()
    data = GetYamlMetadata(lines)
    metadata['type_filter'] = data['filter'] if ('filter' in data) else '*'
    metadata['limit'] = data['limit'] if ('limit' in data) else DEFAULT_LIMIT
    return metadata


  def LoadIndexArticle(self, path):
    metadata = self.GetIndexArticleMetadata(path)
    return IndexArticle(**metadata)


  def LoadHomeArticle(self, path):
    metadata = self.GetIndexArticleMetadata(path)
    return HomeArticle(**metadata)


  def GetArticleMetadata(self, path, lines=[]):
    """Parses markup from files like this:

      My new post
      ===========
      type: post
      posted: 2012-03-01 9:00
      slug: my-new-post
      snip: A short summary of what's written in the post.

      Just **testing**

    into an dict bundle representing it.
    """
    source_path = path
    if not lines:
      # Load the file.
      f = open(path, 'rU')
      lines = f.readlines()

    if len(lines) == 0:
      raise BuildException('Unable to load article %s: content missing.' %
          source_path)

    data = GetYamlMetadata(lines)

    if type(data) != dict:
      raise BuildException('Expected dictionary YAML header for %s.' \
          % source_path)

    # Process the rest of the post as Markdown.
    separator_index = lines.index('\n')
    markdown_lines = lines[separator_index+1:]
    markdown_body = ''.join(markdown_lines).decode('utf-8')
    content = markdown2.markdown(markdown_body)
    # If there's no snip specified, try to parse it before the <!--more--> tag.
    snip = 'snip' in data and markdown2.markdown(data['snip']) \
                           or ParseSnip(content)

    # Save a bunch of properties.
    snip = snip or content
    title = unicode(data['title'], 'utf8')
    content = content

    # Infer slug and type from path.
    slug = 'slug' in data and data['slug'] or GuessSlugFromPath(path)
    type_name = None

    # Get the type of guess it based on the path.
    if 'type' in data:
      type_name = data['type']
    elif self.site_config:
      type_name = GuessType(path, self.site_config.type_mapping) or \
          self.site_config.default_type

    summary = markdown_body[:markdown_body.find('.')+1]
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
      'source_path': source_path
    }
    permalink = self.GetPermalinkMetadata(metadata)
    metadata.update(permalink)
    return metadata


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


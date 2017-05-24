import os
import warnings
import yaml

from ArticleLoader import ArticleLoader
from Article import IndexArticle
from Site import *
from Utils import *

REQUIRED_CONFIG_FIELDS = ['template', 'content', 'output']
REQUIRED_SITE_FIELDS = ['site_title', 'date_format', 'permalink_formats',
    'type_mapping', 'default_type']


class SiteLoader:
  """Loads a whole site, based on the lightning.yaml in the current directory."""

  def __init__(self, include_staging=True):
    self.include_staging = include_staging
    self.build_config = self.LoadBuildConfig('lightning.yaml')
    self.site_config = self.LoadSiteConfig(self.build_config.content_root)


  def Load(self):
    self.LoadContent()


  def LoadBuildConfig(self, path):
    config = yaml.load(open(path))
    EnsureFieldsExist(config, REQUIRED_CONFIG_FIELDS)

    template_root = config['template']
    if not os.path.exists(template_root):
      raise Exception('Template path %s not found.' % template_root)

    content_root = config['content']
    if not os.path.exists(content_root):
      raise Exception('Content path %s not found.' % content_root)

    output_root = config['output']

    return BuildConfig(content_root=content_root, template_root=template_root,
        output_root=output_root)


  def LoadSiteConfig(self, content_root):
    site_config_path = os.path.join(content_root, 'site.yaml')
    site = yaml.load(open(site_config_path))
    EnsureFieldsExist(site, REQUIRED_SITE_FIELDS)

    return SiteConfig(title=site['site_title'], date_format=site['date_format'],
        permalink_formats=site['permalink_formats'],
        type_mapping=site['type_mapping'], default_type=site['default_type'])


  def LoadContent(self, staging_prefix='staging'):
    """Load all of the articles found in the content root, ultimately returning
    a list of articles."""
    content_root = self.build_config.content_root
    staging_root = os.path.join(content_root, staging_prefix)

    # Load all of the markdown files.
    markdown_files = []
    for dirpath, dirnames, filenames in os.walk(content_root):
      for fname in filenames:
        if fname.endswith('.md'):
          path = os.path.join(dirpath, fname)

          if not self.include_staging:
            # Ignore files that are for staging.
            if path.startswith(staging_root):
              continue

          markdown_files.append(path)

    loader = ArticleLoader(self.site_config)
    articles = [loader.LoadAny(path) for path in markdown_files]
    self.site_config.SetArticles(articles)

    all_articles = self.site_config.GetFlattenedArticles()
    #warnings.warn(str([a.type_name for a in all_articles]))

    # Set date format on all articles.
    for article in all_articles:
      if article.date_created:
        article.date_created.SetDateFormat(self.site_config.date_format)

    def IsMatchingSingle(article, type_filter):
      is_single = not isinstance(a, IndexArticle)
      is_matching = (type_filter == '*') or a.type_name == type_filter
      return is_single and is_matching

    def ByDate(a, b):
      if not a.date_created and not b.date_created:
        return 0
      if a.date_created and not b.date_created:
        return 1
      elif not a.date_created and b.date_created:
        return -1
      return b.date_created - a.date_created

    # After loading all of the articles, populate sub-articles for all of the
    # index articles.
    index_articles = [a for a in all_articles if isinstance(a, IndexArticle)]
    for index in index_articles:
      # Filter articles by type.
      matching_articles = [a for a in all_articles if \
          IsMatchingSingle(a, index.type_filter)]

      # Order articles by date, then apply a limit.
      matching_articles = sorted(matching_articles, cmp=ByDate)
      if index.limit:
        matching_articles = matching_articles[:index.limit]

      #warnings.warn('Index %s has matching articles %s.' % (index.title,
      #  [a.permalink for a in matching_articles]) )

      index.SetArticles(matching_articles)

    # Fix all broken links in the articles.
    for article in all_articles:
      article.content = FixBrokenLinks(article.content, article.permalink)
      article.snip = FixBrokenLinks(article.snip, article.permalink)



def EnsureFieldsExist(data, fields):
  for field in fields:
    if not field in data:
      raise Exception('Lightning config field missing: %s.' % field)

import os
import warnings

from Article import SplitArticle, IndexArticle
from Utils import *

class SiteBuilder:

  def __init__(self, build_config):
    self.build_config = build_config

  def BuildSite(self, site):
    # Render each article into HTML.
    for article in site.GetFlattenedArticles():
      self.BuildArticle(article, site)

    # Copy static assets.
    self.CopyStatic()


  def BuildPartialSite(self, site, changed_articles):
    # Render only the specified articles.
    for article in changed_articles:
      self.BuildArticle(article, site)


  def BuildArticle(self, article, site=None):
    template_data = article.ToDict()
    if site:
      template_data['site'] = site.ToDict()
    template_data['date_generated'] = Date.Now()

    html = RenderTemplate(self.build_config.template_root,
        article.GetTemplatePath(), template_data)

    #if isinstance(article, IndexArticle):
    #  print('Index %s has %s children.' % (article.title,
    #    len(article.articles)))
    #print('Rendering article %s.' % article)

    # Create the directory for the parsed HTML.
    if article.output_path.endswith('.html'):
      index_path = os.path.join(self.build_config.output_root, article.output_path);
      print('.html path specified, outputting at {}'.format(index_path))
    else:
      dir_path = os.path.join(self.build_config.output_root, article.output_path)
      if isinstance(article, IndexArticle) and article.is_feed:
        index_path = dir_path + '.xml'
      else:
        if not os.path.exists(dir_path):
          os.makedirs(dir_path)
        index_path = os.path.join(dir_path, 'index.html')

    # Copy any assets that should be copied.
    self.CopyAssets(article)

    # Create the index file inside the directory.
    f = open(index_path, 'w')
    f.write(html)


  def CopyAssets(self, article):
    """If the item is an index file, and there are assets in its directory,
    copy them over."""
    if not article.source_path.endswith('index.md'):
      # It's an index file, so there's nothing to do.
      return

    src = os.path.dirname(article.source_path)
    dst = os.path.join(self.build_config.output_root, article.output_path)
    # Copy everything in the item path to the destination path.
    CopyAndOverwrite(src, dst)

    # Remove the raw index.md.
    os.remove(os.path.join(dst, 'index.md'))


  def CopyStatic(self):
    """Copies the static part of the template directory into the output
    root (only if it's not there yet)."""
    src = os.path.join(self.build_config.template_root, 'static/')
    dst = os.path.join(self.build_config.output_root, 'static/')

    #if not os.path.exists(dst):
    print('Copying static directory from %s to %s' % (src, dst))
    CopyAndOverwrite(src, dst)


  def Clean(self):
    """Removes the contents of the output directory entirely."""
    # If there's nothing to clean, do nothing.
    if not os.path.exists(self.build_config.output_root):
      return

    for f in os.listdir(self.build_config.output_root):
      # Leave the .git directory intact.
      if f == '.git' or f == 'CNAME':
        continue
      file_path = os.path.join(self.build_config.output_root, f)
      DeletePath(file_path)

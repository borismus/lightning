import os
import warnings

from Article import SplitArticle, IndexArticle
from Utils import *

class SiteBuilder:

  def __init__(self, build_config, is_incremental=False):
    self.build_config = build_config
    self.is_incremental = is_incremental

  def BuildSite(self, site):
    # Render each article into HTML.
    for article in site.GetFlattenedArticles():
      self.BuildArticle(article, site)


  def BuildArticle(self, article, site=None):
    html = RenderTemplate(self.build_config.template_root,
        article.GetTemplatePath(), article.ToDict())

    #warnings.warn('Rendering article %s.' % article.ToShortDict())

    # Create the directory for the parsed HTML.
    dir_path = os.path.join(self.build_config.output_root, article.output_path)
    if not os.path.exists(dir_path):
      os.makedirs(dir_path)
    index_path = os.path.join(dir_path, 'index.html')

    # Copy any assets that should be copied.
    self.CopyAssets(article)

    # Create the index file inside the directory.
    f = open(index_path, 'w')
    f.write(html.encode('utf-8'))


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


  def Clean(self):
    """Removes the contents of the output directory entirely."""
    for f in os.listdir(self.build_config.output_root):
      # Leave the .git directory intact.
      if f == '.git' or f == 'CNAME':
        continue
      file_path = os.path.join(self.build_config.output_root, f)
      DeletePath(file_path)

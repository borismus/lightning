import os
import sys
sys.path.insert(0, './src')

from Site import BuildConfig, SiteConfig
from ArticleLoader import ArticleLoader
from SiteLoader import SiteLoader
from SiteBuilder import SiteBuilder

site_config = SiteConfig(type_mapping={'/pages/': 'page', '/posts/': 'post'},
    default_type='page', permalink_formats={'post': 'blog/{{slug}}'})
build_config = BuildConfig(template_root='template')
loader = ArticleLoader(site_config)
builder = SiteBuilder(build_config)


def test_article():
  article = loader.LoadArticle('content/simple.md')
  builder.BuildArticle(article)
  assert os.path.exists('www/simple/index.html')


def test_post():
  article = loader.LoadArticle('content/posts/2012/lightning/index.md')
  builder.BuildArticle(article)
  assert os.path.exists('www/blog/lightning/index.html')


def test_split():
  article = loader.LoadArticle('content/books.md')
  builder.BuildArticle(article)


def test_build_site():
  site_loader = SiteLoader()
  site_loader.Load()
  builder = SiteBuilder(site_loader.build_config, is_incremental=False)
  builder.BuildSite(site_loader.site_config)
  assert os.path.exists('www/about/index.html')


def setup_module(module):
  """Setup any state specific to the execution of the given module."""
  pass


def teardown_module(module):
  """Teardown any state that was previously setup with a setup_module
  method."""
  print('teardown_module')
  builder.Clean()

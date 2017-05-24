import sys
sys.path.insert(0, './src')

from ArticleLoader import ArticleLoader
from Article import *
from Site import SiteConfig


site_config = SiteConfig(type_mapping={'/pages/': 'page', '/posts/': 'post'},
    default_type='page', permalink_formats={'post': 'blog/{{slug}}'})
loader = ArticleLoader(site_config)

def test_simple():
  path = 'content/simple.md'
  article = loader.LoadArticle(path)
  assert article.source_path == path
  assert article.title == 'My new post'

def test_any():
  path = 'content/split.md'
  article = loader.LoadAny(path)
  assert article.source_path == path
  assert isinstance(article, SplitArticle)

def test_index():
  pass

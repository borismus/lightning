import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
EXAMPLE = os.path.join(ROOT, 'example')

from ArticleLoader import ArticleLoader
from Article import *
from Site import SiteConfig


site_config = SiteConfig(type_mapping={'/pages/': 'page', '/posts/': 'post'},
    default_type='page', permalink_formats={'post': 'blog/{{slug}}'})
loader = ArticleLoader(site_config)

def test_simple():
  path = os.path.join(EXAMPLE, 'content', 'simple.md')
  article = loader.LoadArticle(path)
  assert article.source_path == path
  assert article.title == 'My new post'

def test_any():
  path = os.path.join(EXAMPLE, 'content', 'books_all.md')
  article = loader.LoadAny(path)
  assert article.source_path == path
  assert isinstance(article, SplitArticle)

def test_index():
  path = os.path.join(EXAMPLE, 'content', 'books.md')
  article = loader.LoadAny(path)
  assert isinstance(article, IndexArticle)

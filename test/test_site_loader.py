import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
EXAMPLE = os.path.join(ROOT, 'example')
CONFIG = os.path.join(EXAMPLE, 'lightning.yaml')

from SiteLoader import SiteLoader

def test_simple():
  loader = SiteLoader(CONFIG, include_staging=False)
  loader.Load()
  site_config = loader.site_config
  build_config = loader.build_config
  assert len(site_config.articles) > 0
  assert len(site_config.articles) == 9
  assert build_config.content_root == os.path.join(EXAMPLE, 'content')
  assert build_config.template_root == os.path.join(EXAMPLE, 'template')
  assert site_config.title == 'Sample Lightning Blog'


def test_staging():
  loader2 = SiteLoader(CONFIG, include_staging=True)
  loader2.Load()
  site_config = loader2.site_config
  assert len(site_config.articles) == 10


def related_by_permalink(site_config):
  return {a.permalink: [r.permalink for r in a.related]
      for a in site_config.GetFlattenedArticles()}


def test_related_from_site_yaml():
  loader = SiteLoader(CONFIG, include_staging=False)
  loader.Load()
  related = related_by_permalink(loader.site_config)
  assert loader.site_config.related['types'] == ['post', 'book']
  assert related['/lightning'] == ['/about-lightning',
      '/books/homo-deus-by-harari-yes-if-you-havent-read-sapiens']
  # Pages aren't in the configured types, so they neither get nor appear in
  # related lists.
  assert related['/about'] == []
  assert '/about' not in sum(related.values(), [])


def test_related_skipped_for_metadata_only_loads():
  loader = SiteLoader(CONFIG, include_staging=False)
  loader.LoadContent(is_metadata_only=True)
  assert all(r == [] for r in related_by_permalink(loader.site_config).values())

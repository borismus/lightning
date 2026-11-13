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

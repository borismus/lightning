import sys
sys.path.insert(0, './src')

from SiteLoader import SiteLoader

def test_simple():
  loader = SiteLoader(include_staging=False)
  loader.Load()
  site_config = loader.site_config
  build_config = loader.build_config
  assert len(site_config.articles) > 0
  assert len(site_config.articles) == 9
  assert build_config.content_root == 'content'
  assert build_config.template_root == 'template'
  assert site_config.title == 'Sample Lightning Blog'


def test_staging():
  loader2 = SiteLoader(include_staging=True)
  loader2.Load()
  site_config = loader2.site_config
  assert len(site_config.articles) == 10

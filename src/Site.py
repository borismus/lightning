class SiteConfig:
  """A class to hold all of the information about the site, including permalink
  formats."""

  def __init__(self, title='Blog Title', date_format='%B', permalink_formats=[],
      type_mapping={}, default_type=None):
    self.title = title
    self.date_format = date_format
    self.permalink_formats = permalink_formats
    self.type_mapping = type_mapping
    self.default_type = default_type
    self.articles = []


  def SetArticles(self, articles):
    self.articles = articles


  def GetIndexArticles(self):
    """Only return the index articles."""
    pass


class BuildConfig:
  """Holds all of the config information in the lightning.yaml file."""
  def __init__(self, content_root='content', template_root='template',
      output_root='www'):
    self.content_root = content_root
    self.template_root = template_root
    self.output_root = output_root

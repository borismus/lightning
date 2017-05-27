from Article import SplitArticle

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


  def ReplaceArticle(self, article):
    """Given an article, find the one already loaded, and replace it."""
    for index, a in enumerate(self.articles):
      if a.permalink == article.permalink:
        print 'Replaced article %s at index %s.' % (a, index)
        self.articles[index] = article



  def GetFlattenedArticles(self):
    articles = []
    for article in self.articles:
      if isinstance(article, SplitArticle):
        articles += article.children
      else:
        articles.append(article)

    return articles


  def ToDict(self):
    return self.__dict__


class BuildConfig:
  """Holds all of the config information in the lightning.yaml file."""
  def __init__(self, content_root='content', template_root='template',
      output_root='www'):
    self.content_root = content_root
    self.template_root = template_root
    self.output_root = output_root

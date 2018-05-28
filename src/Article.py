import warnings

class Article(object):
  def __init__(self, title, type_name, content, date_created, source_path, slug,
      permalink, snip, output_path, meta_description, yaml):
    # The title of this article.
    self.title = title
    # Name of the template to use for this article.
    self.type_name = type_name
    # Content in markdown format.
    self.content = content
    # Created date in datetime format.
    self.date_created = date_created
    # The source of the article (path on filesystem).
    self.source_path = source_path
    # The output path of the article (on fs)
    self.output_path = output_path
    # Slug.
    self.slug = slug
    # Permalink.
    self.permalink = permalink
    # Snippet.
    self.snip = snip
    # Is it a long article or not?
    self.is_long = (self.snip != self.content)
    # Description used in head <meta> tags.
    self.meta_description = meta_description
    # The raw yaml, for exotic uses.
    self.yaml = yaml

  def GetTemplatePath(self):
    if self.type_name.find('.') >= 0:
      return self.type_name
    return self.type_name + '.html'

  def GetFilename(self):
    return 'index.html'

  def ToDict(self):
    params = self.__dict__
    return params

  def __str__(self):
    return self.permalink


class IndexArticle(Article):
  def __init__(self, type_filter, limit=None, *args, **kwargs):
    super(IndexArticle, self).__init__(*args, **kwargs)

    # Which type of item to filter on.
    self.type_filter = type_filter
    # How many articles to list.
    self.limit = limit
    # List of related articles.
    self.articles = []
    # Whether or not it's an XML feed.
    self.is_feed = self.type_name.endswith('.xml')

    #warnings.warn('Made a new IndexArticle: %s' % str(self.__dict__))

  def SetArticles(self, articles):
    self.articles = articles

  def ToDict(self):
    params = super(IndexArticle, self).ToDict()
    posts = [a.ToDict() for a in self.articles]
    params['posts'] = posts
    return params

  def GetFilename(self):
    return self.is_feed and 'feed.xml' or 'index.html'

  def Match(self, type_name):
    return self.type_filter == '*' or type_name in self.type_filter


class SplitArticle(Article):
  def __init__(self, children, *args, **kwargs):
    super(SplitArticle, self).__init__(*args, **kwargs)
    # List of articles belonging to the split.
    self.children = children
    # Don't actually output anything for this article.
    self.output_path = None


class HomeArticle(IndexArticle):
  def __init__(self, *args, **kwargs):
    super(HomeArticle, self).__init__(*args, **kwargs)

    self.permalink = '/'
    self.output_path = ''

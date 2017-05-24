class Article(object):
  def __init__(self, title, type_name, content, date_created, source_path, slug,
      permalink, snip, output_path):
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

  def GetTemplatePath(self):
    if self.type_name.find('.') >= 0:
      return self.type_name
    return self.type_name + '.html'

  def ToDict(self):
    params = self.__dict__
    return params

  def ToShortDict(self):
    params = self.__dict__
    del params['content']
    del params['snip']
    if 'posts' in params:
      del params['posts']
    return params




class IndexArticle(Article):
  def __init__(self, type_filter, limit, *args, **kwargs):
    super(IndexArticle, self).__init__(*args, **kwargs)

    # Which type of item to filter on.
    self.type_filter = type_filter
    # How many articles to list.
    self.limit = limit
    # List of related articles.
    self.articles = []

  def SetArticles(self, articles):
    self.articles = articles

  def ToDict(self):
    params = super(IndexArticle, self).ToDict()
    posts = [a.ToDict() for a in self.articles]
    params['posts'] = posts
    return params


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

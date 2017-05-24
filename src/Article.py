class Article(object):
  def __init__(self, title, type_name, content, date_created, source_path, slug,
      permalink, snip):
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


class SplitArticle(Article):
  def __init__(self, articles, *args, **kwargs):
    super(SplitArticle, self).__init__(*args, **kwargs)

    # List of articles belonging to the split.
    self.articles = articles

  def GetTemplatePath(self):
    return self.articles[0].type_name + '.html'

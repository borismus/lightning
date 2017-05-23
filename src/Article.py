class Article:
  def __init__(self, title, type_name, slug, content, permalink, date_created, source_path):
    # The title of this article.
    self.title = title
    # Name of the template to use for this article.
    self.type_name = type_name
    # Short name (eg. my-new-post)
    self.slug = slug
    # Content in markdown format.
    self.content = content
    # Permalink (eg. /hihi/2017/my-new-post).
    self.permalink = permalink
    # Created date in datetime format.
    self.date_created = date_created
    # The source of the article (path on filesystem).
    self.source_path = source_path


class IndexArticle(Article):
  def __init__(self):
    # Which type of item to filter on.
    self.type_filter = None
    # How many articles to list.
    self.limit = None


class SplitArticle(Article):
  def __init__(self, articles, source_path):
    self.articles = articles
    self.source_path = source_path

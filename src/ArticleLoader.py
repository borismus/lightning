import markdown2
import re
import yaml

from Article import *
from BuildException import BuildException
from Utils import *

class ArticleLoader:
  def __init__(self):
    pass


  def LoadAny(self, path):
    """Loads any type of article, and determines the type of the article later.
    This can return an Article, IndexArticle or SplitArticle.

    Type of article is determined by YAML header called class."""
    # Determine what the article type is based on the YAML metadata.
    f = open(path, 'rU')
    lines = f.readlines()
    data = GetYamlMetadata(lines)
    class_name = data['class'] if ('class' in data) else 'default'

    if class_name == 'index':
      return self.LoadIndexArticle(path)
    elif class_name == 'split':
      return self.LoadSplitArticle(path)
    else:
      return self.LoadArticle(path)


  def LoadArticle(self, path, lines=[]):
    """Parses markup from files like this:

      My new post
      ===========
      type: post
      posted: 2012-03-01 9:00
      slug: my-new-post
      snip: A short summary of what's written in the post.

      Just **testing**

    into an Article representing it.
    """
    source_path = path
    if not lines:
      # Load the file.
      f = open(path, 'rU')
      lines = f.readlines()

    if len(lines) == 0:
      raise BuildException('Unable to load article %s: content missing.' %
          source_path)

    data = GetYamlMetadata(lines)

    if type(data) != dict:
      raise BuildException('Expected dictionary YAML header for %s.' \
          % source_path)

    # Process the rest of the post as Markdown.
    separator_index = lines.index('\n')
    markdown_lines = lines[separator_index+1:]
    markdown_body = ''.join(markdown_lines).decode('utf-8')
    content = markdown2.markdown(markdown_body)
    # If there's no snip specified, try to parse it before the <!--more--> tag.
    snip = 'snip' in data and markdown2.markdown(data['snip']) \
                           or ParseSnip(content)

    # Save a bunch of properties.
    snip = snip or content
    title = unicode(data['title'], 'utf8')
    content = content
    # Infer slug and type from path.
    slug = 'slug' in data and data['slug'] or GuessSlug(path)
    type_name = 'type' in data and data['type'] or GuessType(path)
    summary = markdown_body[:markdown_body.find('.')+1]
    date_created = None
    if 'posted' in data:
      # Parse the date if it's specified.
      date_created = ParseDate(data['posted'])
    else:
      # Otherwise, guess the date based on the directory structure.
      date_created = GuessDate(path)
      if not date_created:
        raise BuildException('No date specified and failed to guess date from \
            path %s.' % source_path)
    # Compute the permalink.
    try:
      permalink = ComputePermalink(type_name, slug, date_created)
    except Exception as e:
      raise BuildException('Failed to compute permalink for %s: %s' % (slug, e))

    return Article(title=title, type_name=type_name, slug=slug, permalink=permalink,
        content=content, date_created=date_created, source_path=source_path)


  def LoadSplitArticle(self, path):
    """If we're dealing with a split article, we have to split the file into
    separate files, and handling each one separately, and then creating an
    Article for each and linking them together in a SplitArticle."""
    f = open(path, 'rU')
    lines = f.readlines()

    # Look for splits in the file, in the form \nTITLE\n=====\n\n.
    split_indices = FindSplitIndices(lines)

    # Separate the file based on split indices, and load an article for each.
    split_indices.insert(0, 0)
    split_indices.append(len(lines) - 1)

    articles = []
    for start, end in Pairwise(split_indices):
      subset = lines[start:end]
      article = self.LoadArticle(path, lines=subset)
      articles.append(article)

    return SplitArticle(articles, source_path=path)

  def LoadIndexArticle(self, path):
    pass

if __name__ == '__main__':
  import doctest
  doctest.testmod()

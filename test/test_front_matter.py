import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

from ArticleLoader import ArticleLoader
from Article import SplitArticle
from BuildException import BuildException
from Site import SiteConfig
from Utils import ParseFrontMatter, FindEntryStarts


def test_parse_front_matter():
  data, body = ParseFrontMatter('---\ntitle: "Hot bread: deadly?"\n'
      'posted: May 1, 2020\n\ntags: [a]\n---\n\nHello\n\n---\n\nWorld\n')
  assert data == {'title': 'Hot bread: deadly?', 'posted': 'May 1, 2020',
      'tags': ['a']}
  assert body == 'Hello\n\n---\n\nWorld\n'


@pytest.mark.parametrize('text, message', [
  ('Title\n===\n\nbody', 'expected file to start with "---"'),
  ('---\ntitle: x\n\nbody', 'missing its closing "---"'),
  ('---\ntitle: [x\n---\n', 'invalid YAML'),
  ('---\n- a list\n---\n', 'must be a YAML mapping'),
])
def test_parse_front_matter_errors(text, message):
  with pytest.raises(BuildException, match=message):
    ParseFrontMatter(text, 'f.md')


def test_find_entry_starts_ignores_rules_and_code():
  body = '\n'.join([
    '---',              # 0: entry
    'title: One',
    '---',
    'text',
    '---',              # 4: horizontal rule
    '',
    '```',
    '---',              # 7: inside a code fence
    'title: not an entry',
    '```',
    '---',              # 10: entry
    'title: Two',
    '---',
  ])
  assert FindEntryStarts(body) == [0, 10]


def write(tmp_path, name, text):
  path = tmp_path / name
  path.write_text(text)
  return str(path)


def loader():
  return ArticleLoader(SiteConfig(permalink_formats={'book': 'books/{{slug}}'},
      default_type='page'))


def test_split_article(tmp_path):
  path = write(tmp_path, 'books.md', '---\nclass: split\ntype: book\n---\n\n'
      '---\ntitle: First Book\nrating: yes\n---\n\nGood.\n\n---\n\nStill good.\n'
      '\n---\ntitle: Second Book\n---\n\n# Heading inside entry\n\nMeh.\n')
  article = loader().LoadAny(path)
  assert isinstance(article, SplitArticle)
  first, second = article.children
  assert first.title == 'First Book'
  assert first.yaml['rating'] is True  # YAML 1.1 reads yes as true
  assert '<hr />' in first.content and 'Still good.' in first.content
  assert first.permalink == '/books/first-book'
  assert second.title == 'Second Book'
  assert '<h1>Heading inside entry</h1>' in second.content


def test_split_article_errors(tmp_path):
  no_entries = write(tmp_path, 'a.md', '---\nclass: split\n---\n\njust text\n')
  with pytest.raises(BuildException, match='no entries'):
    loader().LoadAny(no_entries)

  stray = write(tmp_path, 'b.md', '---\nclass: split\n---\n\noops\n\n'
      '---\ntitle: A\n---\n\nbody\n')
  with pytest.raises(BuildException, match='content before the first entry'):
    loader().LoadAny(stray)

  unclosed = write(tmp_path, 'c.md', '---\nclass: split\n---\n\n'
      '---\ntitle: A\nposted: May 1\n\nbody without closing delimiter\n')
  with pytest.raises(BuildException, match=r'c.md:5: front matter is missing'):
    loader().LoadAny(unclosed)


def test_article_requires_title(tmp_path):
  path = write(tmp_path, 'post.md', '---\nposted: May 1, 2020\n---\n\nbody\n')
  with pytest.raises(BuildException, match='no title'):
    loader().LoadAny(path)

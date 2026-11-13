import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from Article import Article
from Related import ComputeRelated, LinkedPermalinks, Tokenize


def article(slug, title, content, type_name='post', yaml=None):
  return Article(title=title, type_name=type_name, content=content,
      date_created=None, source_path=slug + '.md', slug=slug,
      permalink='/' + slug, snip='', output_path=slug, meta_description='',
      yaml=yaml or {})


def related_slugs(a):
  return [r.slug for r in a.related]


def test_tokenize_drops_stopwords_and_folds_plurals():
  assert Tokenize("The models' studies of a Model") == \
      ['model', 'study', 'model']


def test_linked_permalinks_normalizes_hrefs():
  a = article('a', 'A', '<a href="https://example.com/b/#x">b</a> '
      '<a href="/c/?q=1">c</a> <a href="https://other.com/d/">d</a> '
      '<a href="#top">top</a>')
  assert LinkedPermalinks(a, 'https://example.com') == {'/b', '/c'}


SAILING = '<p>Sailing boats need wind, sails, a keel and a rudder.</p>'
SAILING_2 = '<p>Racing boats trim sails to the wind; the keel resists.</p>'
BAKING = '<p>Baking bread takes flour, water, yeast and a hot oven.</p>'
BAKING_2 = '<p>Sourdough bread uses wild yeast, flour and a long proof.</p>'


def corpus():
  return [article('sail', 'Sailing', SAILING),
          article('race', 'Racing', SAILING_2),
          article('bake', 'Baking', BAKING),
          article('sourdough', 'Sourdough', BAKING_2)]


def test_finds_the_similar_article():
  sail, race, bake, sourdough = corpus()
  ComputeRelated([sail, race, bake, sourdough], {'limit': 1})
  assert related_slugs(sail) == ['race']
  assert related_slugs(bake) == ['sourdough']


def test_min_score_drops_weak_matches():
  articles = corpus()
  ComputeRelated(articles, {'limit': 3, 'min_score': 0.1})
  # Sailing and baking share no words, so they never relate.
  assert related_slugs(articles[0]) == ['race']


def test_min_count_drops_articles_with_too_few_matches():
  sail, race, bake, sourdough = corpus()
  ComputeRelated([sail, race, bake, sourdough], {'min_count': 2})
  # Each article has only one good match, so none get a related list.
  assert all(a.related == [] for a in (sail, race, bake, sourdough))

  sail, race, bake, sourdough = corpus()
  sail.content += '<a href="/bake/">unrelated link</a>'
  ComputeRelated([sail, race, bake, sourdough], {'min_count': 2})
  # The link gives sailing and baking a second match each.
  assert sorted(related_slugs(sail)) == ['bake', 'race']
  assert sorted(related_slugs(bake)) == ['sail', 'sourdough']
  assert race.related == [] and sourdough.related == []


def test_link_bonus_relates_linked_articles():
  sail, race, bake, sourdough = corpus()
  sail.content += '<a href="/bake/">unrelated link</a>'
  ComputeRelated([sail, race, bake, sourdough], {'limit': 3})
  assert 'bake' in related_slugs(sail)
  # Links count in both directions.
  assert 'sail' in related_slugs(bake)


def test_only_configured_types_participate():
  sail, race, bake, sourdough = corpus()
  race.type_name = 'page'
  ComputeRelated([sail, race, bake, sourdough], {'types': ['post']})
  assert related_slugs(sail) == []
  assert race.related == []


def test_headline_counts_as_title():
  memento = article('memento', 'Memento Mori',
      '<p>Contemplating mortality and memento mori.</p>')
  review = article('ivan', 'The Death of Ivan Ilyich', '<p>A novella.</p>',
      type_name='book', yaml={'headline': 'Is Memento Mori Futile?'})
  ComputeRelated([memento, review] + corpus(),
      {'types': ['post', 'book'], 'limit': 1})
  assert related_slugs(memento) == ['ivan']

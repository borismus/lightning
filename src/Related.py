"""Finds related articles by text similarity, without any external services.

Each article becomes a TF-IDF vector over its words (title words count
extra), and articles are compared by cosine similarity. Articles that link to
each other get a bonus, since an explicit link is strong evidence. Matches
below a minimum score are dropped, so an article with no good match gets no
related section rather than a weak one. Likewise, an article with fewer than
min_count good matches gets none, so a lone weak-ish card never shows.

Enable it in site.yaml:

  related:
    types: [post, note, book]   # which articles get, and can be, related
    limit: 3                    # max related articles per article
    min_score: 0.1              # drop weaker matches
    min_count: 2                # show none unless at least this many match
"""
import collections
import html
import math
import re

DEFAULTS = {'types': ['post'], 'limit': 3, 'min_score': 0.1, 'min_count': 1}
TITLE_WEIGHT = 3
LINK_BONUS = 0.15

STOPWORDS = set('''
a about above after again against all also am an and any are as at be because
been before being below between both but by can could did do does doing done
down during each even few for from further get got had has have having he her
here hers herself him himself his how however i if in into is it its itself
just let like lot made make many may me might more most much must my myself no
nor not now of off often on once one only or other our ours ourselves out over
own really same she should since so some something still such than that the
their theirs them themselves then there these they thing things this those
though through to too two under until up upon us use used using very via was
way we well were what when where which while who whom why will with without
would yet you your yours yourself yourselves
'''.split())

TAG = re.compile(r'<[^>]+>')
CODE = re.compile(r'<(pre|code)[^>]*>.*?</\1>', re.DOTALL)
HREF = re.compile(r'href="([^"]+)"')
WORD = re.compile(r"[a-z][a-z'-]*[a-z]")


def Tokenize(text):
  words = []
  for word in WORD.findall(text.lower()):
    word = word.replace("'", '')
    if len(word) < 3 or word in STOPWORDS:
      continue
    words.append(Stem(word))
  return words


def Stem(word):
  """Folds simple plurals together (models -> model, studies -> study)."""
  if len(word) > 4 and word.endswith('ies'):
    return word[:-3] + 'y'
  if len(word) > 3 and word.endswith('s') and not word.endswith(('ss', 'us', 'is')):
    return word[:-1]
  return word


def ArticleText(article):
  body = html.unescape(TAG.sub(' ', CODE.sub(' ', article.content or '')))
  # Book reviews can have a headline in addition to the book's title.
  title = ' '.join(str(t) for t in (article.title,
      article.yaml.get('headline')) if t)
  return (title + ' ') * TITLE_WEIGHT + body


def LinkedPermalinks(article, domain):
  """Permalinks of the articles this one links to, normalized like
  article.permalink (no domain, fragment, or trailing slash)."""
  links = set()
  for href in HREF.findall(article.content or ''):
    if domain and href.startswith(domain):
      href = href[len(domain):]
    if not href.startswith('/'):
      continue
    href = href.split('#')[0].split('?')[0].rstrip('/')
    if href:
      links.add(href)
  return links


def Vectorize(token_lists):
  """Returns a unit-length TF-IDF vector (dict) per token list. Words found
  in only one document can't make documents similar, so they're dropped."""
  n = len(token_lists)
  df = collections.Counter(w for tokens in token_lists for w in set(tokens))
  vectors = []
  for tokens in token_lists:
    tf = collections.Counter(tokens)
    vector = {w: (1 + math.log(c)) * math.log(n / df[w])
        for w, c in tf.items() if df[w] > 1}
    norm = math.sqrt(sum(x * x for x in vector.values())) or 1
    vectors.append({w: x / norm for w, x in vector.items()})
  return vectors


def Similarities(vectors):
  """Cosine similarity of every pair of unit vectors, as one dict per vector
  mapping other vector index -> score. Walks a word index so pairs that share
  no words cost nothing."""
  postings = collections.defaultdict(list)
  for j, vector in enumerate(vectors):
    for w, x in vector.items():
      postings[w].append((j, x))
  similarities = []
  for i, vector in enumerate(vectors):
    scores = collections.defaultdict(float)
    for w, x in vector.items():
      for j, y in postings[w]:
        scores[j] += x * y
    scores.pop(i, None)
    similarities.append(scores)
  return similarities


def ComputeRelated(articles, config, domain=''):
  """Sets article.related to a list of the most similar articles, best first,
  for every article whose type is in config['types']."""
  config = dict(DEFAULTS, **(config or {}))
  candidates = [a for a in articles if a.type_name in config['types']]
  similarities = Similarities(
      Vectorize([Tokenize(ArticleText(a)) for a in candidates]))
  links = [LinkedPermalinks(a, domain) for a in candidates]

  for i, article in enumerate(candidates):
    scored = []
    for j, other in enumerate(candidates):
      if i == j:
        continue
      score = similarities[i].get(j, 0)
      if other.permalink in links[i] or article.permalink in links[j]:
        score += LINK_BONUS
      if score >= config['min_score']:
        scored.append((score, other.permalink, other))
    if len(scored) < config['min_count']:
      scored = []
    scored.sort(key=lambda s: (-s[0], s[1]))
    article.related = [other for _, _, other in scored[:config['limit']]]

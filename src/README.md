Five years later, I still really like the Lightning source directory structure.
I still really like Markdown, and writing in vim, and keeping a static blog.
However, I want to add a feature to the engine: multiple articles generated from
one markdown file. This has triggered a refactor/rewrite.

Lightning V1 was a single python file. It wasn't well structured or testable or
conceptually sound. Here's a rough architecture:

- ArticleLoader loads Articles from file system.
- Article represents a post or a page or a book review or whatever. Each article
  has markdown and metadata and generates one HTML file.
  - A SplitArticle is composed of a list of Articles (eg. my book reviews page).
  - A IndexArticle is a type of Article that is an index of other articles (eg.
    the main page, or an archives page).
- A Site contains a list of Articles and some metadata (see site.yaml)
- An IncrementalHelper keeps track of the last built site and, given a
  list of changed files, returns a new Site with just the updated articles.
- A SiteBuilder takes a Site and generates its entire HTML. It also knows how to
  remove already built paths from the filesystem.

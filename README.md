# TODO

Before blog update:

- Pagespeed
- Post describing change
- Better headshot
- Pack it up into a convenient installation (including inotify, dropbox, etc).

Before lightning release:

- Should there be a git repo clone involved?
- submit to pypi
- BUG: What about including `{{...}}` in the markup?
- Unit test and refactor.
- Refactoring into classes.

### Done

- Check all assets for posts, make them inline if needed.
- Analytics
- text distinctions based on post type (talk, link, article)
- graphical permalink (ב)
- Change quote image.
- Migrate all content to new blog.
- Generate RSS feed.
  - one for all posts
  - one for all links

- Make a new type for talks
- More compact archive page
- Does it work well with inotify? How about cron?
- Integrate with dropbox.
- Fix boris.smus.com to work :)
- Make links actually link out
- Publish assets that are stored in the content directory (only if
  associated file changes).
- Try out with real content, porting existing blog.
- Respect the `<!--more-->` tag for excerpts, with a snip attribute as
  an alternative.
- Fix position of the read more thingy
- Responsive styles for different sizes
- Code snippets syntax highlight.
- Archive page (with filtering)

## Lightning features

- One-step to add a new post (eg. a link)
- Static output
- Use any editor
- Uses existing DSLs: Markdown (content) + YAML (metadata) + Mustache (template)
- Simple logic-less templates
- Ability to work offline
- Logical placement of assets (content-related ones near the content,
  layout ones in the template)
- Fast builds
- Content directory format is decoupled from output.

### Important design decisions:

* Build should never change the source tree (with the exception of moving
  published drafts into the main site).
* There must be no server-side component. No rewrite rules, no scripts,
  etc.

## Installation

1. Clone this repository.
2. Run `pip something` to install all of the dependencies.
3. Run engine/builder.py on a regular basis (cron job or via inotify).

### Dependencies

* PyYAML==3.10
* markdown2==1.1.1
* pystache==0.4.0

Or just install via pip. TODO: more details.

## Commands

To build, simply run `make`. This will do an incremental build and create
a `/web` directory with your static output.

To force a non-incremental build, run `make rebuild`.

To deploy to a server, run `make deploy`.

To make a new link post, run `make link`.

## Directory structure

* `/content/` contains files written in Markdown, with a customized header.
* `/site.yaml` is the site-wide configuration.
* `/template/` contains files written in HTML and Mustache templates.

## Building one page

At build time, a content file is transformed into an object that's used
to populate the Mustache template. Content can either be a file.txt
somewhere, or a directory with an index.txt inside. The latter lets you
include other files related to the post.

For example, content like this:

    My new post
    ===========
    type: post
    posted: 2012-03-01 9:00am
    slug: my-new-post

    Just **testing**

    1. Hello
    2. World

Gets transformed into the following data:

    {
      "title": "My new post",
      "type": "post",
      "slug": "my-new-post",
      "published": "2012-03-01 9:00am",
      "content": "Just <b>testing</b> <ol><li>Hello</li><li>World</li></ol>"
    }

Additionally, contents of the global site.yaml, which looks like:

    title: My awesome blog
    permalinks:
      post: {{year}}/{{slug}}
      page: {{slug}}

are added to the template payload:

    {
      "site_title": "My awesome blog"
      "site_permalinks": {
        "post": "{{year}}/{{slug}}",
        "page": "{{slug}}"
      }
    }

Then, once we resolve the template to use (in this case, the post
template):

    <!doctype html>
    <head>
      <title>{{title}} | {{site_title}}</title>
    </head>
    <article>
      {{content}}
    </article>
    <date>
    {{published}}
    </date>

It gets populated with the data, resulting in the following output:

    <!doctype html>
    <head>
      <title>My new post | My awesome blog</title>
    </head>
    <article>
      Just <b>testing</b> <ol><li>Hello</li><li>World</li></ol>
    </article>

Next, the engine looks at the configured permalink structure set in the
site.yaml configuration to decide where to place the output. In this
case, the `post` value of `site_permalinks` is `{{year}}/{{slug}}`, so
year will be populated from {{published}}, resulting in
`2012/my-new-post`.

To avoid rewrite rules, the engine creates a directory with the output,
and creates an index.html inside of it.

Also, if there are assets associated with the article, they are copied
into the corresponding directory. 

## Building it all

Broadly, there are two kinds of templates: single page ones, and ones
that require a list of articles. The engine uses a convention: the
"page" and "post" type are single-source, and "archive" type is
multi-source.

Single-source pages are all described above.

### Multi-source pages

Multi-source pages have an additional `list` value passed into them,
with optional additional values: `filter` and `limit`. For example:

    All links
    =========
    type: archive
    filter: link
    list

    This is a list of all links ever written.

The list value results in an extra property being passed to the
template, called list. The list property will contain a list of articles
requested:

    [
      {
        "title": "My new post",
        "type": "post",
        "slug": "my-new-post",
        "published": "2012-03-01 9:00am",
        "content": "Just <b>testing</b> <ol><li>Hello</li><li>World</li></ol>"
      }, ...
    ]

## Incremental building

Every time we run a build, need to know which files have been changed
since the last build.

Solution is to dump a cache of files, their modification times and other
details required by the list as of the last build:

    {
      "path": "index.txt",
      "modified": NNNN,
      "info": {...}
    }

This cache is stored in `/web/.last_build`. Strategy is to generate this
cache on build, and see which files differ.

1. Build each changed file.
2. Build every list file.
3. Update the cache and save it, replacing the old one.

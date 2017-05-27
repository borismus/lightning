Lightning is a static blogging engine designed to make it painless to author and
update large blogs. 

- Clear separation between content and templating.
- Assets that you can store alongside content (in the same directory).
- Split posts so that you can write multiple shortform articles in the same
  markdown file.
- Incremental building.
- Use your favorite editor for everything.

# Installation

1. Clone the repository via `git clone git@github.com:borismus/lightning.git`
2. Run `cd lightning` to get to your newly cloned repository.
2. Install all required dependencies by running `pip install -r requirements.txt`.
4. Take a look at [template][] and [content][] for my blog at <http://smus.com>.

[template]: https://github.com/borismus/smus.com-template
[content]: https://github.com/borismus/smus.com

# Usage

Build your site by running ./lightning in the current working directory. This
will read your lightning.yaml and go from there.

I used livereload to build a preview script:

    #!/usr/bin/env python
    from livereload import Server, shell

    server = Server()
    server.watch('content', shell('../lightning/lightning -o www'))
    server.serve(root='www')

And host my static site on github pages, which I deploy to using this script:

    #!/usr/bin/env sh

    DEPLOY_PATH=/Users/smus/Projects/smus.com-deploy

    # Do a deploy build to the smus.com gh-pages repo.
    ../lightning/lightning --out=$DEPLOY_PATH

    # Commit the updated contents there, and push it upstream.
    pushd $DEPLOY_PATH
    git add -A
    git commit -m "Updating smus.com with new content."
    git push origin gh-pages
    popd


# Configuration

`lightning.yaml` specifies where to look for content, template and where
to dump output.

`site.yaml` specifies metadata about the site itself. A [simple
example][site.yaml] is at [content/site.yaml][site.yaml].

[site.yaml]: https://github.com/borismus/smus.com/blob/master/site.yaml

Lightning is a static blogging engine designed to make it painless to
author and update large blogs. Key features are:

- Standalone content directory.
- Incremental building.
- Easy-to-author configuration.
- Use your favorite editor for everything.

Here's a preview of [publishing using lightning][flow] once you're set up.

# Installation

1. Clone the repository via `git clone git@github.com:borismus/lightning.git`
2. Run `cd lightning` to get to your newly cloned repository.
2. Install all required dependencies by running `pip install -r requirements.txt`.
3. Run `./lightning` to build and `./lightning preview` to run a
   webserver.
4. Open <http://localhost:8000> in your browser.

# Usage

Build incrementally.

    > ./lightning

Forcibly rebuild everything regardless of whether or not there have been
changes made to the content. This is useful if you change your template.

    > ./lightning rebuild

Start watching for local changes to the content, rebuilding
incrementally based on that.

    > ./lightning watch

Start a really simple local web server with its document root pointing
to the output directory.

    > ./lightning preview

Deploy the site to the specified S3 bucket.

    > ./lightning deploy


# Configuration

`lightning.yaml` specifies where to look for content, template and where
to dump output. It also specifies where to deploy the site.

`site.yaml` specifies metadata about the site itself, including
permalinks, verbs, site title, date format. It belongs in the content
root.


# For production

I use a combination of Dropbox and Lightning (which uses inotify-tools)
to make for a [pleasant blogging experience][flow]. Here are the steps to get
Lightning working on your server.

0. Install Dropbox on your [server][dropbox].
1. Install Lightning on your server (see above).
2. Customize your theme.
3. Configure `lightning.yaml` to look for your content on Dropbox (eg.
   `~/Dropbox/my-blog/`)
4. Setup a watcher on your server via `lightning watch`. It's useful to
   run the watcher using `nohup`.
5. Make some changes to your content directory from any Dropbox client
   (I sometimes use [Nebulous][nebulous] on iPad).
6. You're done.

[Enjoy][flow].

[dropbox]: https://www.dropbox.com/install?os=lnx
[nebulous]: http://nebulousapps.net/
[flow]: http://www.youtube.com/watch?v=z6ZH2DyURU4


From Wordpress to Hyde
======================
categories: [web]
posted: 2011-04-20
snip: or, how I stopped worrying and switched this blog to a Django static site generator.




I've used [Wordpress][] for a couple of years now as my web publishing platform of
choice. I customized it a little bit, and made a [custom theme][] for it. But 
nothing is perfect, and neither is wordpress. As a result of relatively heavy
use, I've collected a list of things I don't much like about it:

* Can't upload source code since it restricts allowed file types.
* Can't easily edit files with a regular text editor.
* Painful theme customization.
* PHP makes it unpleasant to extend.
* Constant security upgrades required.

All of these things separately are perhaps small and insignificant, but
together add up to create a certain barrier to blogging.
## Static files

A blog is mostly static. Why should my article be stored in a database? It's hardly 
ever queried or searched. Comments are perhaps the exception here, but services
like [Disqus][] implement commenting with embeddable JavaScript. And in general,
dynamic parts can be handled in client-side code.

So I looked to static site generators. There's about [a million][] of these,
the most prominent of which is [Jekyll][], written by the github co-founder. 
Ultimately I chose [Hyde][] for it's use of [Django templates][] and Python.

## Migrating the old blog

The old blog was written in HTML, but I wanted to switch to a format that can
be written faster, such as Markdown, Textile, or many others. To do this I used
a tool called exitwp, which parses the Wordpress export and generates Markdown
files appropriate for Jekyll. I [forked exitwp][] and hacked it to generate
files better suited to Hyde. Thanks [Thomas Frössman][] for exitwp.

I did spent a fair amount of time tweaking the export, replacing Smart YouTube URLs
with real YouTube embeds, and eliminating Syntax Highlighter markup.

## Customizing hyde

Hyde is basically built on top of Django templates, so is customizable with
template tags and filters, written in Python. It comes with a bunch of them,
including ones that parse markdown and other structured text formats into HTML.

Surprisingly I didn't need to customize Hyde much, although I did fix a couple of 
bugs, which the author, [Lakshmi Vyas][] accepted. Anyway, I feel much more
future proof now than with Wordpress, since I can easily write extensions in
Python, or in the worst case take my Markdown-formatted blog posts and easily
export them to many different formats.

## Dynamic stuff

The bit of custom JS for the site layout is written using jQuery.

I use the excellent [highlight.js][] plugin to highlight code snippets. The
jQuery [timeago][] plugin does a great job of converting absolute dates (April
1, 2010) to relative dates (about a year ago). Finally, Disqus powers comments,
which I migrated from the wordpress database.

## New design

In my great wisdom, I decided that since there's so much flux in the blog, why not
add some more chaos by switching to a new layout too? Here's the old layout:

![old][]

I recently heard from sage advice from some experienced writers. Among things
that stuck were:

* Optimal posting time is 9am PST
* Writing personal posts is OK sometimes
* Show personal information in the sidebar

The last part is expressed in the new design. Overall the redesign was an
exercise in typography, CSS3 features and [responsive layout][]. 

[Google fonts][] is a nice collection of web fonts. I decided to switch from
Myriad (used on borismus.com) to a serif for the main body for a
change. I ultimately went with [PT Serif][], which seemed like a nice
improvement to Georgia, which is probably my favorite serif web font.

I used a bunch (too many?) CSS3 features on the new site. Most of these are
CSS box-shadows, gradients, transformations and transitions. I used [SCSS][].

Also, following the responsive layout philosophy, I wanted the site to scale well
to a number of different resolutions. For example, the sidebar moves to the end of the 
articles if the window is too narrow. Also, in the [projects page][], the number of 
columns of projects is flexible. This is achieved through [CSS media queries][].

For posterity, here is the new layout at the time of writing:

![new][]

## New domain

I also recently bought [smus.com][] from a fellow in Germany, and will be migrating 
my site there. I'll keep the [borismus.com][] blog intact for a while, but will 
place an annoying banner there, and disable commenting. I guess I should also 
switch the feedburner feed to point to smus.com as well.

Not long ago, I wrote about how switching from webfaction and apache to slicehost
and NGINX greatly [enhanced page load time][]. Well, this seems to have happened again.
Over the same time period, the average response time of my wordpress instance was 
**934ms**:

![old perf][]

Over the same time frame, my static blog, hosted on the same machine, responded on 
average in **371ms**:

![new perf][]

Oh, finally, the site is fully open source [on github][]. 

## Thanks

Thanks to a bunch of people:

- Sol, Kat and Jon for giving useful design feedback!
- [Noah Levin][] for awesome CSS3 tweaks
- Steve Losh for his [Hyde migration][] write-up

You, for reading this post and continuing to read this blog. Until next time!

[Wordpress]: http://wordpress.com/
[custom theme]: /new-design
[a million]: http://stackoverflow.com/questions/186290/best-static-website-generator
[Django templates]: http://docs.djangoproject.com/en/dev/ref/templates/builtins/
[Disqus]: http://disqus.com/
[Hyde]: https://github.com/lakshmivyas/hyde/
[forked exitwp]: https://github.com/borismus/exitwp
[Thomas Frössman]: http://thomas.jossystem.se/
[Lakshmi Vyas]: http://ringce.com/
[Noah Levin]: http://nlevin.com/
[Google fonts]: http://www.google.com/webfonts
[Hyde migration]: http://stevelosh.com/blog/2010/01/moving-from-django-to-hyde/
[Jekyll]: https://github.com/mojombo/jekyll
[responsive layout]: http://www.alistapart.com/articles/responsive-web-design/
[CSS media queries]: http://www.w3.org/TR/css3-mediaqueries/
[projects page]: /projects
[smus.com]: http://smus.com
[borismus.com]: http://borismus.com
[highlight.js]: http://softwaremaniacs.org/soft/highlight/en/
[timeago]: http://timeago.yarp.com/
[PT Serif]: http://www.google.com/webfonts/list?family=PT+Serif
[enhanced page load time]: /lightweight-wordpress-on-slicehost/
[on github]: http://github.com/borismus/smus.com
[SCSS]: http://sass-lang.com/

[old]: old-design.png
[new]: new-design.png
[old perf]: old-perf.png
[new perf]: new-perf.png



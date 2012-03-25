I See Dead CSS
==============
categories: [web]
posted: 2008-12-11
snip: A rudimentary attempt to write a tool that detects unused CSS styles in a stylesheet.



I wanted a tool that would analyze a complete web site, and report what
CSS selectors and IDs are dead. By dead, I mean one of two things --
either the ID or selector is referenced from the HTML and undefined in
the CSS or it is defined in the CSS but never referenced in the HTML.

A search for some CSS finding utilities proved somewhat fruitful. I
found a brief [survey of related utilities][] for this finding or
cleaning dead CSS, the most promising of which was a Firefox plug-in
called [Dust-Me Selectors][]. But I wanted something that could be
integrated into an automatic build process, easily invokable from the
command line without requiring a browser, so I started thinking about a
custom solution.

The problem can be solved as follows:

1.  Find all referenced IDs and classes, called R
2.  Find all defined IDs and classes, called D
3.  Take a difference between the sets so that the list of undefined IDs
    and classes is (R - D), and the list of unreferenced IDs and classes
    is (D - R)

I've already had the pleasure of using [BeautifulSoup][] python library
to parse all sorts of HTML documents, and I quickly found [cssutils][]
to be a very handy CSS parser. In a matter of hours I was able to whip
up a basic dead CSS finder in 100 lines of code using these great tools.
I named it 7sense, after [the movie][]. To run it, you just need to
invoke `./7sense.py <list of files and directories>` and the specified
files will be parsed as if they were all part of the same webpage.
Directories will be walked recursively, with all encountered CSS and
HTML files assumed to be part of the web page.

But things are not as simple as I had hoped, and my program has several
notable limitations.

1.  Due to lack of time, 7sense does not look at what stylesheets are
    referenced by an HTML page. Instead, you have to tell it explicitly
    what stylesheets are used by passing them as arguments.
2.  7sense does not properly decipher heirarchical CSS selectors like
    '\#myContainer .aboutBox'. Instead, it splits the selector into
    whitespace separated tokens, ignoring their structure. I skimped on
    this feature also due to lack of time.
3.  More fundamentally, 7sense is not aware of any Javascript
    modifications to the DOM. This could be remedied on a case-by-case
    basis. For example, one could write a parser to seek jQuery.setClass
    invocations, and extract additional classes from there.

At any rate, here's [7sense so far][]. Though flawed, it's a useful
start. Ideas and code improvements, especially addressing the above
limitations are very much appreciated!

  [survey of related utilities]: http://www.aggiorno.com/blogs/aggiornings/post/Detecting-unused-CSS-selectors-.aspx
  [Dust-Me Selectors]: http://www.sitepoint.com/dustmeselectors/
  [BeautifulSoup]: http://www.crummy.com/software/BeautifulSoup/
  [cssutils]: http://cthedot.de/cssutils/
  [the movie]: http://www.imdb.com/title/tt0167404/
  [7sense so far]: http://www.borismus.com/wp-content/uploads/2008/12/7sense.py


Chronos: Chrome Browsing Metrics
================================
categories: [web, chrome, statistics]
posted: 2011-03-21
snip: Ever wondered how much time you spend in your browser?



Like most people, I'm slowly lifting most of my work into the cloud.
This leads to a lot of time spent in the browser. Just how much, I'm not
really sure. Enter [Chronos][], a Chrome extension to track how much
time you spend on each domain you visit. Chronos gives a per-day
breakdown of time spent actively browsing. In addition to showing a
graphical summary of domain frequency, you also get a total time spent
in Chrome, and how much time your Chrome spends idle.

Chronos, named after the Greek god of time, quietly sits and monitors
keyboard and mouse events you generate. If you've been active recently,
the domain you're visiting gets recorded. The data structure that stores
this timing information persists on the client side using localStorage.
This data is never sent to any servers, so your browsing privacy is
preserved. Chronos' visualization is built out of HTML divs. Just for
fun, if you become inactive in Chrome, the Chronos icon in the
extensions toolbar fades out.

Some features that I would find useful to
add to Chronos revolve around productivity and time management:

1.  Chronos makes it really obvious which sites consume most of your
    time. It would make sense to be able to enforce time limits spent on
    sites, either by interfacing with an extension like [StayFocusd][],
    or by replicating that functionality.
2.  Many people find it helpful to be reminded to take breaks from
    computing, either for RSI purposes or for general productivity.
    Chronos already tracks activity levels in Chrome, so it could be
    augmented to remind people to take breaks in a way similar to
    [AntiRSI][].

Have a great idea to add to Chronos? Let me know, or add it yourself! As
usual, the [source code][] is on github.

  [Chronos]: https://chrome.google.com/extensions/detail/dbgohgmphghmoghphoiaghbopikmmgop/
  [StayFocusd]: https://chrome.google.com/extensions/detail/laankejkbhbdhmipfmgcngdelahlfoji
  [AntiRSI]: http://tech.inhelsinki.nl/antirsi/
  [source code]: https://github.com/borismus/Chronos


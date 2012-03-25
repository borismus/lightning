jQuery Conference 2011
======================
categories: [web, conference]
posted: 2011-04-26
snip: I went to the Bay Area jQuery Conference and learned some interesting things.




A few weekends ago I went to the jQuery Conference held at the MS campus in
Mountain View. And I took notes!

Overall trends about the jQuery community:

* People are writing more complex apps on top of jQuery and there
is a widely understood need for MVC frameworks, such as [Backbone.js][], 
[Knockout.js][] and [JavaScript MVC][].

* Feature detection is important!
    * Polyfill - replicates standard feature with a compatible API
    * Shim - provides its own API for a future feature

* Serious need for templating systems. Boris Moore showed a very performant
  demo of jQuery Templates. Many other templating systems exist as well,
  like one built into [underscore.js][] and [mustache.js][].

* Many new mobile performance tools: [blaze.io][] -- a tool that gives a
  general overview of a site's performance, [pcapperf][] -- a web performance
  analyzer that uses tcpdump output from mobile device activity, and [jDrop][]
  -- a service that lets you capture large amounts of data on your mobile
  device and then analyze it on the desktop web browser.

* People are rallying around [JSHint][], a fork of Crockford's [JSLint][]
  project, but with more configurable JavaScript sanitation rules.

* Haters gotta hate. Everybody seems to get a kick out of hating Douglas
  Crockford. Give the nice opinionated man a break and go write some
  JavaScript.

I went to a bunch of talks, and I took the most notes for during this talk:

## State of jQuery

John Resig talked about a bunch of changes to the project structure, largely
irrelevant to jQuery library consumers. He also covered some of many jQuery 1.6
improvements:

* Rewrite of `attr()` and `val()`. For example, `attr('val', false)` removes
the attribute
* Separate `prop()` from `attr()`. Indeed!
* `$('input:focus')` gets focused input box across platforms
* Significant performance boosts:
    * `attr()` performance ~85% faster, `val()` ~150% faster, `data()` ~115%
    faster
* Integration with requestAnimationFrame for animations
* `$.map(Object, function)` now works (as it does for Arrays)

Pro tip: jQuery automatically parses serialized JSON if it's included as the value 
of a HTML5 data attribute. Example: `<header data-array="[0,1,2]">` then 
`$('header').data('array')[1] == 1`

## State of jQuery Mobile

Mobile matters. 5.3 billion mobile subscriptions (cf. global population of 6.8
billion), 10 billion web-enabled mobile devices.

John Resig also touched on jQuery Mobile, and then Scott Jehl and Todd Parker went 
into a lot more detail.

* Navigation model now uses the [history API][] for hash-less URLs.
* jQM minified and packed is ~18kb!
* Nice gallery of goodness at [jQuery Mobile Gallery][]
    * Including [Obama's mobile site][]!
* Media queries
    * Useful as a browser support cutoff heuristic.
    * CSS classes added based on media queries, facilitating simpler styles
    * Uses [Respond.js][], a polyfill for browsers that don't support media queries
* Philosophy: easily brandable cross-device experience
* All builtin views are ARIA-enabled

Pro tip: mouse events in some mobile browsers are on a [300ms delay][] to allow
the browser to interpret user's gestures. jQuery Mobile includes a fix for
this!

## Prototyping Tools in jQuery

Super useful and informative set of tools!

MockJAX is a library that simulates a server.

* Intercepts and simulates AJAX calls
    * Define a URL structure and a response structure
* Can define responses as a function.
* Can simulate error responses.
* Useful for unit testing as well!

MockJSON: create fake JSON on demand

* A way to generate random-ish JSON
* For example, `{'age|0-99'}` outputs `{'age': randint_between_0_and_99}`

Amplify: abstraction layer for all data

* Abstracts away shifting server-side APIs
* amplify.request.define can define a data store. 

For example:

    amplify.request.define("list", "ajax", {
      url: "/todo/",
      dataType: "json",
      type: "GET"
    });

[HTTP Archive]: http://httparchive.org/
[history API]: https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
[300ms delay]: http://cubiq.org/remove-onclick-delay-on-webkit-for-iphone
[jQuery Mobile Gallery]: http://www.jqmgallery.com/
[Obama's mobile site]: http://www.barackobama.com/m/
[Respond.js]: https://github.com/scottjehl/Respond
[Backbone.js]: http://documentcloud.github.com/backbone/
[Knockout.js]: http://knockoutjs.com/
[JavaScript MVC]: http://javascriptmvc.com/
[JSLint]: http://www.jslint.com/
[JSHint]: http://jshint.com/
[blaze.io]: http://www.blaze.io/
[pcapperf]: http://pcapperf.appspot.com/
[jDrop]: http://jdrop.org/
[underscore.js]: http://documentcloud.github.com/underscore/
[mustache.js]: http://mustache.github.com/



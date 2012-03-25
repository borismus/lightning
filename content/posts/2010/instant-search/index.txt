Instant Search in 60 Lines
==========================
categories: [web]
posted: 2010-10-09
snip: A short snippet of jQuery code that approximately implements the instant search
  experience.



Google recently unveiled Instant, a search enhancement which show
results as you type. The real technical challenge here is scaling the
backend, which now needs to handle a lot more load. The frontend
implementation, however, is quite simple. Yearning for some web
development, I decided to get my hands dirty. Here's a minimal
[implementation][] in under 60 lines of jQuery code.

Instant Search relies on two separate data sources: a suggestions API,
and a web search API. Roughly speaking, it works as follows: as you type
in the search box, AJAX requests are made to the suggestion API. The top
suggestion is then used as the query to search. In this case, I used the
following two services, both of which support JSONP:

-   Suggest: [http://suggestqueries.google.com/complete/search][]
-   Search: [http://ajax.googleapis.com/ajax/services/search/web][]

To make your own search instant, all you need are your own suggest and
search feeds, and some tweaks to my code. Just make sure your server can
handle the load!

  [implementation]: instant-search.html
  [http://suggestqueries.google.com/complete/search]: http://suggestqueries.google.com/complete/search
  [http://ajax.googleapis.com/ajax/services/search/web]: http://ajax.googleapis.com/ajax/services/search/web


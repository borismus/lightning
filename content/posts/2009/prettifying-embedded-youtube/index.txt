Prettifying Embedded YouTube
============================
categories: [web]
posted: 2009-02-27
snip: Raving about the Smart Youtube wordpress plugin.



In late January 2009, [YouTube][] decided to change the default look of their
embedded videos. They silently added an informative header which includes the
video title and rating. Some time before then, a default search bar appeared at
the top of the video. Thanks to these changes, most haphazardly embedded
YouTube videos on the internet sport a repulsive new look. 

What, you might ask, can be done about this excessive ugliness? Well, you could
switch to [Vimeo][], which has a much nicer set of defaults, but that would
mean bidding the YouTube community farewell -- and what a tragedy that would
be! A better alternative is to learn the [YouTube Embedding API][], but there
are still problems:

1.  Embedding code for YouTube videos is ugly.
2.  The YouTube embedding scheme often silently changes.
3.  If you embed multiple videos, there is no way to specify a default
    set of embedding preferences.

If you are a wordpress user, all of these issues are resolved by the most
excellent [Smart YouTube][] plugin. With it you can embed videos by simply
inserting the URL to any YouTube video into your wordpress page or post and
replacing http with http**v**. Through a settings page, you can modify the way
all of your embedded videos look with one fell swoop.

  [YouTube]: http://www.youtube.com/
  [Vimeo]: http://www.vimeo.com
  [YouTube Embedding API]: http://code.google.com/apis/youtube/player_parameters.html
  [Smart YouTube]: http://www.prelovac.com/vladimir/wordpress-plugins/smart-youtube


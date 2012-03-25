An Onslaught of Mobile HTML Games
=================================
categories: [web]
posted: 2010-10-16
snip: Porting Onslaught! to a mobile web-based game controller. Also featuring frustrations
  involving multi-touch on Android.



HTML5 games are really picking up. Casual Girl Gamer recently produced a
nice [list of impressive titles][]. The modern web platform (namely,
fast javascript and canvas) is incredibly promising to a game developer.
The advantages that it brings are huge: no installation required, and
ubiquitous cross platform compatibility. I took a practical look at
games in the HTML5 mobile space, taking [Onslaught!][], a particularly
fun and well written game, and [porting it to Android/iPhone][]. 

Perhaps porting is too strong a word here. Onslaught! runs and performs
reasonably well on my Nexus One running Android 2.2.1. The only problem
is that the game uses keyboard input, making it completely unplayable on
mobile devices. Luckily, the controls are quite simple, and only require
a directional pad and two buttons. So I decided to build an on-screen
virtual game controller, not unlike those found in many native iPhone
games.  At first I was inclined to build the controls by extending the
game itself (using the canvas element), but then decided that an
HTML-based approach is better (since it saves the trouble of hit
detection), and might even work as a generic controller for other games.

Hoping to create a general game controller for Android/iPhone, I sought
to generate keyboard events from JavaScript, based on touch input. While
this is possible if your key event handlers are written in a particular
framework ([say jQuery][]), it seems to be generally impossible 
[for security reasons][]. I wrote an Onslaught!-specific [controller][]
that should be easy to port to any other game. The controller simply
embeds the Onslaught! game in it's original 640x480 resolution, which is
then scaled to the device size using the [meta viewport][] element. The
result is a mobile game that's playable on Nexus One, and
not-quite-playable on iPod Touch (2nd gen) due to slower JavaScript
execution. These are the only two devices I currently have access to, so
I would appreciate it if you could [try it][porting it to
Android/iPhone] on your Android or iOS device (in landscape mode) and
let me know how it goes!

[![image][]][porting it to Android/iPhone] 

I ran into a few stumbling blocks as I was developing and testing this
port, most of which involve the Android browser on Nexus One running
Android 2.2.1.

1.  Very immature touch event (ontouchstart, ontouchend, etc) support.
    In fact, the **browser doesn't seem to support multi-touch at all**
    (ie. only one touch can be registered at a time). In contrast,
    Safari for iOS supports multitouch events quite well. For complete
    details, see this [quirksmode writeup][] and this [bug report][].
2.  The Android browser completely ignores many properties in the meta
    viewport element's content attribute. Specifically, the **browser
    doesn't react to initial-scale, minimum-scale, maximum-scale and
    width**. As a result, I had to hack around this issue by abusing an
    Android-only property called [target-densityDpi][]. I suspect that I
    may be doing something wrong here, since it's a pretty fundamental
    issue. Still I logged a [bug][].
3.  Less significant but still noteworthy, the CSS **:active selector
    does not activate** on the Android browser (at least for div
    elements). The reference implementation is iOS, where a touchstart
    event on a div element causes it to become :active until a touchend
    event.

In the short term, HTML as a gaming platform is emerging as a real Flash
killer. In the long term, I wouldn't be surprised if HTML games will be
widely played on Mac, PC, TV console, and mobile phone platforms.
Whatever happens, browsers will continue to be pushed to conform to
modern specifications and perform ever better, making mobile rich web
applications more and more feasible. 

In closing, many thanks to [Lost Decade Games][] team for writing such a
sweet game and not obfuscating the JavaScript! Oh, and a reminder that
if you're working on a HTML game, be sure to submit it to 
[Mozilla's Game On][] contest, then add some touch controls and submit
it to this [mobile HTML game contest][]. Let the games begin!

  [list of impressive titles]: http://www.casualgirlgamer.com/articles/entry/28/The-Best-30-HTML-5-games/
  [Onslaught!]: http://lostdecadegamesapp.appspot.com/
  [porting it to Android/iPhone]: onslaught/
  [say jQuery]: http://api.jquery.com/keydown/
  [for security reasons]: http://stackoverflow.com/questions/1601593/fire-tab-keypress-event-in-javascript
  [controller]: onslaught/js/controller.js
  [meta viewport]: http://www.quirksmode.org/mobile/viewports.html
  [image]: onslaught.png
  [quirksmode writeup]: http://quirksmode.org/mobile/tableTouch.html
  [bug report]: http://code.google.com/p/android/issues/detail?id=11909
  [target-densityDpi]: http://developer.android.com/reference/android/webkit/WebView.html
  [bug]: http://code.google.com/p/android/issues/detail?id=11912
  [Lost Decade Games]: http://blog.lostdecadegames.com/
  [Mozilla's Game On]: http://mozillalabs.com/gaming/2010/09/30/game-on-2010-is-here/
  [mobile HTML game contest]: http://www.html5contest.com/


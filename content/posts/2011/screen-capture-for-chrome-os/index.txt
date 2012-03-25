Screen video capture for Chrome OS
==================================
categories: [web, google, chrome]
posted: 2011-10-04
snip: An effective way of creating video screen captures in Chrome without relying
  on a plugin.




This post is about video capture in Chrome that doesn't rely on any
external dependencies like Flash (no fun), NPAPI (not supported on
Chrome OS) and Native Client (not *yet* supported on Chrome OS).

I take screenshots all the time for bug reporting, image editing, etc.
On OS X, this functionality is conveniently built in, and available
through `Command` - `Shift` - `4`. As a web denizen, I find it very
useful to auto-upload these captures to a remote server, so I wrote this
[minimal image uploader][uploader] which replaces the default behavior
on OS X to capture the screenshot, and also uploads it to a picture
hosting service.

Taking video capture of various UIs is also immensely useful for showing
demonstrations, complex interactions, and subtle bugs. I recently
re-discovered that QuickTime on OS X comes with this functionality built
in. Prior to that I used (paid) ScreenFlow, which also has very nice
dimension cropping and time dilation features.

What if we're on a web-only device, such as a Chromebook running Chrome
OS? There is a still screenshotting API, but capturing video is less
trivial. I've released an extension that captures and play backs video
captures inside Chrome, and also lets you share stills to Picasa (using
the OAuth 2 [extension library][oauth2crx]). It's available on the
[webstore][webstore], and the source is on [github][source]. Read on to
learn how it works, and see how you can help.

# Screenshots in Chrome

Chrome provides the [`captureVisibleTab`][api] extension API for taking
a screenshot of a tab. It requires host permissions on the page, but as
usual the <all_urls> permission will enable the API across all pages
(with some exceptions). A few successful extensions, such as
[Awesome Screenshot][awesomescreenshot], use this API and allow
cropping, annotation and sharing of screen grabs.

What if you want to capture video of a tab? Chrome provides no
pre-existing API for this purpose, however, we can piggyback on the
still screenshot API, executing it repeatedly from the background page
for every frame we want to capture:

    var images = [];
    var FPS = 30;
    var QUALITY = 50;
    timer = setInterval(function() {
      chrome.tabs.captureVisibleTab(null, {quality: QUALITY},
        function(img) {
          images.push(img);
        });
    }, 1000 / FPS);

As we capture, we store the base64-encoded strings representing video
frames in an array. Once we're done capturing, we can simulate video
playback by rapidly swapping the images in and out:

    var background = chrome.extension.getBackgroundPage();
    timer = setInterval(function() {
      if (currentIndex >= images.length - 1) {
        pause();
        return;
      }
      setIndex(currentIndex + 1);
      updateSliderPosition();
    }, 1000 / background.FPS);

This approach turns out to be surprisingly efficient, with the extension
being able to capture at 30 FPS on a MacBook Air, and 10 FPS on a
Chromebook without too much noticeable slowdown.

Note that we rely on a fixed FPS for ease of implementation, however one
could imagine using `requestAnimationFrame` and tracking the variable
frame rate so that the playback speed is reasonable. However, there are
definitely precision issues with JavaScript's timers, so this is a much
more challenging approach.

So we can capture and playback videos inside the browser, but getting it
out of the browser is another matter entirely. As a temporary measure,
my colleague [Ido Green][ido] built a screen stitching service which
encodes multiple images into a movie using ffmpeg. Ideally, of course,
we would encode in the browser. Perhaps a JavaScript video encoder could
be implemented, though the performance may be too poor for practical
use. Alternatively, a ffmpeg Native Client-based approach might be
suitable, especially given that ffmpeg has [already been ported][ffmpeg].

# Free ideas

There are a few logical next steps for this sample. As already
mentioned, encoding video in the browser is a top priority, but there
are a slew of other interesting directions, some of which can be seen as
features, and others as separate products.

* The `captureVisibleTab` API doesn't track the mouse cursor. This could
  be done by injecting an overlay onto the current page and tracking
  mousemove and click events. This data could then either be drawn onto
  a canvas context, or encoded separately as `mouseData`, and then drawn
  with JavaScript at playback time.

* Cropping the video dimensions, modifying the video time schedule
  (speedup, slowdown, truncation) and annotation are all desired
  video-editing class features that could be implemented by treating
  images as canvases.

* A compelling use case for this technology is creating screen sharing
  sessions for demos and presentations. Thus, it would be very useful to
  stream the video to a server, and broadcast it to multiple clients in
  real time. [Binary websockets][binaryws] are now available in Chrome,
  and this could be a great application.

* Audio annotations on screen captures make perfect sense, and are
  widely supported by desktop applications. APIs for sound capture have
  been a [long time coming][deviceapi], but finally we may have an answer
  via the [WebRTC][webrtc] ecosystem, and the `getUserMedia` call.

By the way, I've switched to exclusively using Markdown for all of my
published writing, and wrote an [markdown preview][markdown] for Chrome
to make my life a bit easier.

[uploader]: https://github.com/borismus/screencapture-www
[api]: http://code.google.com/chrome/extensions/tabs.html#method-captureVisibleTab
[awesomescreenshot]: http://awesomescreenshot.com/
[ido]: http://greenido.wordpress.com
[ffmpeg]: http://code.google.com/p/naclports/source/browse/trunk/src/libraries/ffmpeg-0.5/
[source]: https://github.com/borismus/chrome-screencast
[webstore]: https://chrome.google.com/webstore/detail/omahgjnmfgeeeoekegajhndkncocoofd
[oauth2crx]: http://smus.com/oauth2-chrome-extensions
[binaryws]: http://updates.html5rocks.com/2011/08/What-s-different-in-the-new-WebSocket-protocol
[deviceapi]: http://www.w3.org/2009/dap/
[webrtc]: http://www.webrtc.org/
[markdown]: https://github.com/borismus/markdown-preview



Multi-Touch for your Desktop Browser
====================================
categories: [web]
posted: 2011-05-02
snip: Prototyping multi-touch applications? Simulate spec-compatible touch events
  without a mobile device.




In mobile development, it's often easier to start prototyping on the desktop
and then tackle the mobile-specific parts on the devices you intend to support.
Multi-touch is one of those features that's difficult to test on the desktop, since
most desktops didn't have multi-touch hardware, and thus desktop browsers don't
have touch event support. Things are different today (you hear every mother say). 
Most new Macs, for example, ship with multi-touch capable input of some sort.
Unfortunately the browsers haven't really caught up yet.

Enter Fajran Iman Rusadi, who released a [npTuioClient][] NPAPI plugin with a
JavaScript wrapper. Unfortunately this library provides a non-standard API to
multi-touch, which is not ideal for developers that want to write their
multi-touch application on desktop and then run the same code on their mobile
devices without modifications.

## Browser Patches

As HTML5 grows up, browser vendors struggle to stay current up with the growing
variety of specifications. The result is [uneven feature support][] across
browsers and a complex problem for web developers.

The web development community has rallied around **shims** and **polyfills**
for the solution. These are bizarre terms that I find confusing and so will
defer to [Remy Sharp to define][]. The basic idea of both is to fill in
functionality that's missing in the browser implementation.

Since we now have a well established [touch events specification][] working
group at the W3C, I wrote [MagicTouch.js][], a multi-touch polyfill thatlets
you, the developer, write the same code, test it on your desktop browser and
then, run it on your real device. Totally tubular!

MagicTouch.js still relies on the npTuioClient plugin, it just creates
spec-compatible touch events. Incidentally, here's how you can trigger custom
DOM events:

    var event = document.createEvent('CustomEvent');
    // Initialize the event, make it bubble up and possible to cancel
    event.initEvent('touchstart', true, true);
    // Assign properties to the event
    event.touches = touchArray;
    ...
    // Get the element associated with the event
    var element = document.elementFromPoint(...);
    // Assign the element
    event.target = element;
    // Finally, dispatch the event
    element.dispatchEvent(event);

Note that this approach to create custom DOM events is not cross-browser
compatible. I only tested in Chrome.

## Installation

Here how to get multi-touch web events working in Chrome for Mac:

1. Download and install the [npTuioClient NPAPI plugin][]
into `~/Library/Internet Plug-Ins/`.
2. Download the [TongSeng TUIO tracker][] for Mac’s MagicPad and start the
server
3. Download [MagicTouch.js][] and include both the script and the plugin in your
app.

The code for this is as follows:

    <head>
      ...
      <script src="/path/to/magictouch.js"></script>
    </head>
    <body>
      ...
      <object id="tuio" type="application/x-tuio" style="width:0; height:0;">
        TUIO Plugin failed to load
      </object>
    </body>

...and you're off to the races! Your multi-touch code will now work. Try out
this [finger tracking demo][] on either your multi-touch mobile device or your
newly patched desktop browser.

## Future Steps

As you saw, MagicTouch.js takes some effort to set up initially, requires
you to use an `<object>` in the HTML, and also needs you to run a separate
process for intercepting touch events. While we can't quite get away without
having to run another process, we can eliminate the NPAPI plugin by using the
[WebSocket API][] to communicate to that process.

If you're interested in multi-touch mobile web development, check out this
[article on html5rocks.com][].

[compatibility tables]: http://caniuse.com/
[bizarre terms]: http://remysharp.com/2010/10/08/what-is-a-polyfill/
[touch events specification]: https://dvcs.w3.org/hg/webevents/raw-file/tip/touchevents.html
[uneven feature support]: http://caniuse.com/
[finger tracking demo]: https://github.com/borismus/MagicTouch/blob/master/samples/tracker.html
[WebSocket API]: http://dev.w3.org/html5/websockets/
[Remy Sharp to define]: http://remysharp.com/2010/10/08/what-is-a-polyfill/
[MagicTouch.js]: https://github.com/borismus/MagicTouch
[npTuioClient]: https://github.com/fajran/npTuioClient
[article on html5rocks.com]: http://www.html5rocks.com/mobile/touch.html
[npTuioClient NPAPI plugin]: https://github.com/fajran/npTuioClient#readme
[TongSeng TUIO tracker]: https://github.com/fajran/tongseng/downloads



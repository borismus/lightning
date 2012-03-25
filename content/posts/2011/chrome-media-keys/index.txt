Chrome Media Keyboard Shortcuts
===============================
categories: [chrome, web, keyboard, shortcuts]
posted: 2011-04-01
snip: A Chrome extension that lets you bind keyboard shortcuts to control your favorite
  music player.



Few people want to synchronize their burgeoning music libraries across
computers (SSDs are small), or even lift it into the clouds with
something like Amazon's Music Cloud (uploading would take forever). As a
result many are saying goodbye to iTunes and moving to web-based
streaming music services like [grooveshark][], [last.fm][],
[thesixtyone][], [rd.io][] etc. This move has a significant UX drawback:
many keyboards come with multimedia keys to control your music player,
but these are useless if you use a web-based music player. This post
addresses this inconvenience with [Media Keys][], a Chrome extension
that lets you assign keyboard shortcuts in Chrome control web-based
music players (currently thesixtyone only).

## How it works

The extension relies on two injected [content scripts][]: [key.js][], a
keyboard event listener injected into all pages and [player.js][], a
music player controller, injected into the player page. 

Key.js intercepts keyboard commands (ex. the next song key), and if they
match bound music player keyboard shortcuts (ex. next song key =\>
change to the next song), it sends a message to player.js, which then
does the right thing (ex. changes to the next song) by simulating mouse
clicks.  Sounds good on paper, but the snag here is that you can't
easily do direct tab-to-tab communication in Chrome extensions, except
possibly through a long-lived port connection. However using long lived
connections doesn't make conceptual sense, since the lifespan of a tab
is relatively short. 

So we go the long way with the help of a [background page][].

1.  On tab load, injected key.js messages the background page to
    retrieve media key bindings
2.  On music player load, injected player.js messages the background
    page, reporting its tab ID. The background page [opens a Port][]
    through which to communicate with the player page
3.  Matching keyboard events on all tabs send messages to the background
    page. The background page then relays those messages through the
    port to the music player

Here's an abridged code sample from the [background page][1]: 

    chrome.extension.onRequest.addListener(
      function(request, sender, sendResponse) {
        switch(request.type) {
          case 'command':
            try {
              port.postMessage(request.command);
            } catch(error) {
              if (localStorage['autoload']) {
                chrome.tabs.create({url: SITE_URL});
              }
            }
            sendResponse({});
            break;
          case 'register':
            chrome.tabs.getSelected(null, function(tab) {
              port = chrome.tabs.connect(tab.id);
              sendResponse({});
            });
            break;
        }
      }
    );

To summarize, this approach enables a client-side remote control for a
specific web application from any other page. This is potent stuff!

## Try it out

Want to try it out? Media Keys works across all Chrome platforms.

1.  Install [Function Flip][] *(Mac only)*
2.  Check previous, pause/play and next buttons (F6, F7, F8 here) *(Mac
    only)*
3.  Install the [Media Keys][2] extension
4.  Open up the extension options, bind the keys and save
5.  Open up a new page and press the key bound to play

I made a short screencast showing how to install configure and use the
extension.

<iframe title="YouTube video player" width="600" height="368"
  src="http://www.youtube.com/embed/SrfsnU2gSyI" frameborder="0"
  allowfullscreen></iframe>

## Wish list

Just to recap, the keyboard shortcut binding pattern described above
injects a script into all tabs, which essentially listens to all key
events. A malicious developer could write a key logger watches username
and password fields, correlates to the current domain and sends
harvested data to some private server. 

There are also several limitations to this keyboard shortcut binding
pattern. It simply won't work in the following cases:

1.  Chrome is in the background
2.  Focus inside chrome is not on the page (ex. location bar)
3.  Chrome is on a special page (ex. new tab page) where content scripts
    don't get injected
4.  The current page intercepts keyboard events and stops propagation
    (ex. Google Docs)

Keyboard shortcuts are super important to power users, and Chrome (OS)
surely won't leave us in the dust, so I'm looking forward to helping
address the security risks and practical limitations this approach as a
Chromium project contributor.

## Share and enjoy

One last thing. If you've read my [previous post][], you know that I'm a
big fan of [thesixtyone.com][thesixtyone] so my initial implementation
works for this service only. Making it work for other music streaming
services is just a matter of creating a customized player.js file for
your favorite music app, and tweaking the manifest to inject the new
player.js into the correct domain. Feel free to fork the 
[project on github][].

  [grooveshark]: http://listen.grooveshark.com/
  [last.fm]: http://www.last.fm
  [thesixtyone]: http://thesixtyone.com
  [rd.io]: http://rdio.com
  [Media Keys]: https://chrome.google.com/extensions/detail/cpgegiegacijlefhjkfodppcefjhgdeo/
  [content scripts]: http://code.google.com/chrome/extensions/content_scripts.html
  [key.js]: https://github.com/borismus/Chrome-Media-Keys/blob/master/key.js
  [player.js]: https://github.com/borismus/Chrome-Media-Keys/blob/master/t61.js
  [background page]: http://code.google.com/chrome/extensions/background_pages.html
  [opens a Port]: http://code.google.com/chrome/extensions/messaging.html#connect
  [1]: https://github.com/borismus/Chrome-Media-Keys/blob/master/dispatch.html
  [Function Flip]: http://kevingessner.com/software/functionflip/
  [2]: https://chrome.google.com/extensions/detail/cpgegiegacijlefhjkfodppcefjhgdeo
  [previous post]: /chrome-extension-mashups/
  [project on github]: https://github.com/borismus/Chrome-Media-Keys


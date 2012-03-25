Global Chrome Media Keys with Key Socket
========================================
categories: [chrome, web, keyboard, websockets, music]
posted: 2011-07-28
snip: An extension that lets you bind global keyboard shortcuts to control your favorite
  music player in chrome.




I just skipped to the next Google Music track without leaving vim. Wanna play?
Here's the [app][] and [Chrome extension][crx]. To learn how it works, read on!

## Script injection limitations

[Last time around][post] I implemented keyboard bindings by injecting a content
script into every tab in Chrome, capturing key events and sending them to a
background page. This approach has some serious performance drawbacks:

* Content scripts injected into each page.
* Background pages don't perform very well.

And functional limitations:

* Won't work on special URLs like `chrome://` and `file://`.
* Won't work when the omnibox is focused.
* Requires chrome to be in the foreground.

## Global key bindings and websockets

What we really want is global key bindings. I don't care where my keyboard
focus happens to be right now, I just want to switch to the next freaking song!
This sort of thing requires OS-level event capture, which is functionality most
browsers don't come with. To get around this, I run a standalone app to capture
global keys and run a websocket server to send these events to the browser.
Note that this approach generalizes well to other use cases where functionality
is not available in a browser, but can be more readily implemented natively.

The obvious drawback to this approach is that it requires the user to run a
separate process to capture events.

## Media key bindings in Cocoa and Python

Rogue Amoeba, maker of some popular OS X audio utilities, has a
[nice post][mediakeys] on their blog on capturing media keys from an OS X
application. The basic idea is to subclass NSApplication and override the
sendEvent: selector:

    - (void)sendEvent: (NSEvent*)event {
      if( [event type] == NSSystemDefined && [event subtype] == 8 ) {
          // Event processing
      }
      [super sendEvent: event];
    }

Which in PyObjC results in the following equivalent code:

    def sendEvent_(self, event):
        if event.type() is NSSystemDefined and event.subtype() is 8:
            # Event processing

        NSApplication.sendEvent_(self, event)

It's pretty neat to be able to implement Cocoa apps without having to write a
single line of objective C. Writing a statusbar app with no dock item was
surprisingly simple (though I have doubts that this works well for Lions and
Tigers and Bears). All that's required is to set `LSUIElement` to `true` in the
Info.plist.

To package the whole PyObjC application, I wrote a setup.py script and used
[py2app][], which generates a Mac OS X .app bundle which, from a user's
perspective is indistinguishable from an OS X app written in Objective C.

## A WebSocket server in python

In addition to spawning off a Cocoa application and capturing events, of course
I create a WebSocket server. WebSockets use a pretty simple protocol which can
easily be implemented using python sockets. I based my implementation heavily
on [this one][wspy].

Since a Cocoa application runs its own event loop which captures the
main thread, the websocket listener needs to run in a separate thread:

    class KeySocketServer(Thread):
        def __init__(self):
            self.server = websocket.WebSocketServer('localhost', 1337, KeySocket)
            Thread.__init__(self)

        def run(self):
            self.server.listen()

The WebSocket standards are still evolving and implementers are, as ever,
scrambling to catch up. The good news is that this means
[binary support][wsbin] is coming, which is a boon for games and other
intensive network consumers. The bad news is that the latest Chrome canary (at
the time of writing), requires the response to contain the
`Sec-WebSocket-Accept` header, conforming to the
[draft-ietf-hybi-thewebsocketprotocol-06][wsspec], which is incompatible with
the python WebSocket code I'm currently using.

On my wishlist is a robus python WebSockets implementation that supports
multiple versions of the spec while it's still in flux.

## Injected scripts

On the Chrome extension side, a script is injected into the web player
application, which creates a WebSocket client that connects to the python
server on port 1337. When media keys are pressed, the python server sends
messages to the JS clients and the injected JS simulates DOM events in the web
player application, controlling music playback.

## Try it out

If you listen to Google Music, thesixtyone or Grooveshark in Chrome on OS X and
want global key bindings, please install the [extension][crx] and
[application][app]. If you're feeling generous, contribute your time and love!
I'd gladly take fixes for

* Key Socket servers for Linux and Windows
* Content scripts to control other web audio players
* Web Socket implementations that work with the new spec

And of course, here's the [source][src].

[post]: /chrome-media-keys
[mediakeys]: http://rogueamoeba.com/utm/2007/09/29/apple-keyboard-media-key-event-handling/
[wspy]: https://gist.github.com/512987
[wsspec]: http://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-06
[wsbin]: http://tools.ietf.org/html/draft-ietf-hybi-thewebsocketprotocol-06#section-4.6
[py2app]: http://svn.pythonmac.org/py2app/py2app/trunk/doc/index.html
[crx]: https://chrome.google.com/webstore/detail/fphfgdknbpakeedbaenojjdcdoajihik
[app]: https://github.com/downloads/borismus/keysocket/KeySocket.zip
[src]: https://github.com/borismus/keysocket
[manifest]: https://github.com/borismus/keysocket/blob/master/extension/manifest.json



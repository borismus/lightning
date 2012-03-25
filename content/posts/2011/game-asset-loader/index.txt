Loading Large Assets in Modern HTML5 Games
==========================================
categories: [web, offline, games]
posted: 2011-09-22
snip: An HTML5 filesystem-based approach to loading game assets. Still a work in progress.




HTML5 games are here today, and rapidly increasing in complexity. Impressive
[demos][water] are [everywhere][chromeexp], and prominent titles like [Gun
Bros][gunbros] and [Angry Birds][angrybirds] prove that it's possible to
create competitive gaming experiences in the browser. Games like these are
possible thanks largely to the modern web stack which includes WebGL, the Web
Audio API, Web Sockets and others.

Often forgotten, however, is the less sexy story of loading game assets. As the
web platform progresses and allows for increasingly complex games, game assets
(ex. textures, movies, music and images) grow in size and number, and asset
management becomes a sticking point for game developers.

Let me share with you some truths:

1. Modern games require gigabytes of assets (textures, movies, etc)
2. Gamers don't like waiting for their game to load
3. Browser gamers want to be able to play regardless of internet connectivity

"But wait," you say, "I know! Just use the [Application Cache][appcache]
and yer done!". Not so fast, dear reader... As described below, there are
problems with this approach, and I propose some solutions.

[water]: http://madebyevan.com/webgl-water/
[gunbros]: https://chrome.google.com/webstore/detail/ciamkmigckbgfajcieiflmkedohjjohh
[angrybirds]: http://chrome.angrybirds.com
[appcache]: http://diveintohtml5.org/offline.html
[chromeexp]: http://www.chromeexperiments.com/

# Problems with Application Cache

So you've started implementing your awesome asset loading solution using
AppCache. The good news is that there are some useful tools to help you debug
if you have taken this difficult route:

1. You can get basic information about the site's app cache through the
   Developer Tools' [resource panel][appcache-cdt].
2. You can view (and remove!) caches stored in Chrome by navigating to
   `chrome://appcache-internals/`.

But let me be blunt: **AppCache is annoying to deal with**. If you've made a
small error in your cache manifest file, you'll quickly hit a brick
wall. I ran into an issue where I forgot to include a `NETWORK:`
fallback clause, and wasted hours trying to figure out why all of my
XHRs were responding with status 0.

Part of what makes AppCache difficult to debug is its very **limited
JavaScript API**. Aside from letting you inspect the status of the entire cache
with `window.applicationCache` and the `updateready` event, AppCache doesn't
give us much to work with. There's no way to tell if a particular resource
we're dealing with is cached or not and no programmatic way of clearing the
cache.

AppCache takes a fully transactional approach to asset loading.  Either
the cache is fully loaded, or fully unloaded. Compounding this issue,
it's impossible to resume the download of an AppCache. Thus, if you have
a large amount of assets, your user will have to **wait a long time for
everything to be loaded**, and if they reload, they will need to restart
their cache download.

Lastly, you can only include one cache manifest per page, making it
**impossible to group assets** into multiple bundles. There are hacks that
use multiple iframes with different cache manifests to work around this
limitation (used in [Angry Birds][angrybirds]), but these are ugly!

Ultimately, what we need is a well-thought-out Application Cache
enhancement or replacement. Given how quickly web standards bodies move,
I've started thinking a bit about a transitional solution.

[appcache-cdt]: http://code.google.com/chrome/devtools/docs/resources.html

# Designing a game asset loader

An ideal asset loading solution requires some of these features:

1. Granular asset loading. Load all, in groups, or individually.
2. No asset size limits.
3. Offline capability.
4. Programatic control over assets.

It makes sense to group assets in bundles and let the loader take care
of the details. We can even create a custom manifest format, for
example, in JSON format:

    {
      "assetRoot": "./media/",   // The root of the assets.
      "bundles": [{
        "name": "core",          // A bundle definition.
        "contents": [            // The contents within.
          "theme.mp3",
          "loading.jpg"
        ]
      }, {
        "name": "level1",        // Multiple bundles defined.
        "contents": [            // Note: order implicit since bundles
          "L1/background.jpg",   // objects are stored in an array.
          "L1/blip.wav"
        ]
      }, {
        "name": "level2",
        "contents": [
          "L2/intro.mov"
        ]
      }],
      "autoDownload": false      // If true, download all in order.
    }

With this manifest format in mind, sample API usage might look like
this:

    // Load the asset library.
    var gal = new GameAssetLoader('/path/to/gal.manifest');

    // Read the manifest and other good stuff.
    gal.init(function() {
      // When ready, download the bundle named 'core'.
      gal.download('core');
    });

    // When the core assets are loaded.
    gal.onLoaded('core', function(result) {
      if (result.success) {
        // Show a loading indicator.
        document.querySelector('img').src = gal.get('loading.jpg');
      }
    });

    // Check the progress of the download.
    gal.onProgress('core', function(status) {
      console.log('status:', status.current/status.total, '%');
    });

Note that although I've been using the name Game Asset Loader, this
approach can be used for loading any large non-game assets, such as for
example, a video or photo gallery.

# Implementation details

Luckily, the modern web stack enables us to create a custom solution to
address all of these requirements. By leveraging technologies such as
the HTML5 Filesystem API or Indexed DB, we have programmatic access to
a storage mechanism that we can use to build an asset loader described
here.

I used the [Filesystem API][fsapi] to implement a version of the asset
loader. The code requests a large amount of persistent storage using the 
[Quota API][quotaapi], which is undocumented, but works anyway:

    // Get quota.
    storageInfo.requestQuota(window.PERSISTENT, quota,
      onQuotaGranted, onError);

    // Callback when the quota API has granted quota
    function onQuotaGranted = function(grantedBytes) {
      // Save grantedBytes in the adapter
      that.grantedBytes = grantedBytes;
      // Once quota is grantedBytes, initialize a filesystem
      requestFileSystem(window.PERSISTENT, grantedBytes, onInitFS, onError);
    };

    // Callback when the filesystem API has created a filesystem.
    function onInitFS = function(fs) {
      // Create a directory for the root of the assets.
      fs.root.getDirectory(ROOT_DIR, {create: true}, function(dirEntry) {
        that.root = dirEntry;
      }, onError);
    };

The approach fetches assets with `XMLHttpRequest`, and stores them in the
filesystem. All files in the filesystem are accessible via the `filesystem://`
schema, and can be used as any other resource. This filesystem URL is returned
by the library in the `get(path)` call.

Note that the writable HTML5 filesystem API is currently available in Chrome
only, but that it's quite possible to use IndexedDB (supported in Firefox and
IE10) as the data store.

[fsapi]: http://www.html5rocks.com/en/tutorials/file/filesystem/
[quotaapi]: https://groups.google.com/a/chromium.org/group/chromium-html5/msg/5261d24266ba4366?dmode=source

# Usage scenarios

The following section briefly describes what the game asset loader (GAL) does
in several scenarios.

Player goes to game.com which uses the game asset loader. The game calls
`gal.download('core')` to download core assets and
`gal.download('level1')` to load the first level into the player’s
filesystem. While the core bundle loads, the game displays a loading
indicator. Once core is loaded, the game displays the main menu. As soon
as the first level is loaded, the "Play now" button is enabled. As the
player plays, the GAL downloads more of the levels in the background.

Next time, the player tries playing offline. He goes to game.com, whose
code is cached via AppCache, and loads GAL again. This time GAL knows it’s
offline, looks up its manifest stored on the filesystem and doesn’t try to
download new assets. The old assets still work though.

Player is still offline, making good progress, and beats level 5, but
there are no assets downloaded for level 6. Luckily, before starting
each level, the game calls `gal.download('levelBundle')` to make sure
that the contents of that bundle are downloaded. The callback returns an
error and the game displays an error telling the player that he needs to
be online to download the next level.

So the player goes online and tries again. GAL re-downloads a manifest.
Next, GAL tries re-downloading every asset that the JS requests. Luckily most
of these assets are still in the browser cache, and won't be re-downloaded. The
loader then saves all of the assets in the filesystem, clobbering old files
indiscriminately. (This is bad, and needs to be fixed. Read on!)

# Future work

In particular, re-downloading every asset while online is not desirable
behavior, and we can't always rely on the browser cache for this. For
smaller files, we can probably rely on ETag and Last-Modified headers
and hopefully the browser won't re-download the files. However, the
**asset loader will still overwrite the asset in the filesystem, even if
it's unmodified**. This needs to be fixed. Large files are not likely to be
cached by the browser, so we will need more intelligent **caching built into
the asset loader itself**.

There are other edge cases that need to be considered, such as what happens
when an **asset is removed from a manifest**. Ideally if this occurs, it
**should also be removed from the filesystem**, but this is not currently
implemented.

I'm happy to release the [source][source] under the permissive Apache 2
license and provide [unit tests][tests] and a [sample][sample] project
for your perusal. It's well documented and should be reasonably easy to
understand. I've also made provisions to separate the core library
interface from the Filesystem-based implementation, making it even
easier to implement an Indexed DB adapter.

Before I go, let me reiterate that this library isn't quite production ready,
but a step in the right direction for facilitating real games on the web.
Please comment below if you have feedback on the idea, or are using the
library to write a game of your own!

[source]: https://github.com/borismus/game-asset-loader
[sample]: https://github.com/borismus/game-asset-loader/tree/master/tests/game
[tests]: https://github.com/borismus/game-asset-loader/blob/master/tests/tests.js




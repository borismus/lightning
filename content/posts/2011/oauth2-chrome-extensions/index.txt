OAuth 2.0 from Chrome Extensions
================================
categories: [web, google, chrome]
posted: 2011-07-07
snip: A JavaScript library that handles OAuth 2.0 for you, with a dead simple API.
  Comes with adapters for Google, Facebook and Github.




Applications that access online services often need to access a user's private
data. Chrome Extensions are no different. OAuth has emerged as the standard way
of letting users share their private resources across sites without having to
hand out their usernames and passwords. There is already a very nice 
[OAuth library for Chrome Extensions][oauth crx] that aims to simplify some of 
the pains that developers face when authorizing against OAuth endpoints.

Since this library was written, the OAuth standard enjoyed a version bump
([OAuth 2.0][oauth2]) which greatly simplifies the flow by no longer requiring
cryptography in the client. Also, some adventurous companies (notably
Google, Facebook and others) have actually implemented OAuth 2.0
endpoints. At the time of writing, OAuth 2.0 is still a draft spec, but is
nearing completion, and Chrome Extensions need some love.

You may be wondering why you even need an OAuth 2.0 library in the first place.
As Aaron Parecki pointed out in his [Current State of OAuth 2][oauth2 preso]
presentation at [Open Source Bridge][osb] in Portland, OAuth 2 is very
much a moving target. The spec is not yet finalized, and there are 16 versions
of it (although the most popular seems to be v10). Also, today's OAuth 2
implementations diverge from the spec in varying degrees, adding to the
developer pain. The reason this library needs to be chrome extension-specific
is that unfortunately Chrome extensions can't directly use the OAuth 2.0
server-side or client-side flows because they live at `chrome-extension://`
URLs.

When writing the OAuth 2.0 library for Chrome extensions, I had some goals in
mind:

1. Support a variety of OAuth 2.0 providers that implement the spec
2. Allow one app/extension to use multiple different OAuth 2.0 endpoints
3. Avoid background pages for performance reasons

## The OAuth 2.0 Library

There's a bit of setup involved if you'd like to create a Chrome extension that
connects to an OAuth 2 endpoint. This brief tutorial will guide you through
connecting to Google's APIs.

Register your application with an OAuth 2.0 endpoint that you'd like to
use. If it's a Google API you're calling, go to the [Google APIs][gapi] page,
create your application and note your client ID and client secret. For more
info on this, check out the [Google OAuth 2.0][goauth2] docs. When you setup your
application, you will be asked to provide redirect URI(s). Please provide the
URI that corresponds to the service you're using.

Here's a table that will come in handy:

<style>
  #impls { margin-left: -100px; }
  #impls td, #impls th { border: 1px solid #999 }
  #impls td { padding: 5px }
</style>
<table id="impls">
  <tr>
    <th>Adapter</th>
    <th>Redirect URI</th>
    <th>Access Token URI</th>
  </tr>
  <tr>
    <td>google</td>
    <td>http://www.google.com/robots.txt</td>
    <td>https://accounts.google.com/o/oauth2/token</td>
  </tr>
  <tr>
    <td>facebook</td>
    <td>http://www.facebook.com/robots.txt</td>
    <td>https://graph.facebook.com/oauth/access_token</td>
  </tr>
  <tr>
    <td>github</td>
    <td>https://github.com/robots.txt</td>
    <td>https://github.com/login/oauth/access_token</td>
  </tr>
</table>

#### Step 1: Copy library

You will need to copy the [oauth2 library][oauth2crx] into your chrome extension
root into a directory called `oauth2`.

#### Step 2: Inject content script

Then you need to modify your manifest.json file to include a content script
at the redirect URL used by the Google adapter. The "matches" redirect URI can
be looked up in the table above:

    "content_scripts": [
      {
        "matches": ["http://www.google.com/robots.txt*"],
        "js": ["oauth2/oauth2_inject.js"],
        "run_at": "document_start"
      }
    ],

#### Step 3: Allow access token URL

Also, you will need to add a permission to Google's access token granting URL,
since the library will do an XHR against it. The access token URI can be looked
up in the table above as well.

    "permissions": [
      "https://accounts.google.com/o/oauth2/token"
    ]

#### Step 4: Include the OAuth 2.0 library

Next, in your extension's code, you should include the OAuth 2.0 library:

    <script src="/oauth2/oauth2.js"></script>

#### Step 5: Configure the OAuth 2.0 endpoint

And configure your OAuth 2 connection by providing clientId, clientSecret and
apiScopes from the registration page. The authorize() method may create a new
popup window for the user to grant your extension access to the OAuth2
endpoint.

    var googleAuth = new OAuth2('google', {
      client_id: '17755888930840',
      client_secret: 'b4a5741bd3d6de6ac591c7b0e279c9f',
      api_scope: 'https://www.googleapis.com/auth/tasks'
    });

    googleAuth.authorize(function() {
      // Ready for action
    });

#### Step 6: Use the access token

Now that your user has an access token via `auth.getAccessToken()`, you can
request protected data by adding the accessToken as a request header

    xhr.setRequestHeader('Authorization', 'OAuth ' + myAuth.getAccessToken())

or by passing it as part of the URL (depending on the server implementation):

    myUrl + '?oauth_token=' + myAuth.getAccessToken();

**Note**: if you have multiple OAuth 2.0 endpoints that you would like to
authorize with, you can do that too! Just inject content scripts and add
permissions for all of the providers you would like to authorize with.

I've provided [some sample extensions][samples] that use this library to help
you get started.

## Varying OAuth implementations

Writing this library for one OAuth 2.0 endpoint was pretty straightforward.
The issues came when branching out to support multiple OAuth 2.0 server
implementations which comply to various degrees with differing versions of the
spec.

Facebook was the worst offender here. They claim to be an OAuth 2.0
implementation in line with v10, but are actually quite far from it. Here are
some of the issues:

* Token request method is GET instead of POST.

* Token response is some strange form encoded format instead of JSON.

* [List of scopes][fbscope] (aka "extended permissions") was really hard to
find.

* Apparently to get a user's favorite music, you need the `user_likes`
permission. Facebook, please [fix your docs][fblikes].

* No refresh tokens but they have an offline_access permission which makes your
access token expire later. This is ridiculous!

Twitter doesn't even have an OAuth 2.0 API. [@Anywhere][twoauth] does not
count. Some good [questions][twq1] on [quora][twq2] about this.

Still there are a lot of services that *DO* implement OAuth 2.0, such as
Foursquare, Gowalla, Windows Live, Salesforce, Soundcloud and many others.

## Extending the Library

To mitigate differences between OAuth 2.0 implementations, I implemented the
[Adapter pattern][adapt_pattern]. Doing this encapsulates protocol differences
in a separate adapter module for each server implementation.

The library comes with adapters for Google, Facebook and Github. These adapters
are located in the [adapters directory][adapters] here. If you would like to
contribute your own adapter, please take a look at the sample adapter and then
[fork the project][fork], submit a pull request, and I'll try to add
it to the project.

Also, please let me know if you experience problems using this library and
we'll sort them out! The best way to do this is via [github][] or
[twitter][].

[oauth2 preso]: http://www.slideshare.net/aaronpk/the-current-state-of-oauth-2
[osb]: http://opensourcebridge.org/
[oauth crx]: http://code.google.com/chrome/extensions/tut_oauth.html
[oauth2]: http://oauth.net/2/
[gapi]: https://code.google.com/apis/console/
[goauth2]: http://code.google.com/apis/accounts/docs/OAuth2.html
[fbscope]: http://developers.facebook.com/docs/authentication/permissions/
[fblikes]: http://forum.developers.facebook.net/viewtopic.php?pid=283691
[twoauth]: http://dev.twitter.com/anywhere
[twq1]: http://www.quora.com/Why-isnt-Twitter-implementing-OAuth-2-0-just-like-Facebooks
[twq2]: http://www.quora.com/When-is-Twitter-going-to-implement-OAuth-2-0
[adapt_pattern]: http://en.wikipedia.org/wiki/Adapter_pattern
[bt]: http://tools.ietf.org/html/draft-ietf-oauth-v2-bearer-02
[adapters]: https://github.com/borismus/oauth2-extensions/tree/master/lib/adapters
[oauth2crx]: https://github.com/borismus/oauth2-extensions/tree/master/lib
[samples]: https://github.com/borismus/oauth2-extensions/tree/master/samples
[fork]: https://github.com/borismus/oauth2-extensions
[twitter]: http://twitter.com/borismus
[github]: http://github.com/borismus



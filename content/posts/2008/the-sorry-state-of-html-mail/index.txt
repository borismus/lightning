The (Sorry) State of HTML Mail
==============================
categories: [web]
posted: 2008-10-31
snip: Complaining about how terrible it is to create HTML email that renders properly
  in multiple mail clients.



Web design used to be a black art. Ten years ago, browser differences used to
be so dramatic that the only viable solution for an HTML designer was to fall
back to the least common denominator for page layout, which was HTML tables. In
today's web design community, using table layouts is considered to be a heinous
crime, since most popular modern rendering engines (IE, Gecko and WebKit) are
converging to some shared interpretation of web standards. Unlike layout
engines on the web, though, rich mail interpreters have remained stagnant, and
in some cases have regressed. <strike>Without pointing any fingers...</strike>

Much of the blame for this difference lies in Microsoft's decision to use the
same engine for composing and viewing email in Outlook 2007. They wanted to
make the life of email designers easier, or so the story goes. But since
Internet Explorer doesn't have editing functionality, and Front Page is too
heavy to embed, the remaining choice was Word '07. Unfortunately, Word's
rendering engine is extremely limited, in the following notable ways:

1.  No positioning or floating elements, so CSS-based layouts are out
2.  No CSS backgrounds, combined with (1) means that there's no way to
    have an image background at all.

So, if you care a significant population of email readers (7% use Outlook '07),
and want to deliver a rich media email, you are condemned to designing with
table layouts, or to skip HTML altogether, and simply use images. 

For a long time, there was no good way of determining a
breakdown of email client usage. Recently, the good people at
fingerprint have come up with a solution, and now use a large sample of
people to determine global [email client usage statistics][]. According
to them, Hotmail, Yahoo Mail and Gmail add up to roughly 50% of all
usage. 

Since the UI of a web-based email client is written in HTML, so it is critical
for webmail developers to ensure that the CSS and HTML found in the email does
not interfere with the global look and feel. The canonical solutions are to
decorate all ids and classes in the email with some kind of prefix to ensure
that there are no name collisions, and use a white list approach to CSS styles.
These white lists are usually quite long, but lack some important and oft-used
properties. For example, CSS image backgrounds are disallowed, except on Yahoo.
And of course, Microsoft had to leave its bizarre mark too: Hotmail strips the
margin-top property, but not the margin-bottom property. 

Historically,
webmail clients used to ignore anything outside of the `<body\>` tag,
which meant that all CSS had to be written inline, leading to
unmaintainable layouts. In recent tests, however, popular webmail
clients no longer ignore `<style\>` elements in the `<head\>`, and instead,
apply the CSS sparingly inline. Among modern native mail clients, there
is a positive trend as well. Microsoft Live Mail uses the IE7 rendering
engine, Thunderbird uses Gecko and Mail.app uses WebKit. So it looks
like there is light at the end of the tunnel for downtrodden HTML email
designers. In the meantime though, I send them my deepest condolences.

  [email client usage statistics]: http://fingerprintapp.com/email-client-stats


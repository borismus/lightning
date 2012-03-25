Jam Hunt: Friendly Jam Sessions
===============================
categories: [web, music]
posted: 2010-04-24
snip: A Facebook application for finding impromptu jam partners.



Ever wanted to join a band? I bet you have! Why? Because collaborative
music making is an incredibly enjoyable and rewarding experience. But
the barriers to entry are high: not only do you need to have baseline
musical skills, you also need considerable managerial talent to find and
bring together disorganized musicians. To find partners to jam with,
people use craigslist and band matching sites to try to establish
relationships with randoms. Why not leverage our social networks for
this purpose?

Okay, now that you're fully convinced that there's a huge opportunity to
tap into this friend-jam space, let me introduce [Jam Hunt][]. The idea
behind Jam Hunt is to allow you to manage your musical profile by
specifying a list of instruments you are skilled at and a list of songs
you know how to play. If your friends also maintain such profiles, Jam
Hunt can look across the social graph and discover friends to try
jamming with. Thus, the application enables spontaneous *flash bands*
(in the spirit of [flash mobs][]) to form brief, friendly jam sessions. 

I developed a Jam Hunt prototype for [SAUI class][] while pleasantly
stranded in Pittsburgh as a result of [Eyjafjallajökull's eruption][].
The assignment stipulated that I implement a Facebook application, which
was initially distressing to me, due to the [walled-garden nature][] of
the platform. I was slightly mollified when I discovered three things:

1.  that there is a [way to use django][] to develop Facebook apps.
2.  that the *average* Facebook user has a whopping 130 friends.
3.  that there is a potentially [bright future][] ahead for Facebook

My prospects for having fun while developing something useful, and
potentially viral, and not entirely evil, were on the rise. 

As it turns out, developing a django application for Facebook is no
cakewalk.  Firstly, python is not an officially supported language for
Facebook development. As a result, there are a number of
[semi-abandoned][] [open source projects][] to [bridge that gap][].
Coupled with Facebook's outright disregard for API stability, calling
Notifications.send and Stream.write were next to impossible from python.
But surely writing PHP applications must be a breeze, right? Well,
during the week that I was developing Jam Hunt,
[forum.developers.facebook.com][], one of the most indexed resources on
Facebook API questions, was consistently down. The sorry state of their
hybrid [documentation-wiki][] system was just icing on the cake. 

Anyway, enough bitching! If you have some spare cycles and a Facebook
account, please try [Jam Hunt][]. Whether you find it interesting,
appealing, pointless, ugly, or just outright broken, let me know.

  [Jam Hunt]: http://www.jamhunt.com/
  [flash mobs]: http://en.wikipedia.org/wiki/Flash_mob
  [SAUI class]: http://www.hcii.cmu.edu/courses/software-architecture-user-interfaces-0
  [Eyjafjallajökull's eruption]: http://www.nytimes.com/2010/04/25/weekinreview/25kimmelman.html
  [walled-garden nature]: http://www.codinghorror.com/blog/2007/06/avoiding-walled-gardens-on-the-internet.html
  [way to use django]: http://wiki.developers.facebook.com/index.php/User:PyFacebook_Tutorial
  [bright future]: http://developers.facebook.com/docs/opengraph
  [semi-abandoned]: http://code.google.com/p/simplefacebook/
  [open source projects]: http://github.com/sciyoshi/pyfacebook/tree/master
  [bridge that gap]: http://code.google.com/p/minifb/
  [forum.developers.facebook.com]: http://forum.developers.facebook.com/
  [documentation-wiki]: http://wiki.developers.facebook.com/index.php/New_Design_Platform_Changes


Never Delete Your Gmail Account
===============================
categories: [misc]
posted: 2009-08-28
snip: Bitching and moaning about the perils of deleting your GMail account.



Since moving to the states, I have had nothing but grief from the .ca at the
end of my all-purpose email address. Even in Canada, people would constantly
confuse z3.ca for z3.com, resulting in email bounces. To resolve this problem
once and for all, I decided to switch to Gmail like all the cool kids. I
registered boris.smus long ago out but never used it. The first thing I did was
try to link my z3.ca to the Gmail. When I couldn't figure out how to do that, I
deleted my Gmail account in order to re-create a new pre-linked account with
the same name. Sounds innocent enough, right? 

*Wrong*! Google has an uncharacteristically evil account deletion policy which
is not at all clearly communicated. The deletion page simply says:

> You're trying to delete your Google Account that provides access to
> the Google products listed below. Please select each checkbox to
> confirm you fully understand that you'll no longer be able to use any
> of these products and all information associated with them, and that
> your account will be lost.

Meanwhile, the [F.A.Q.][] reads:

> If you use Gmail with your account, you'll no longer be able to access
> that email. You'll also be unable to reuse your Gmail username.

Long story short, I tried everything in my power to recover the old username. I
found handfuls of frustrated users in the same position as me; some having
deleted their account by accident, others victims of pranks and identity theft.
I asked on official and unofficial Gmail forums, and even consulted with my
Googler friends, all to no avail.  After mourning the loss of
boris.smus@gmail.com, it was time to take a critical look at Google's email
offerings. 

I enjoy Gmail's webmail client very much. It's a fast, intuitive, search and
tag based model with virtually unlimited mailbox storage. In terms of
usability, however, I much prefer Mail on Mac. On the iPhone, the native Mail
client is far superior to the mobile web Gmail client. Fortunately, Google
provides SMTP and IMAP services to fill this need. Sadly, both of these
services are plagued with issues. 

I recently sent an email which had roughly 50 bcc recipients. Google's SMTP
server thought I was a spammer and banned me, *despite my having authenticated
via SSL*.  Perhaps sending email to 50 people is slightly unusual. Still, I
would expect my mail gateway to be capable of performing such a 'feat'. 

The way the Google IMAP maps directories is fundamentally incompatible with
Mail.app expectations. Further, the IMAP server has a limit of 10 simultaneous
connections, which often causes the connection threshold to be reached with
[just two connected clients][]. Additionally, the IMAP server is often down; I
wish I had some data to support that, but I don't. 

When I finally settled on boris@borismus.com, I had a decision to make: do I
use Google Apps or Webfaction for email? I quite like Webfaction, and, perhaps
irrationally, trust them more than Google with my private data. With the above
limitations of Gmail in mind, I did not hesitate to choose Webfaction. I still
miss having a first.last@gmail.com though. What's with the oddly draconian
account deletion rules?

  [F.A.Q.]: http://www.google.com/support/accounts/bin/answer.py?hl=en&answer=32046
  [just two connected clients]: http://mail.google.com/support/bin/answer.py?hl=en&answer=97150


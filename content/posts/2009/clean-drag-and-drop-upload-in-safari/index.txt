Clean drag and drop upload in Safari
====================================
categories: [web, design]
posted: 2009-02-15
snip: A how-to about implementing file drag and drop from the desktop into Safari,
  and presenting the user with a nice UI.



Somehow I often find myself arguing in defense of the web browser as a
viable platform for developing rich applications. In many such
discussions, the issue of interoperability with the desktop arises.
Someone will astutely observe that they **can't even drag and drop**
from their OS file manager into their browser, and all hell will break
loose. 

Happily, this is changing! Since version 3, Safari on Mac OS X
has had support for [dragging and dropping files][] from the finder into
file input boxes. In various kludgy ways, [Firefox][] and [IE][] are now
following suite. 

Unfortunately, even in Safari, the default look of the
`<input type="file">` box is quite ugly and the element itself is
[difficult to style][]. In addition, clicking anywhere in the file input
element causes the default open file dialog to appear. I wanted to
provide drag-and-drop uploading without ugly boxes or browser dialogs.
The solution I came up with involves hiding the file upload box entirely
by setting its opacity to 0, and then preventing the default action on
click via `event.preventDefault()`. Here's a sample of what I mean, with
the entire browser window [converted into a drag area][]. 

Note that the drag area must be the first DOM element to receive the drop event
for this approach to work. Unfortunately I ran into a bug where the file dialog
refuses to bubble click events to other elements below it. This is baffling to
me, since `event.preventDefault()` should not stop event propagation, but only
prevent the default browser handler from being called. You can see what I mean
by trying to click the link in the [sample HTML][converted into a drag area]
file. If this is not a bug, and someone has an answer, I would really
appreciate it.

Note also that there are [java applet][]-based drag and drop solutions, but
they are reserved for developers who have nothing but disdain for their users.

  [dragging and dropping files]: http://www.jakeri.net/2008/04/drag-and-drop-into-file-upload-in-safari/
  [Firefox]: https://addons.mozilla.org/en-US/firefox/addon/2190
  [IE]: http://www.download.com/HTTP-File-Upload-ActiveX-Control/3000-2206_4-10451672.html
  [difficult to style]: http://www.quirksmode.org/dom/inputfile.html
  [converted into a drag area]: drag-drop-upload.html
  [java applet]: http://www.radinks.com/upload/


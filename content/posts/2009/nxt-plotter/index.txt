Plotting Something Radial
=========================
categories: [physical]
posted: 2009-08-07
snip: Attempting to build a plotter based on the radial coordinate system using LEGO
  Mindstorms. Eventually I gave up and built a cartesian plotter.



In anticipation of 48-739: Making Things Interactive, I've been itching to
build something interesting. I decided to create a printing plotter out of my
brother's Mindstorms set. There are already many [excellent plotter designs][]
floating around in the Mindstorms community, so I decided to try something new.
Plotters typically draw straight, edge-aligned lines, since they have a caret
motor which travels along the x-axis and a feed motor which aligns along the
y-axis. There are many variations on this theme. 

What if, instead of using the Cartesian coordinate system, a plotter was built
against radial coordinates. That is, one motor would control the rotation of an
arm (theta in radian coordinates), and one would drive a caret along the arm,
controlling the distance from the origin (r in radian coordinates). I began
building, and despite the ardent help of my young brother, we failed to create
a reasonable construction. The problem we ran into was that as r increased to
the maximum length of the arm, the engine driving theta would not have enough
strength to rotate due to the increased torque. I'm ashamed to admit that we
gave up. 

A month later, I picked up the project again, and due to limited time, decided
to build a Cartesian plotter after all.  I did not consult state of the art of
NXT plotters, and ended up with a plotter of unconventional design. Instead of
a paper feed, a caret travels along the y-axis, and another caret travels along
the first caret on the x-axis. I borrowed wheels from the RCX set, but the rest
is stock NXT. 

<iframe title="YouTube video player" width="600" height="368"
  src="http://www.youtube.com/embed/tZhqjrHSIfE" frameborder="0"
  allowfullscreen></iframe>

I named the robot "Malevich 2" in honor of [Kazimir Malevich][], an avant-guard
Russian painter, famous for pioneering geometric abstract art, especially a
series of [paintings of squares][]. I prefer Malevich 2's rendition of the
square, but maybe that's just me.

  [excellent plotter designs]: http://www.norgesgade14.dk/plotter.php
  [Kazimir Malevich]: http://en.wikipedia.org/wiki/Kazimir_Malevich
  [paintings of squares]: http://en.wikipedia.org/wiki/File:Malevich.black-square.jpg


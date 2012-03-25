Arduino-Nerf Mashup
===================
categories: [physical]
posted: 2009-10-20
snip: Using an Arduino and a servo motor to retrofit a nerf gun with an auto-fire
  mechanism.




My favorite class at CMU is probably [Making Things Interactive][]. For me
it is an opportunity to take my thus far casual electronics hacking to to
the next level. In this article, I'll briefly outline my submission for the
"Motion" assignment. I used a servo motor to control a Nerf gun. I built it
and installed it in my MHCI lab, which has a handful of Nerf pistols
floating around. The idea was to have the gun automatically fire at
unsuspecting visitors as they entered the room. 

To arm it, one manually cocks the gun, loads a dart and resets the program
by pushing the button on the Arduino board. The program then allows 10
seconds for the door to be open before it arms the system. When the system
is armed, the servo activates and shoots the gun as soon as the door is
opened.

<iframe title="YouTube video player" width="600" height="480"
  src="http://www.youtube.com/embed/-XkLRZ2OBRo" frameborder="0"
  allowfullscreen></iframe>

As you can see, I generously used rubber bands and binder clips in this
project. I used them to fasten the servo motor to the Nerf gun. I also used
them to harness a telephone cable by wrapping a rubber band around the RJ11
connector, carefully inserting jumpers, and applying additional pressure (to
ensure contact) with binder clips. This hacked telephone cable stretched
from the gun to the door sensor. 

The circuit was dead simple.  The door acted as a switch for the pull down
resistor circuit. 

  [Making Things Interactive]: http://mtifall09.wordpress.com/


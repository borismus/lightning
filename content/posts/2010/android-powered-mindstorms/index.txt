Android-powered Mindstorms
==========================
categories: [android, web]
posted: 2010-06-27
snip: This LEGO Mindstorms robot is controlled using twitter. When the robot is online,
  it responds to at-replied command to @mindstorms.



A few projects around the internet use an Android phone to control the
LEGO Mindstorms NXT brick. Most involve an ugly hack in which the phone
communicates with a computer over WiFi, and the computer (paired to the
NXT through bluetooth) submits the command to the brick. These projects
typically use Android as a remote control for the NXT robot, and not as
part of the robot itself. Here is a missed opportunity: the NXT could be
augmented by an [impressive list][] of sensors, GPS and Internet access
provided by an Android phone. 

This project does just that, while eliminating the need for a computer in
the loop, so that the Android directly communicates to the NXT. This allows
for more powerful Android-powered NXT robots. As an example, I made a fully
autonomous twitter-controlled robot. The NXT uses two motors to spin in
place or move forward, and a third motor to control the tilt of a Android
phone cradle. The Android phone keeps track of its orientation (compass
heading and tilt), polls [twitter search][] for new commands and sends
commands to the NXT brick. After each command completes, the Android phone
takes a picture and sends it to twitter. Any twitter user can look at the
last few photos, decide which command makes sense to perform next, and issue
it. This approach can be summarized succinctly as "[crowdsourced][]
[teleoperation][]". 

Here's a demonstration video of the robot in action:

<iframe title="YouTube video player" width="600" height="368"
  src="http://www.youtube.com/embed/ATQ_0tySttM" frameborder="0"
  allowfullscreen></iframe>

I think that this marriage of Android and NXT can fuel a very interesting
set of robots impossible to build with the NXT alone. [@mindstorms][] is
offline for now to save some battery life, but code is available at my new
[github][]. If you make use of my code or have some feedback, please reply
below!

  [impressive list]: http://developer.android.com/reference/android/hardware/Sensor.html
  [twitter search]: http://search.twitter.com/
  [crowdsourced]: http://en.wikipedia.org/wiki/Crowdsourcing
  [teleoperation]: http://en.wikipedia.org/wiki/Teleoperation
  [@mindstorms]: http://twitter.com/mindstorms
  [github]: http://github.com/borismus/android-nxt


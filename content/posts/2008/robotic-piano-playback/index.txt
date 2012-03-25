Robotic Piano Playback
======================
categories: [physical]
posted: 2008-11-15
snip: About a LEGO Mindstorms robot that listens to a melody and then plays it back
  on the piano.



After several weeks of casual spare-time research and implementation,
I've finally built a fully working piano playback robot. The usage is
simple: someone plays or sings an arbitrary monophonic melody, and the
robot, parked on a piano bench, will play it back.

<iframe class="youtube-16x9" title="YouTube video player"
  src="http://www.youtube.com/embed/Bo0eCSkjy-0" frameborder="0"
  allowfullscreen></iframe>

The physical construction of the robot is very simple: it consists of a car
with a crane-like arm mounted on it. The arm is used to push down and release a
single piano key. On either end of the car, there are sensors which detect if
the robot has come too close to the edges of the piano bench. The simplicity of
the robot comes at the price of significant limitations, such as only being
able to play back melodies on the white keys. 

Software is the challenging part of the project. The Mindstorms sound sensor is
too primitive to use for pitch analysis. Without hacking it, you can only
extract the amplitude of the sound signal, not any frequency details.  Instead
of the NXT sound sensor, I use a macbook pro and it's built-in microphone. A
computer separate from the NXT is involved, so an additional set of
communication problems arose. 

Here's a rough outline of happens to make the playback work, from capturing the
melody line to playing the melody back.

1.  On the mac, using a [Python AppleScript bridge][], the QuickTime
    Player is invoked and starts capturing audio.
2.  Once the audio is captured into an AIFF file, a very useful 
    [pitch detection library][] called aubio processes the audio file and
    extracts raw frequency-to-time data, sampled at some tick rate.
    Compiling this library on OS X was quite a feat!
3.  Next, the raw data is processed by throwing out extraneous values
    and extracting a melody
4.  Once we have the melody line, we inject it into [an NXC program][],
    and compile it with the nbc compiler
5.  This program is then sent via bluetooth to the robot via nxtcom
6.  Using [NXT_Python][] and [Lightblue Glue][], the robot is told to
    execute the program.

Please let me know if you have any questions or suggestions!

  [Python AppleScript bridge]: http://appscript.sourceforge.net/
  [pitch detection library]: http://aubio.org/
  [an NXC program]: http://bricxcc.sourceforge.net/nbc/
  [Lightblue Glue]: http://www.cs.wlu.edu/~levy/software/nxt_lightblue_glue/
  [NXT_Python]: http://home.comcast.net/~dplau/nxt_python/


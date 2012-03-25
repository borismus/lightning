Crowdsourcing Articles with Mechanical Turk
===========================================
categories: [social]
posted: 2010-01-14
snip: At CMU we conducted user research with real life Mechanical Turk users. We also
  tried to get them to collaboratively write articles using etherpad.



Last semester at CMU, I was involved in a research project involving
[Mechanical Turk][]. The goal was to get Mechanical Turk users (turkers)
to collaborate on creating online wikipedia-style articles. Prior to my
team's involvement, an undergraduate created a mediawiki-based platform
to allow turkers to collaborate on articles. Despite a high
compensation, few turkers completed the task. My team tackled the
problem and came up with some interesting videos on the way. 

We began by conducting contextual interviews with turkers living in
Pittsburgh, all of whom rather unexpectedly, were female. The general
takeaway was clear: turkers are used to very short and repetitive tasks,
but article creation requires a prolonged period of concentration. Our
solution was to significantly tweak the task, making it seem less
arduous. In addition to simplifying the HIT's flow, we switched from
mediawiki to [etherpad][] as the article editing and collaboration
platform. As a result of these changes, we were able to churn out
turker-created articles on a given topic for under ten dollars. Here's a
video of turkers collaborating on an article about Halloween:

<iframe title="YouTube video player" width="600" height="480"
  src="http://www.youtube.com/embed/AmUq_Uovqek" frameborder="0"
  allowfullscreen></iframe>

We started out by creating an etherpad instance with a simple paragraph
about the topic, as well as some article quality guidelines. Next, we
created a series of Mechanical Turk HITs referencing the etherpad
instance's URL. We paid our turkers a quarter up front for accepting the
task, and provided a nickel (up to one dollar) every time they returned
to edit the pad. We had no good way to verify the bonus mechanism, so we
generally gave out the maximum bonus to every active collaborator.
Here's the evolution of an article on Windows 7: 

<iframe title="YouTube video player" width="600" height="480"
  src="http://www.youtube.com/embed/C7pV9fXIo0M" frameborder="0"
  allowfullscreen></iframe>

Watching the etherpad explode in color as multiple turkers
simultaneously edit the same article is still mesmerizing. Though the
quality of the articles was quite low, it generally increased with each
turker's successive pass. Also it's worth noting that errors that we
deliberately inserted in the starting paragraph as well as in real time
were swiftly edited out. Not much quantitative analysis of this
collaboration data has been done yet, though there are plans to conduct
more scientific experiments in the future. 

Several other researchers have been conducting interesting studies on
mturk. Greg Little's work at MIT generated an interesting project called
[TurKit][], intended to simplify setting up experiments such as the one
outlined above. Panos Ipeirotis at NYU runs a variety of turk
experiments as well as an [mturk statistics monitor][], which
continually scrapes Mechanical Turk and generates summary data. Most
recently, Jennifer Boriss surveyed the Turk community about their
browser preferences [projecting a growing interest in Chrome][]. 

These varied Mechanical Turk projects represent only a small fraction of
the potential of crowd-sourced marketplaces. It's especially interesting
to take complex tasks, break them down into turk-sized morsels, and
recombine them again. To improve the article collaboration scenario
discussed here, one could provide an outline of an article and task
turkers to elaborate on each point. This seems to be exactly what Greg's
group is doing in an [collaborative essay writing experiment][].  Such
an approach may also be effectively applicable to crowd-sourced software
development, which I hope to explore in the near future. Do you know
other interesting projects and resources related to Mechanical Turk? If
so, please respond below!

  [Mechanical Turk]: http://www.mturk.com/
  [etherpad]: http://www.etherpad.com/
  [TurKit]: http://groups.csail.mit.edu/uid/turkit/
  [mturk statistics monitor]: http://hyperion.stern.nyu.edu/mturk/
  [projecting a growing interest in Chrome]: http://jboriss.wordpress.com/2010/01/13/mechanical-turk-studies-show-ie-users-discontent-a-growing-interest-in-chrome/
  [collaborative essay writing experiment]: http://groups.csail.mit.edu/uid/deneme/?p=603


Crowdsourcing Code
==================
categories: [social]
posted: 2010-01-16
snip: A brief Mechanical Turk survey to determine whether or not turkers might be
  willing to write code.



As a follow up to my [last post][], I posted a HIT on Mechanical Turk
asking 20 turkers if they know Java. I paid them 5 cents to answer the
question. Surprisingly, 9 of 20 claimed to know. I was amazed at how
strong selection bias was in this case, since surely not 50% of turkers
know how to program! I then asked those turkers who know Java to
complete the following trivial Java method. If they wrote it correctly,
I paid them a 45 cent bonus.

    public static String reverse(String source) {
      // your code here 
    }

Here are the results:

-   4 turkers used `StringBuffer.reverse`
-   3 turkers created a new string by iterating through the original
    string in reverse
-   1 used recursion
-   1 used `Collections.sort(l)`. I'm not sure what was intended

I was hoping that people would fill in the empty reverse method with
their code, but many of them implemented their own methods and helpers.
One person implemented their own class with extensive comments. This
data as a nice existence proof, indicating that turkers can be harnessed
for programming-related crowdsourcing. 

I'd like to turn Mechanical Turkers into Mechanical Coders. Given a set
of unit tests and a method to implement, their work could be
automatically verified based on passing the unit tests. Furthermore,
some turkers could be tasked to write additional unit tests for this
method. Through this technique, it's conceivable to harness the power of
The Turk to implement whole classes. Code quality aside, what sort of
software quality could be achieved by following this approach?

  [last post]: /crowdsourcing-articles-with-mechanical-turk/


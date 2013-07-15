class Syndicator:
    """
    Publishes a link to a service (eg. Twitter, G+).
    """
    def __init__(self, link_url, blog_url, title, body):
        """
        Publishes the link to the service.
        """
        self.title = title
        self.body = body
        self.blog_url = blog_url
        self.link_url = link_url

    def publish(self):
        pass

class TwitterSyndicator(Syndicator):
    """
    Shortens the text and URL to fit within 140 characters and publishes to
    Twitter.
    """
    def publish(self):
        print "Published to Twitter."

class GPlusSyndicator(Syndicator):
    """
    Publishes to Google Plus.
    """
    def publish(self):
        print "Published to G+."

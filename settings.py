import os


class Settings():
    """ A class to store all the settings. """

    def __init__(self):
        """ Initialize. """

        self.poll_every = 10  # minutes

        self.website_to_scrape = ""

        self.root_dir = os.path.dirname(__file__)

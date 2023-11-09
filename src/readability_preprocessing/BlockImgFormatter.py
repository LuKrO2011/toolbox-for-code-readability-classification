from pygments.formatter import Formatter


class BlockImgFormatter(Formatter):

    def __init__(self, **options):
        Formatter.__init__(self, **options)

        self.styles = {

        }

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            color = self.get_color(ttype)
            length = self.get_length(value)


    def get_color(self, ttype):
        return self.styles[ttype]

    def get_length(self, value):
        return len(value)

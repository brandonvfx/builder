import os
import sys

class BuilderError(BaseException):
    pass
# end class BuilderError

class BuilderOptionsError(BuilderError):
    def __init__(self, *args):
        super(BuilderOptionsError, self).__init__(*args)
        self.errors = None
    # end def __init__
# end class BuilderOptionsError
#!/usr/bin/env python
# encoding: utf-8
"""
errors.py

Created by Brandon Ashworth on 2010-12-27.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

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
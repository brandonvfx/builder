#!/usr/bin/env python
# encoding: utf-8
"""
test.py

Created by Brandon Ashworth on 2010-12-24.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import os
import sys
from optparse import make_option

from api.blueprint import Blueprint


#recipes = Library()

class TestPlugin(Blueprint):
    class Meta:
        name = 'test_script'
        version = (1,0,0)
    # end class Meta
    
    options = Blueprint.options + [
        make_option('--testing', action='store', default='test'),
    ]

    def run(self, context, args):
        self.logger.info("Context: %s", context) 


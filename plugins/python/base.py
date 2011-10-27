#!/usr/bin/env python
# encoding: utf-8
"""
base.py

Created by Brandon Ashworth on 2010-12-25.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

from optparse import make_option

from api.blueprint import Blueprint

class PythonBlueprint(Blueprint):
    """ 
    :synopsis: Class ScriptBase
    """
    
    options = Blueprint.options + [
        make_option('-f', '--filename', action='store')
    ]
    
    def validate(self, context, args):
        if not context.get('filename', None) and not args:
            self.addError('-f/--filename option or filename argument missing')
        
        if self.errors:
            return False
        return True
    # end def validateOptions
    
# end class Python
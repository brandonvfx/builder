#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Brandon Ashworth on 2010-12-24.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from plugin.blueprint import Blueprint

class BuildTree(Blueprint):
    class Meta:
        name = 'buildtree'
        namespace = 'svn'
        version = (1,0,0)
    # end class Meta

    tree = dict(
        trunk = dict(
            bin = None,
            src = None,
            lib = None,
            test = None,
        ),
        branches = None,
        tags = None
    )
    
    def run(self, context):
        working_dir = context.working_dir
        make_dirs(working_dir, self.tree)
        
def make_dirs(base_dir, structure):
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    for dirname, subdirs in structure.items():
        dir_path = os.path.join(base_dir, dirname)
        os.mkdir(dir_path)
        if subdirs:
            make_dirs(dir_path, subdirs)
        
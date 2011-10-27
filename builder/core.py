#!/usr/bin/env python
import os
import sys
import inspect
import logging
import traceback
from copy import copy
from glob import glob
from datetime import datetime
from optparse import OptionParser

from pprint import pprint as pp

from .api.logger import logger
from .api.blueprint import Blueprint
from .config import BuilderConfig
from .utils import loadPlugin

INSTALL_DIR = os.path.dirname(__file__)

CONFIG_DIR = os.path.expanduser(
    os.path.expandvars(
        os.getenv('BUILDER_CONFIG_DIR', '~/.builder')
        )
    )

class Builder(object):
    """docstring for Builder"""
    __usage__ = "prog plugin.blueprint [options]"
    
    def __init__(self):
        super(Builder, self).__init__()
        self.build_parser()
        self.config = BuilderConfig(CONFIG_DIR)
        self.plugins = self.config.plugins
        self.loaded_plugins = []
        self.aliases = copy(self.config.aliases)
        self.blueprints = self.get_blueprints()
        self.logger = logger
        self.plugin_data = {}
    # end def __init__
    
    @property
    def help(self):
        return self.parser.print_help()
    # end def
    
    def build_parser(self):
        self.parser = OptionParser(prog='builder', usage=self.__usage__)
        self.parser.add_option('--logging-level', help='Set logging level. (Default: INFO)', action="store", default='INFO')
        self.parser.add_option('--list-namespaces', help='List the available plugins.', action="store_true", default=False)
        self.parser.add_option('--list-blueprints', help='List the available blueprints for a plugin.', 
                                action="store_true", default=False)
    # end def build_parser
    
    def parse_blueprint_name(self, fullname):
        parts = fullname.split('.', 1)
        namespace = parts[0]
        blueprint_name = "default" if len(parts) == 1 else parts[1]
        return namespace, blueprint_name
    # end def parse_plugin_blueprint
    
    def main(self, input_args=sys.argv):
        cmd_args = copy(input_args)
        script = cmd_args.pop(0)
        if not cmd_args:
            print self.help
            sys.exit(2)
        elif '--list-namespaces' in cmd_args:
            print "Installed plugins:"
            print ", ".join(sorted(self.blueprints.keys()))
            sys.exit(0)
        # end if

        blueprint_fullname = cmd_args.pop(0)    
        if blueprint_fullname.startswith('-'):
            options, args = self.parser.parse_args(input_args)
            # if parsed and -h/--help is not there print help anyways 
            # since the args are incorrect.
            print "Blueprint must the be the first argument."
            print self.help
            sys.exit(2) 
            # end if
        # end if
        
        aliased = self.aliases.get(blueprint_fullname)
        if aliased:
            alias_args = aliased.split()
            blueprint_fullname = alias_args.pop(0)
            # Only one level of recursion for aliases at this time.
            nested_alias = self.aliases.get(blueprint_fullname)
            if nested_alias:
                blueprint_fullname = nested_alias
            # end if
            # insert that alias's args before the command line args
            new_cmd_args = alias_args
            new_cmd_args.extend(cmd_args)
            cmd_args = new_cmd_args
        # end if
        
        namespace, blueprint_name = self.parse_blueprint_name(blueprint_fullname)
        if namespace not in self.blueprints:
            print "Error finding blueprint '%s'.\n" % blueprint_fullname
            print "Installed plugins:"
            print ", ".join(sorted(self.plugins))
            print "Namespaces from plugins:"
            print ", ".join(sorted(self.blueprints.keys()))
            sys.exit(1)
        # end if 

        if '--list-blueprints' in cmd_args:
            print "Installed blueprints for '%s':" % (namespace)
            print ", ".join(self.blueprints[namespace].keys())
            sys.exit(0)
        # end if
        
        blueprint_cls = self.blueprints[namespace].get(blueprint_name)
        if not blueprint_cls:
            print "No blueprint '%s'" % (blueprint_name)
            print "Blueprints for '%s':" % (namespace)
            print "\t", ", ".join(self.blueprints[namespace].keys())
            sys.exit(1)
        # end if
        
        self.parser.add_options(blueprint_cls.options)
        self.parser.prog = '%s %s' % (self.parser.prog, blueprint_fullname)
        options, args = self.parser.parse_args(cmd_args)
        # set logging level
        self.logger.setLevel(getattr(logging, options.logging_level.upper()))
        exit_code = 0
        if not self.run_blueprint(
            blueprint_cls, 
            self.build_context(options, self.config.get_blueprint_config(blueprint_fullname)), 
            args):
            exit_code = 1
        # end if
        sys.exit(exit_code)
    # end def main
    
    def build_context(self, option_values, blueprint_config):
        context = {}
        context.update(blueprint_config)
        for option, value in option_values.__dict__.iteritems():
            if value != None:
                context[option] = value
            # end if
        # end for
        if 'list_blueprints' in context:
            del context['list_blueprints']
        # end if
        if 'list_plugins'in context:
            del context['list_plugins']
        # end if
        if 'logging_level'in context:
            del context['logging_level']
        # end if
        return context
    # end def build_context
    
    def run_blueprint(self, blueprint_cls, context, args):
        blueprint = blueprint_cls()
        valid = blueprint.validate(context, args)
        success = False
        if valid:
            try:
                blueprint.run(context, args)
                success = True
            except Exception, run_ex:
                print "Error running '%s' blueprint:\n" % (blueprint)
                print run_ex
                try:
                    blueprint.rollback(context, args)
                except Exception, roll_ex:
                    print "Error rolling back '%s' blueprint:\n" % (blueprint)
                    print roll_ex
                # end try
            # end try
        else:
            blueprint.printErrors()
        return success
    # end def run_blueprint
    
    def get_blueprints(self):
        blueprints = {}
        for plugin_name in self.plugins:
            try:
                plugin = loadPlugin(plugin_name)
                self.loaded_plugins.append(plugin_name)
            except ImportError:
                logger.warn("Plugin '%s' could not be loaded.", plugin_name)
            # end try
            if plugin:
                found_blueprint = False
                for key in dir(plugin):
                    blueprint = getattr(plugin, key, None)
                    if blueprint and inspect.isclass(blueprint) and \
                        issubclass(blueprint, Blueprint) and blueprint != Blueprint:
                        ns = blueprint._config.namespace
                        name = blueprint._config.name
                        aliases = getattr(blueprint._config, 'aliases', [])
                        if ns not in blueprints:
                            blueprints[ns] = {}
                        # end if
                        blueprints[ns][name] = blueprint
                        for alias in aliases:
                            self.aliases['%s.%s' % (ns, alias)] = '%s.%s' % (ns, name) 
                        # end for
                        found_blueprint = True
                    # end if
                # end for
                if not found_blueprint:
                    logger.warn("Not blueprints were found in plugin '%s'", plugin_name)
            # end if
        # end for
        return blueprints
    # end def get_blueprints
# end class Builder


if __name__ == '__main__':
    builder = Builder()
    builder.main()
# end if
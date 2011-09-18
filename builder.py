#!/usr/bin/env python
import os
import sys
import traceback
from copy import copy
from glob import glob
from datetime import datetime
from optparse import OptionParser, Values

from api import cabinet
from api.context import Context
from config import BuilderConfig

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
        self.plugin_dirs = self.get_plugin_dirs()
        self.plugins = self.get_plugins(self.plugin_dirs)
        self.config = BuilderConfig(CONFIG_DIR)
    # end def __init__
    
    @property
    def help(self):
        return self.parser.print_help()
    # end def
    
    def build_parser(self):
        self.parser = OptionParser(prog='builder', usage=self.__usage__)
        self.parser.add_option('--logging-level', help='Set logging level. (Default: INFO)', action="store", default='INFO')
        self.parser.add_option('--list-plugins', help='List the available plugins.', action="store_true", default=False)
        self.parser.add_option('--list-blueprints', help='List the available blueprints for a plugin.', 
                                action="store_true", default=False)
    # end def build_parser
    
    def parse_blueprint_name(self, fullname):
        parts = fullname.split('.', 1)
        plugin_name = parts[0]
        blueprint_name = "default" if len(parts) == 1 else parts[1]
        return plugin_name, blueprint_name
    # end def parse_plugin_blueprint

    def check_for_alias(self, fullname):
        return self.config.aliases.get(fullname)
    # end def check_for_alias
    
    def main(self, input_args=sys.argv):
        cmd_args = copy(input_args)
        script = cmd_args.pop(0)
        if not cmd_args:
            print self.help
            sys.exit(2)
        elif '--list-plugins' in cmd_args:
            print "Installed plugins:"
            print ", ".join(sorted(self.plugins))
            sys.exit(0)
        # end if
        
        blueprint_fullname = cmd_args.pop(0)    
        if blueprint_fullname.startswith('-'):
            options, args = self.parser.parse_args()
            # if parsed and -h/--help is not there print help anyways 
            # since the args are incorrect.
            print "Blueprint must the be the first argument."
            print self.help
            sys.exit(2) 
            # end if
        # end if
        
        aliased = self.check_for_alias(blueprint_fullname)
        if aliased:
            full_alias = aliased.split()
            blueprint_fullname = full_alias.pop(0)
            new_cmd_args = full_alias
            new_cmd_args.extend(cmd_args)
            cmd_args = new_cmd_args
        # end if

        plugin_name, blueprint_name = self.parse_blueprint_name(blueprint_fullname)
        if plugin_name not in self.plugins:
            print "Error finding blueprint '%s'.\n" % plugin_name
            print "Installed plugins:"
            print ", ".join(sorted(self.plugins))
            sys.exit(1)
        # end if 

        plugin = self.import_plugin(plugin_name)
        if '--list-blueprints' in cmd_args:
            print "Installed blueprints for '%s':" % (plugin_name)
            print ", ".join(cabinet.keys())
            sys.exit(0)
        # end if
        
        blueprint_cls = getattr(cabinet, blueprint_name, None)
        if not blueprint_cls:
            print "No blueprint '%s'" % (blueprint_name)
            print "Blueprints for '%s':" % (plugin_name)
            print "\t", ", ".join(cabinet.keys())
            sys.exit(1)
        # end if
        
        self.parser.add_options(blueprint_cls.options)
        self.parser.prog = '%s %s' % (self.parser.prog, blueprint_fullname)
        options, args = self.parser.parse_args(cmd_args)
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
            print "Error:"
            print "\n".join(blueprint.errors)
        return success
    # end def run_blueprint
    
    def get_plugin_dirs(self):
        plugin_dirs = []

        for plugin_dir in os.getenv('BUILDER_PLUGIN_DIR', '').split(':'):
            if plugin_dir.strip():
                plugin_dirs.append(plugin_dir.strip())
        # end for

        plugin_dirs.append(os.path.join(CONFIG_DIR, 'plugins'))
        plugin_dirs.append(os.path.join(INSTALL_DIR, 'plugins'))
        return plugin_dirs
    # end def get_plugin_dirs

    def get_plugins(self, plugin_dirs):
        """
        :synopsis: get_plugins
        :param list *args: List of args
        :param dict **kwargs: Dict of keyword args
        """

        all_plugins = []
        for plugin_dir in plugin_dirs:
            plugin_files = glob(os.path.join(plugin_dir, '*'))
            all_plugins.extend(
                map(lambda f: f.split('.')[0], 
                    map(os.path.basename, plugin_files)
                    )
                )
        # end for
        return list(set(all_plugins))
    # end def get_plugins
    
    def import_plugin(self, plugin):
        old_sys_path = copy(sys.path)
        new_sys_path = copy(self.plugin_dirs)
        new_sys_path.extend(sys.path)
        sys.path = new_sys_path
        try:
            __import__(plugin)
        except Exception, ex:
            raise RuntimeError("Could not import plugin: %s\n%s" % (plugin, ex))
        plugin_mod = sys.modules[plugin]
        sys.path = old_sys_path
        return plugin_mod
    # end def import_plugin
# end class Builder


if __name__ == '__main__':
    builder = Builder()
    builder.main()
# end if
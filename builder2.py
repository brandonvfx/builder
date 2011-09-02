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

INSTALL_DIR = os.path.dirname(__file__)

class Builder(object):
    """docstring for Builder"""
    
    #__usage__ = "\n%prog blueprint [options]\n%prog plugin.blueprint [options]"
    __usage__ = "prog plugin.blueprint [options]"
    
    def __init__(self):
        super(Builder, self).__init__()
        self.build_parser()
        self.plugin_dirs = self.get_plugin_dirs()
        self.plugins = self.get_plugins(self.plugin_dirs)
    # end def __init__
    
    @property
    def help(self):
        return self.parser.print_help()
    # end def
    
    def build_parser(self):
        self.parser = OptionParser(prog='builder', usage=self.__usage__)
        self.parser.add_option('--list-plugins', help='List the available plugins.', action="store_true", default=False)
        self.parser.add_option('--list-blueprints', help='List the available plugins.', action="store_true", default=False)
    # end def build_parser
    
    def parse_blueprint_name(self, fullname):
        parts = fullname.split('.', 1)
        plugin_name = parts[0]
        blueprint_name = "default" if len(parts) == 1 else parts[1]
        return plugin_name, blueprint_name
    # end def parse_plugin_blueprint
    
    def parser_args(self, plugin, blueprint ):
        pass
    # end def parser_args
    
    def main(self):
        cmd_args = copy(sys.argv)
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
        #context = self.build_context(options)
        exit_code = 0
        if not self.run_blueprint(blueprint_cls, self.build_options(options), args):
            exit_code = 1
        # end if
        sys.exit(exit_code)
    # end def main
    
    def build_options(self, option_values):
        options = {}#dict(now=datetime.now())
        #options.update(self.config_file_values)
        options.update(option_values.__dict__)
        return options
    # end def build_options
        
    # def build_context(self, options):
    #     """
    #     :synopsis: buildContext
    #     """
    #     context = Context(**options.__dict__)
    #     return context
    # # end def buildContext
    
    def parse_config_file(self):
        return {}
    # end parse_config_file
    
    def run_blueprint(self, blueprint_cls, options, args):
        blueprint = blueprint_cls()
        # validate the options and args
        valid = blueprint.validate(options, args)
        if valid:
            try:
                blueprint.run(options, args)
            except Exception, ex:
                print "Error running '%s' blueprint:\n" % (blueprint)
                print ex
                return False
            # end try
        else:
            print "Error:"
            print "\n".join(blueprint.errors)
            return False
        return True
    # end def run_blueprint
    
    def get_plugin_dirs(self):
        plugin_dirs = []

        for plugin_dir in os.getenv('BUILDER_PLUGIN_DIR', '').split(':'):
            if plugin_dir.strip():
                plugin_dirs.append(plugin_dir.strip())
        # end for

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
            #plugin_files = filter(os.path.isfile, plugin_files)
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
        __import__(plugin)
        plugin_mod = sys.modules[plugin]
        sys.path = old_sys_path
        return plugin_mod
    # end def import_plugin
# end class Builder


if __name__ == '__main__':
    builder = Builder()
    builder.main()
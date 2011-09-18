import os
import sys
from glob import glob

from . import plugins
from .blueprint import Blueprint

INSTALL_DIR = os.path.dirname(__file__)

def get_plugin_dirs():
    plugin_dirs = []
    
    for plugin_dir in os.getenv('BUILDER_PLUGIN_DIR', '').split(':'):
        if plugin_dir.strip():
            plugin_dirs.append(plugin_dir.strip())
    # end for
            
    plugin_dirs.append(os.path.join(INSTALL_DIR, os.path.pardir, 'plugins'))
    
    return plugin_dirs
# end def get_plugin_dirs

def get_plugins(plugin_dirs):
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

def import_plugin(plugin_name):
    """
    :synopsis: import_plugin
    :param list *args: List of args
    :param dict **kwargs: Dict of keyword args
    """
    __import__(plugin_name)
    return sys.modules[plugin_name]
# end def import_plugin

def load_plugins():
    """
    :synopsis: load_plugins
    :param list *args: List of args
    :param dict **kwargs: Dict of keyword args
    """
    global plugins
    plugin_dirs = get_plugin_dirs()
    for plugin_dir in plugin_dirs:
        sys.path.insert(0, plugin_dir)
    for plugin in get_plugins(plugin_dirs):
        mod = import_plugin(plugin)
        try:
            recipe_library = getattr(mod, 'cabinet')
        except AttributeError:
            print "Plugin '%s' missing recipe library. Not loading plugin." % plugin
            continue
        
        # if 'default' not in recipe_library:
        #     print "Plugin '%s' missing default recipe. Not loading plugin." % plugin
        #     continue
        # else:
        #     plugin_default = recipe_library.recipes['default']
        #     
        # if not callable(plugin_default):
        #     print "Plugin '%s' default recipe is not callable. Not loading plugin." % plugin
        #     continue
        #     
        # if not issubclass(plugin_default, Blueprint):
        #     print "Blueprint '%s.default' a.k.a. '%s' is not a subclass of 'Blueprint'" % (plugin, plugin_default.__class__.__name__) 
            
        plugins[plugin] = dict(mod=mod,
                               recipes=recipe_library.recipes)
    # end for 
    for plugin_dir in plugin_dirs:
       sys.path.pop(sys.path.index(plugin_dir))
    # end for 
# end def load_plugins
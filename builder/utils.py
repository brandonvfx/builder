import imp
import string

def loadPlugin(plugin):
    plugin_parts = plugin.split('.')
    
    package_name = plugin_parts.pop(0)
    f, filename, description = imp.find_module(package_name)
    package = imp.load_module(package_name, f, filename, description)
    last_package = package
    module_name = package_name

    for submodule_name in plugin_parts:
        f, filename, description = imp.find_module(submodule_name, last_package.__path__)
        module_name = '%s.%s' % (module_name, submodule_name)
        try:
            submodule = imp.load_module(module_name, f, filename, description)
            last_package = submodule
        finally:
            if f:
                f.close()
            # end if 
    # end for
    return last_package
# end def load_plugin

def camelcase(name):
    name_parts = name.split('_')
    name_parts = map(string.capitalize, name_parts)
    return ''.join(name_parts)
# end classTitle


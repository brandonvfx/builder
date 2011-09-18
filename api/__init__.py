class Cabinet(object):
    """ 
    :synopsis: Class PluginLibrary
    :param list *args: List of args
    :param dict **kwargs: Dict of keyword args
    """

    def __init__(self):
        """
        :synopsis: __init__
        :param list *args: List of args
        :param dict **kwargs: Dict of keyword args
        """
        self.__blueprints = {}
    # end def __init__
    
    def __str__(self):
        return str(self.__blueprints)
    # end def __str__
    
    def __getattr__(self, name):
        if name.startswith('__') or name.startswith('_%s__' % self.__class__.__name__):
            return super(Cabinet, self).__getattribute__(name)
        else:
            if name in self.__blueprints:
                return self.__blueprints[name]
    # end def __getattr__
    
    def register(self, cls, default=False):
        """
        :synopsis: register
        :param class cls: Dict of keyword args
        :param bool default: Run if now blueprint is passes.
        """
        #ns = getattr(cls._config, "namespace", None)
        name = getattr(cls._config, "name", None)
        if not name:
            raise RuntimeError("'%s' has no name set!" % cls.__name__)
        # end if
        # if ns:
        #     if ns not in self.__blueprints:
        #         self.__blueprints[ns] = {}
        #     self.__blueprints[ns][name] = cls
        # else:
        self.__blueprints[name] = cls
        if default:
            self.__blueprints["default"] = cls
        # end if
    # end def register
    
    def __contains__(self, key):
        return key in self.__blueprints
    # end def __contains__
    
    def keys(self):
        return self.__blueprints.keys()
# end class Cabient

cabinet = Cabinet()
class Context(dict):
    """ 
    :synopsis: Class Context
    :param list *args: List of args
    :param dict **kwargs: Dict of keyword args
    """
    
    def __getattr__(self, key):
        """
        :synopsis: __getattr__
        :param str key: key for look up.
        """
        if key.startswith('__'):
            super(Context, self).__getattribute__(key)
        if key in self:
            return self[key]
        else:
            raise KeyError()
    # end def __getattr__
    
    def __setattr__(self, key, value):
        """
        :synopsis: __setattr__
        :param list *args: List of args
        :param dict **kwargs: Dict of keyword args
        """
        self[key] = value
    # end def __setattr__
    
    def __dir__(self):
        return self.keys()
    # end def __dir__
# end class Context

import os
from optparse import make_option

from .logger import logger

try:
    import jinja2
    from .template import BlueprintTemplateMixIn
except ImportError:
    BlueprintTemplateMixIn = None
    pass

class BlueprintConfig(object):
    keys = ('name', 'namespace', 'version', 'version', 'author', 
                 'email', 'desc', 'help', 'usage', 'aliases')
    
    name = ''
    namespace = ''
    version = ()
    author = ''
    email = ''
    desc = ''
    help = ''
    usage = ''
    aliases = ()
    
    def __init__(self, opts):
        if opts:
            #for key, value in opts.__dict__.iteritems():
            for key in self.keys:
                value = getattr(opts, key, None)
                if value:
                    setattr(self, key, value)
            # end for
        # end if
    # end def __init__
# end class BlueprintConfig

class BlueprintMeta(type):
    def __init__(cls, name, bases, attrs):
        blueprint_config = getattr(cls, 'Meta', None)
        config = BlueprintConfig(blueprint_config)
        setattr(cls, '_config', config)
        setattr(cls, 'logger', logger.getChild(config.name))
    # end def __init__
# end class BlueprintMeta

class BlueprintBase(object):
    """ 
    :synopsis: Blueprint base class
    """
    __metaclass__ = BlueprintMeta
    
    options = [
        make_option('--working_dir', dest='working_dir', action='store', default=os.getcwd()),
    ]

    def __init__(self):
        """
        :synopsis: __init__
        """
        super(BlueprintBase, self).__init__()
        
        if not self._config.version or not self._config.name: #or not self._config.namespace:
            raise RuntimeError("You must set name and version for " \
                "Blueprint class '%s'" % self.__class__.__name__)
        self.errors = []
    # end def __init__
    
    @property
    def usage(self):
        return self._config.usage
    # end def usage
    
    def addError(self, msg):
        self.errors.append(msg)
    # end def addError
    
    def clearErrors(self):
        self.errors = []
    # end def clearErrors

    def printErrors(self):
        for error in self.errors:
            self.logger.error(error)
        # end for
    # end def printErrors
    
    def validate(self, context, args):
        """
        Validate incoming options
        
        :param optparse.Values options: option parser values
        """
        self.errors = []
        return True
    # end def validateOptions
    
    def run(self, context, args):
        raise NotImplementedError('You must subclass Blueprint and implement the run method.')
    # end def run
    
    def rollback(self, context, args):
        pass
    # end def rollback
# end class BlueprintBase
        
if BlueprintTemplateMixIn:
    class Blueprint(BlueprintBase, BlueprintTemplateMixIn):
        pass
    # end class Blueprint
else:
    class Blueprint(BlueprintBase):
        pass
    # end class Blueprint
# end if
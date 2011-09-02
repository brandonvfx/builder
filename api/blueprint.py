import os
import datetime
from copy import deepcopy
from optparse import make_option, OptionParser

# 3rd Party Libs
from tornado.template import Loader
#from jinja2 import Environment, FileSystemLoader

# Project Libs
from context import Context
from .errors import BuilderOptionsError


class BlueprintConfig(object):
    name = ''
    namespace = ''
    version = ()
    author = ''
    email = ''
    desc = ''
    help = ''
    usage = ''
    
    def __init__(self, opts):
        if opts:
            for key, value in opts.__dict__.iteritems():
                setattr(self, key, value)
            # end for
        # end if
    # end def __init__
# end class BlueprintMeta

class BlueprintBase(type):
    def __init__(cls, name, bases, attrs):
        blueprint_config = getattr(cls, 'Meta', None)
        config = BlueprintConfig(blueprint_config)
        setattr(cls, '_config', config)
    # end def __init__
# end class BlueprintBase

class Blueprint(object):
    """ 
    :synopsis: Blueprint base class
    """
    __metaclass__ = BlueprintBase
    
    options = [
        make_option('--prefix', dest='working_dir', action='store', default=os.getcwd()),
    ]
    
    template_dir = ''
    
    def __init__(self):
        """
        :synopsis: __init__
        """
        super(Blueprint, self).__init__()
        
        if not self._config.version or not self._config.name: #or not self._config.namespace:
            raise RuntimeError("You must set name, version, and namespace for " \
                "Blueprint class '%s'" % self.__class__.__name__)
        self.errors = []
        self.input = None
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
    
    def validate(self, options, args):
        """
        Validate incoming options
        
        :param optparse.Values options: option parser values
        """
        self.errors = []
        return True
    # end def validateOptions
    
    def renderTemplate(self, template_file, options):
        loader = Loader(self.template_dir)
        context = deepcopy(options)
        context['now'] = datetime.datetime.now()
        return loader.load(template_file).generate(**context)
    # end def renderTemplate
    
    def run(self, context, args):
        raise NotImplementedError('You must subclass Blueprint and implement the run method.')
    # end def run
    
    def rollback(self, context, args):
        pass
    # end def rollback
# end class Blueprint
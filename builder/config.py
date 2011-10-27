import os
import string
import yaml

class BuilderConfig(object):
    config_file = 'config.yml'
    
    def __init__(self, config_dir):
        self.config_dir = config_dir
        
        self.plugins = []
        self.aliases = {}
        self.context_defaults = {}
        self.blueprint_defaults = {}

        self.load_config()
    # end def __init__

    def load_config(self):
        config_path = os.path.join(self.config_dir, self.config_file)
        if not os.path.exists(config_path):
            self.create_config_dir()
            return
        # end if 

        config = yaml.load(open(config_path, 'r'), Loader=getattr(yaml, 'CLoader', yaml.Loader))
        context_defualts_sections = ['builder', 'context']
        
        for section in context_defualts_sections:
            self.context_defaults.update(config.get(section, {}))
        # end for
        
        self.aliases = config.get('aliases', {})
        self.plugins = config.get('plugins', [])
        
        for section in config:
            if section not in ['builder', 'context'] and section not in ['aliases', 'plugins']:
                print section
                self.blueprint_defaults.update(config.get(section, {}))
            # end if
        # end for
    # end def load_config

    def get_blueprint_config(self, blueprint):
        config = {}
        config.update(self.context_defaults)
        config.update(self.blueprint_defaults.get(blueprint, {}))
        return config
    # end def get_blueprint_config

    def create_config_dir(self):
        dirs = ['']
        files = {self.config_file: dict(builder={}, context={}, aliases={}, plugins=[])}

        for directory in dirs:
            try:
                os.makedirs(os.path.join(self.config_dir, directory))
            except OSError:
                pass
            # end try
        # end for
        for file_name in files:
            path = os.path.join(self.config_dir, file_name)
            fd = open(path, 'w')
            yaml.dump(files[file_name], fd, Dumper=getattr(yaml, 'CDumper', yaml.Dumper))
        # end for
        print "Created User Config: %s" % (self.config_dir)
    # end def create_config_dir
# end class Preferences
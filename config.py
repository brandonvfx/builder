import os
import ConfigParser

class BuilderConfig(object):
	def __init__(self, config_dir):
		self.config_dir = config_dir
		
		self.aliases = {}
		self.context_defaults = {}
		self.blueprint_defaults = {}

		self.load_config()
	# end def __init__

	def load_config(self):
		config_path = os.path.join(self.config_dir, 'config')
		
		if not os.path.exists(config_path):
			self.create_config_dir()
			return
		# end if 

		config = ConfigParser.ConfigParser()
		config.read(config_path)

		context_defualts_sections = ['builder', 'context']
		aliases_sections = ['aliases']

		for section in config.sections():
			if section in context_defualts_sections:
				self.context_defaults.update(dict(config.items(section)))
			elif section in aliases_sections:
				self.aliases.update(dict(config.items(section)))
			else:
				self.blueprint_defaults.update({section:dict(config.items(section))})
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
		dirs = ['plugins']
		files = ['config']

		for directory in dirs:
			os.makedirs(os.path.join(self.config_dir, directory))
		# end for
		for file_name in files:
			path = os.path.join(self.config_dir, file_name)
			fd = open(path, 'w')
			fd.close()
		# end for
		print "Created User Config: %s" % (self.config_dir)
	# end def create_config_dir
# end class Preferences
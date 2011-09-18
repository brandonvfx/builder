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
		config = ConfigParser.ConfigParser()
		config.read(os.path.join(self.config_dir, 'config'))

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
# end class Preferences
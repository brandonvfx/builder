# builder

Builder is a tool/framework for automating task. It allows you to create simple "blueprints" to be executed from the command line.

## Usage
	
	builder <namespace>.<blueprint> [options]
	
	Example:
	builder python.command_line_script --working-dir=/tmp -f script.py
	namespace: python
	blueprint: command_line_script 
	options: --working-dir=/tmp -f script.py

## Configuration

When builder is run for the first time it will automatically create a .builder directory in your home directory where it will place a config.yml file. This config.yml is where all your builder configuration goes.

### Sections

#### builder
This section has 2 settings for now. name and email, the values of this will be passed to any blueprint when it is run.

#### context
This section is free form you can define any extra key value pair you would like to send to any blueprint when it is run. This is handy for values that span many blueprints.

#### aliases
Here you can define aliases to blueprints. The aliases can be just the full blueprint name (<namespace>.<blueprint>) or a command line string (full blueprint name plus any options.)

#### plugins
This is a list of python modules to load blueprints from. The blueprint should be importable directly from the module you provide, submodules will not be searched. 

#### blueprint defaults
To add default values for a specific blueprint you can define a section using the full blueprint name as key section key with a nested dictionary of key value pairs mapping to the options of that blueprint.

	python.command_line_script:
		file_name: testing.py

#### Example Config file
	
	aliases: 
	    t: testing.test_script
	builder: 
	    email: email@yourdomain.com
	    name: Your Name
	context: 
	    twitter_name: @twitter_name
	plugins: 
	    - blueprints.test
	    - blueprints.python
	    - blueprints.django
	python.command_line_script:
	    filename: /tmp/testing.py

## Creating A Blueprint

There is a repo for the best of the best blueprints called [builder_blueprints](http://github.com/brandonvfx/builder_blueprints). For now it is just kind of a reference for how to build a blueprint.

Basic blueprint class:

	# required if your blueprint needs options
	from optparse import make_option

	# Blueprint parent class
	from builder.api.blueprint import Blueprint

	class MyBlueprint(Blueprint):
		options = Blueprint.options + [
        	# your options using make_option
			# please don't set dest for now.
    	]

		# blueprint configuration
		class Meta:
			name = 'my_blueprint_name' 			# REQUIRED
		    namespace = 'blueprint_namespace' 	# REQUIRED
		    version = (1,0,0) 					# REQUIRED
		    author = 'Your Name'
		    email = 'YourEmail@your_domain.com'
		    desc = 'Some text here.'
		    help = 'Help text here.'
		    usage = 'Usage Text here.'
		    aliases = ('aliases', 'you', 'want')
		
		# This method is used validate the input data before the run
		# method is called.
		def validate(self, context, args):
			# If there are errors. You can use the self.addError('message')
			# method to send error message back to the user.
	
			# it should return True if all requirements are met and False if not.
			return True
		
		# The only method required.
		def run(self, context, args):
			# context is a dictionary of values from the configuration and command line.
			# args is list of the non-option args from the command line.
			
			# execute any code you want here.
			# if you need to send messages to the user you can use the logger.
			self.log.info('Message for user')
			
			# if an error is raise during execution of run it will be seen as 
			# error and the rollback will be called.

		# This method is called if your run method fails. 
		def rollback(self, context, args):
			# This should reverse everything the run method did, if possible.
			pass

If jinja2 is installed you have access to templating also.
		
	# When using templates you will need to define the class variable
	# template_dir to tell jinja2 where to find your templates.
	template_dir = '/some/path'

	def run(self, context, args):
		data = self.renderTemplate('template_file.txt', context, args)

The templates receives a context containing all the values from context plus the current datetime as 'now' and the args as 'arg_list'.
	
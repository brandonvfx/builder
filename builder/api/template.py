import os
import datetime
from copy import deepcopy

from jinja2 import Environment, FileSystemLoader

class BlueprintTemplateMixIn(object):
    """docstring for BlueprintTemplateMixIn"""
    template_dir = None
    def renderTemplate(self, template_name, options):
    	template_dirs = []
    	env_template_dirs = os.path.expandvars('$BUILDER_TEMPLATE_PATH').split(os.path.pathsep)
    	if env_template_dirs:
    		template_dirs.extend(env_template_dirs)
    	# end if
    	if self.template_dir:
    		template_dirs.append(self.template_dir)
    	# end if

    	jinja_env = Environment(loader=FileSystemLoader(template_dirs))
        
        context = deepcopy(options)
        context['now'] = datetime.datetime.now()

        return jinja_env.get_template(template_name).render(context)
    # end def renderTemplate
# end class BlueprintTemplateMixIn
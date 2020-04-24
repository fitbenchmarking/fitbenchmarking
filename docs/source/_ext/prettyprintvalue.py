from docutils import nodes
from docutils.parsers.rst import Directive, directives
from importlib import import_module
from pprint import pformat


class PrettyPrintModuleValue(Directive):

    has_content = False
    optional_arguments = 3
    option_spec = {
        'module': directives.unchanged_required,
        'var': directives.unchanged_required,
    }

    def run(self):
        inp_module = self.options['module']
        inp_var = self.options['var']

        # Get variable value
        module = import_module(inp_module)
        value = getattr(module, inp_var)
        value = pformat(value, 2, width=68)

        paragraph_node = nodes.literal_block(text=value)
        return [paragraph_node]


def setup(app):
    app.add_directive("prettyprintmodulevalue", PrettyPrintModuleValue)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

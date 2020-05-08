"""
Module which allows access to variables in the code
"""

from pprint import pformat
from importlib import import_module
from docutils import nodes
from docutils.parsers.rst import Directive, directives


class PrettyPrintModuleValue(Directive):
    """
    Class which enables documentation to access variables from code base
    """

    has_content = False
    optional_arguments = 2
    option_spec = {
        'module': directives.unchanged_required,
        'var': directives.unchanged_required,
    }

    def run(self):
        """
        Accesses variable
        """
        inp_module = self.options['module']
        inp_var = self.options['var']

        # Get variable value
        module = import_module(inp_module)
        value = getattr(module, inp_var)
        value = pformat(value, 2, width=68)

        paragraph_node = nodes.literal_block(text=value)
        return [paragraph_node]


def setup(app):
    """
    Setup PrettyPrintModuleValue for use in docs
    """
    app.add_directive("prettyprintmodulevalue", PrettyPrintModuleValue)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

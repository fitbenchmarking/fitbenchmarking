from docutils import nodes
from docutils.parsers.rst import Directive, directives
from importlib import import_module
import os


class PrettyPrintValue(Directive):

    has_content = False
    optional_arguments = 3
    option_spec = {
        'module': directives.unchanged_required,
        'class': directives.unchanged_required,
        'var': directives.unchanged_required,
    }

    def run(self):
        inp_module = self.options['module']
        inp_class = self.options['class']
        inp_var = self.options['var']

        # Get variable value
        module = import_module(inp_module)
        instance = getattr(module, inp_class)()
        value = str(getattr(instance, inp_var))

        # Remove leading whitespace
        first_line, value = value.split('\n', 1)
        while(first_line.strip() == ''):
            first_line, value = value.split('\n', 1)
        value = first_line + '\n' + value
        num_spaces = len(first_line) - len(first_line.lstrip())
        value = value.replace('\n' + (' ' * num_spaces), '\n')[num_spaces:]

        paragraph_node = nodes.literal_block(text=value)
        return [paragraph_node]


def setup(app):
    app.add_directive("prettyprintvalue", PrettyPrintValue)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

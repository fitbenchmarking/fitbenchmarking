"""
Command to print the help information for setup.py
"""
from __future__ import (absolute_import, division, print_function)

from distutils.core import Command


class Help(Command):
    """
    Command class to display help message
    """

    description = "Provide help on using this setup"
    user_options = []

    def initialize_options(self):
        """ No args hence pass """
        pass

    def finalize_options(self):
        """ No args hence pass """
        pass

    def run(self):
        """
        Print out the help documentation to console
        """
        help_text = (('Usage       :', 'python setup.py [commands]'),
                     ('Description :', 'Script to setup project and '
                                       'testing environment'),
                     ('', ''),
                     ('Commands: ', '')
                    )
        commands = (('     externals', 'Install all external programs'),
                    ('              ', 'Optional: Use the -s argument to '
                                       'specify a comma separated list of '
                                       'packages:'),
                    ('              ', ' python setup.py externals -s mantid'),
                    ('              ', 'Available options: mantid'),
                    ('     help', 'Show the help documentation (i.e. this)')
                   )

        for args in help_text:
            print('{0:<15} {1:<10}'.format(*args))
        for command in commands:
            print('{0:<20} {1:<10}'.format(*command))

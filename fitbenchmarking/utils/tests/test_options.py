'''
Test the options.py file
'''

import configparser
import datetime
import os
import unittest

from fitbenchmarking.utils.options import Options

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class OptionsTests(unittest.TestCase):
    def setUp(self):
        '''
        Create an options file and store input
        '''
        config_str = """
            [MINIMIZERS]
            scipy: nonesense
                   another_fake_minimizer
            dfogn: test

            [FITTING]
            use_errors: no
            """
        opts = {'MINIMIZERS': {'scipy': ['nonesense', 'another_fake_minimizer'],
                               'dfogn': ['test']},
                'FITTING': {'use_errors': False}
                }

        opts_file = 'test_options_tests_{}.txt'.format(datetime.datetime.now())
        with open(opts_file, 'w') as f:
            f.write(config_str)

        self.options = opts
        self.options_file = opts_file

    def tearDown(self):
        os.remove(self.options_file)

    def test_minimizers(self):
        ...

    def test_use_errors(self):
        ...
    
    ...

if __name__ == '__main__':
    unittest.main()

'''
Test the options.py file
'''

import datetime
import json
import os
import unittest

import fitbenchmarking.utils.options as options

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class OptionsTests(unittest.TestCase):
    def setUp(self):
        '''
        Create an options file and store input
        '''

        opts = {'option1': True,
                'option2': [0, 1, 2, 3, 4, 5],
                'option3': {'foo': 1, 'bar': 2}}

        opts_file = 'test_options_tests_{}.txt'.format(datetime.datetime.now())
        with open(opts_file, 'w') as f:
            f.write(json.dumps(opts))

        self.options = opts
        self.options_file = opts_file

    def tearDown(self):
        os.remove(self.options_file)

    def testGetOption(self):
        # Test whole options dict
        opts = options.get_option(options_file=self.options_file)
        self.assertEqual(opts, self.options)

        # Test individual options
        for k in self.options:
            val = options.get_option(options_file=self.options_file, option=k)
            self.assertEqual(val, self.options[k])

        # Test missing options
        with self.assertRaises(ValueError):
            options.get_option(options_file=self.options_file, option='not_real')

        # Test missing file
        with self.assertRaises(FileNotFoundError):
            fake_file = 'fake_{}'.format(self.options_file)
            options.get_option(options_file=fake_file)


if __name__ == '__main__':
    unittest.main()

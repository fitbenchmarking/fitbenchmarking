'''
Test the options.py file
'''
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
            num_runs: 2
            software: foo
                      bar

            [PLOTTING]
            colour_scale: 17.1, a_string?
                          inf, another_string
            comparison_mode: abs
            results_dir: new_results
            """
        opts = {'MINIMIZERS': {'scipy': ['nonesense',
                                         'another_fake_minimizer'],
                               'dfogn': ['test']},
                'FITTING': {'use_errors': False,
                            'num_runs': 2,
                            'software': ['foo', 'bar']},
                'PLOTTING': {'colour_scale': [(17.1, 'a_string?'),
                                              (float('inf'), 'another_string')],
                             'comparison_mode': 'abs',
                             'results_dir': 'new_results'}
                }

        opts_file = 'test_options_tests_{}.txt'.format(
            datetime.datetime.now())
        with open(opts_file, 'w') as f:
            f.write(config_str)

        self.options = opts
        self.options_file = opts_file

    def tearDown(self):
        os.remove(self.options_file)

    def test_from_file(self):
        options = Options(file_name=self.options_file)
        for key in self.options['MINIMIZERS']:
            self.assertEqual(self.options['MINIMIZERS'][key],
                             options.minimizers[key])

        fitting_opts = self.options['FITTING']
        self.assertEqual(fitting_opts['use_errors'], options.use_errors)
        self.assertEqual(fitting_opts['num_runs'], options.num_runs)
        self.assertEqual(fitting_opts['software'], options.software)

        plotting_opts = self.options['PLOTTING']
        self.assertEqual(plotting_opts['colour_scale'], options.colour_scale)
        self.assertEqual(plotting_opts['comparison_mode'],
                         options.comparison_mode)
        # Use ends with as options creates an abs path rather than rel.
        self.assertTrue(
            options.results_dir.endswith(plotting_opts['results_dir']))


if __name__ == '__main__':
    unittest.main()

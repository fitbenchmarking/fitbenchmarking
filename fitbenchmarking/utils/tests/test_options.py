'''
Test the options.py file
'''
import datetime
import os
import unittest

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


class OptionsTests(unittest.TestCase):
    def setUp(self):
        '''
        Create an options file and store input
        '''
        # None of these options should be the defaults in
        # "fitbenchmarking/utils/default_options.ini"
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
            jac_method: random_method

            [PLOTTING]
            make_plots: no
            colour_scale: 17.1, b_string?
                          inf, final_string
            comparison_mode: abs
            table_type: acc
                        runtime
            results_dir: new_results
            """
        incorrect_config_str = """
            [FITTING]
            use_errors: correct
            num_runs: two
            [PLOTTING]
            make_plots: incorrect_falue
            """
        opts = {'MINIMIZERS': {'scipy': ['nonesense',
                                         'another_fake_minimizer'],
                               'dfogn': ['test']},
                'FITTING': {'use_errors': False,
                            'num_runs': 2,
                            'software': ['foo', 'bar'],
                            'jac_method': 'random_method'},
                'PLOTTING': {'make_plots': False,
                             'colour_scale': [(17.1, 'b_string?'),
                                              (float('inf'), 'final_string')],
                             'comparison_mode': 'abs',
                             'table_type': ['acc', 'runtime'],
                             'results_dir': 'new_results'}
                }

        opts_file = 'test_options_tests_{}.txt'.format(
            datetime.datetime.now())
        with open(opts_file, 'w') as f:
            f.write(config_str)
        self.options = opts
        self.options_file = opts_file

        opts_file_incorrect = 'test_incorrect_options_tests_{}.txt'.format(
            datetime.datetime.now())
        with open(opts_file_incorrect, 'w') as f:
            f.write(incorrect_config_str)
        self.options_file_incorrect = opts_file_incorrect

    def tearDown(self):
        os.remove(self.options_file)
        os.remove(self.options_file_incorrect)

    def test_from_file(self):
        options = Options(file_name=self.options_file)
        for key in self.options['MINIMIZERS']:
            self.assertEqual(self.options['MINIMIZERS'][key],
                             options.minimizers[key])

        fitting_opts = self.options['FITTING']
        self.assertEqual(fitting_opts['software'], options.software)
        self.assertEqual(fitting_opts['jac_method'], options.jac_method)

        plotting_opts = self.options['PLOTTING']
        self.assertEqual(plotting_opts['colour_scale'], options.colour_scale)
        self.assertEqual(plotting_opts['comparison_mode'],
                         options.comparison_mode)
        self.assertEqual(plotting_opts['table_type'], options.table_type)
        # Use ends with as options creates an abs path rather than rel.
        self.assertTrue(
            options.results_dir.endswith(plotting_opts['results_dir']))

    def test_write(self):
        """
        Test that the options writer works.
        """
        options = Options(file_name=self.options_file)
        new_file_name = 'copy_of_{}'.format(self.options_file)

        options.write(new_file_name)
        new_options = Options(new_file_name)

        os.remove(new_file_name)

        self.assertDictEqual(options.__dict__, new_options.__dict__)

    def test_make_plots_false(self):
        with self.assertRaises(exceptions.OptionsError):
            Options(file_name=self.options_file_incorrect)

    def test_make_plots_true(self):
        options = Options(file_name=self.options_file)
        plotting_opts = self.options['PLOTTING']
        self.assertEqual(plotting_opts['make_plots'], options.make_plots)

    def test_use_errors_false(self):
        with self.assertRaises(exceptions.OptionsError):
            Options(file_name=self.options_file_incorrect)

    def test_use_errors_true(self):
        options = Options(file_name=self.options_file)
        plotting_opts = self.options['FITTING']
        self.assertEqual(plotting_opts['use_errors'], options.use_errors)

    def test_num_runs_non_int_value(self):
        with self.assertRaises(exceptions.OptionsError):
            Options(file_name=self.options_file_incorrect)

    def test_num_runs_int_value(self):
        options = Options(file_name=self.options_file)
        plotting_opts = self.options['FITTING']
        self.assertEqual(plotting_opts['num_runs'], options.num_runs)


if __name__ == '__main__':
    unittest.main()

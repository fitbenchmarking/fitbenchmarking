'''
Test the options write function
'''
import os
import unittest

from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


class OptionsWriteTests(unittest.TestCase):
    """
    Tests for options.write
    """

    def setUp(self):
        '''
        Create an options file and store input
        '''
        config_str = """
            [MINIMIZERS]
            scipy: CG
                   Powell
            dfo: dfogn

            [FITTING]
            algorithm_type: all
            num_runs: 2
            software: scipy
                      dfo
            jac_method: scipy

            [JACOBIAN]
            scipy: cs

            [OUTPUT]
            results_dir: new_results/
            make_plots: no
            colour_map: viridis
            cmap_range: [0, 0.5]
            colour_ulim: 50
            comparison_mode: abs
            table_type: acc
                        runtime

            [LOGGING]
            file_name: THE_LOG.log
            append: yes
            level: DEBUG
            external_output: display
            """

        opts_file = 'test_options_tests.ini'
        with open(opts_file, 'w', encoding='utf-8') as f:
            f.write(config_str)
        self.options_file = opts_file

    def tearDown(self):
        """
        Removes options file after tests are run
        """
        os.remove(self.options_file)

    def test_write(self):
        """
        Test that the options writer works.
        """
        options = Options(file_name=self.options_file)
        new_file_name = f'copy_of_{self.options_file}'

        options.write(new_file_name)
        new_options = Options(new_file_name)

        os.remove(new_file_name)

        self.assertEqual(options.stored_file_name, self.options_file)
        self.assertEqual(new_options.stored_file_name, new_file_name)

        # Overwrite file names
        options.stored_file_name = ""
        new_options.stored_file_name = ""

        self.assertDictEqual(options.__dict__, new_options.__dict__)

    def test_write_to_stream(self):
        """
        Test that the stream options writer works.
        """
        options = Options(file_name=self.options_file)
        new_file_name = f'copy_of_{self.options_file}'

        with open(new_file_name, 'w', encoding='utf-8') as f:
            options.write_to_stream(f)

        new_options = Options(new_file_name)

        self.assertEqual(options.stored_file_name, self.options_file)
        self.assertEqual(new_options.stored_file_name, new_file_name)

        # Overwrite file names
        options.stored_file_name = ""
        new_options.stored_file_name = ""

        os.remove(new_file_name)
        self.assertDictEqual(options.__dict__, new_options.__dict__)

    def test_create_config(self):
        # pylint: disable=W0212
        """
        Test that created config object contains all valid sections.
        """
        options = Options(file_name=self.options_file)

        config = options._create_config()
        for section in options.VALID_SECTIONS:
            self.assertTrue(config.has_section(section))

    def test_user_section_valid(self):
        """
        Tests that the user defined sections are correct.
        """
        config_str = """
            [MINIMIZERS]

            [FITTING]
            """
        opts_file = 'test_options_tests_valid.ini'
        with open(opts_file, 'w', encoding='utf-8') as f:
            f.write(config_str)
        options = Options(opts_file)
        self.assertEqual(options.stored_file_name, opts_file)
        os.remove(opts_file)

    def test_user_section_invalid(self):
        """
        Tests that the user defined sections are incorrect.
        """
        config_str = """
            [MINIMIZERS SECTION]

            [FITTING]
            """
        opts_file = 'test_options_tests_valid.ini'
        with open(opts_file, 'w', encoding='utf-8') as f:
            f.write(config_str)
        with self.assertRaises(exceptions.OptionsError):
            Options(opts_file)
        os.remove(opts_file)


if __name__ == '__main__':
    unittest.main()

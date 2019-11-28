import os
import unittest

from example_scripts import example_runScripts


class TestExampleScripts(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # inputs. Include at least one test with inputs
        self.args = ['tests', '/../fitbenchmarking/fitbenchmarking_default_options.json']

        # get curdir and store for teardown
        self.cwd = os.getcwd()

        # get rootdir of repo
        root_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

        # chdir to root dir
        os.chdir(root_dir)

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd)

    def test_examplescript(self):
        example_runScripts.main([])

    def test_examplescript_with_inputs(self):
        example_runScripts.main(self.args)

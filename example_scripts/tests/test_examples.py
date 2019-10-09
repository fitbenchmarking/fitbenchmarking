import os
import unittest

from example_scripts import (example_runScripts,
                             example_runScripts_mantid)


class TestExampleScripts(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        # inputs
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
        example_runScripts.main(self.args)

## Commented out as pytest freezes when running the mantid script...
#    def test_examplescript_mantid(self):
#        example_runScripts_mantid.main(self.args)


## Uncomment when expert script works again
#    def test_examplescript_expert(self):
#        example_runScripts_expert.main(self.args)

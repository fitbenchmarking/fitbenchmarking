"""
Module which accesses the values in algorithm_check for each
controller that correspond to a given key from the dictionary
"""

import os
from importlib import import_module
from pprint import pformat

from docutils import nodes
from docutils.parsers.rst import Directive, directives


class AlgorithmCheckDocs(Directive):
    """
    Class which enables documentation to access algorithm_check
    values for each controller
    """

    has_content = False
    optional_arguments = 1
    # when algorithmcheckdocs is called, a value for
    # key should also be given e.g.
    # .. algorithmcheckdocs::
    #   :key: general
    option_spec = {
        "key": directives.unchanged_required,
    }

    def run(self):
        """
        Accesses variable
        """
        inp_key = self.options["key"]

        # import controller factory
        factory = import_module(
            "fitbenchmarking.controllers.controller_factory"
        )

        # set relative path to controllers directory
        cwd = os.path.dirname(__file__)
        dirname = os.path.join(cwd, "../../../fitbenchmarking/controllers")

        # loop over all fitbenchmarking controllers, and extract the minimizers
        # in algorithm_check that correspond to the given dict key
        value = {}
        for filename in os.listdir(dirname):
            if not filename.endswith(".py") or filename in [
                "__init__.py",
                "base_controller.py",
                "controller_factory.py",
                "matlab_mixin.py",
            ]:
                continue
            software_name = os.path.splitext(filename)[0].replace(
                "_controller", ""
            )

            controller_class = factory.ControllerFactory.create_controller(
                software_name
            )
            alg_dict = getattr(controller_class, "algorithm_check")

            value[software_name] = alg_dict[inp_key]

        value = pformat(value, width=80)
        paragraph_node = nodes.literal_block(text=value)
        return [paragraph_node]


def setup(app):
    """
    Setup AlgorithmCheckDocs for use in docs
    """
    app.add_directive("algorithmcheckdocs", AlgorithmCheckDocs)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

import pytest

# set choices for --test-type
test_choices = ["all", "default", "matlab", "mantid", "local_only"]


def pytest_addoption(parser):
    """
    Command line input function which requires one of test_choices
    as an input
    """
    parser.addoption(
        "--test-type",
        action="store",
        default="all",
        type=str,
        choices=test_choices,
    )


def pytest_configure(config):
    """
    Sets variable `pytest.test_type` to be used within testing
    """
    pytest.test_type = config.getoption("--test-type")


def run_for_test_types(test_type, *test_types):
    """
    Sets decorator that specifies the test types for which a
    class/function should be skipped

    :param test_type: the test type selected by the user
    :type test_type: str
    :param test_types: the test types for which the class/function
                       should be run
    :type test_types: str

    :return: decorator that specifies if class/function should be
             skipped based on chosen test_type
    :rtype: callable
    """
    to_skip = [type for type in test_choices if type not in test_types]
    return pytest.mark.skipif(
        test_type in to_skip,
        reason="Tests can't be run with selected test type",
    )

import pytest


def pytest_addoption(parser):
    """
    Command line input function which requires 'all', 'default' or 'external'
    as an input
    """
    parser.addoption(
        "--test-type", action="store", default="all", type=str,
        choices=['all', 'default']
    )


def pytest_configure(config):
    """
    Sets variable `pytest.test_type` to be used within testing
    """
    pytest.test_type = config.getoption('--test-type')

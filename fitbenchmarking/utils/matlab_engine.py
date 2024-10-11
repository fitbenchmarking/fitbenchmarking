"""
Manage the persistent variables withing the matlab engine
"""

import matlab.engine

ENG = matlab.engine.start_matlab()


def add_persistent_matlab_var(name: str) -> None:
    """
    Manage a list of variables to keep when clearing memory.

    :param name: The variable to add to the persistent list
    :type name: str
    """
    ENG.evalc(
        """if ~exist('persistent_vars'); 
        persistent_vars = {'persistent_vars'};end;"""
    )
    ENG.evalc(
        f"if ~ismember('{name}', persistent_vars);"
        f" persistent_vars{{end+1}} = '{name}';"
        "end;"
    )


def clear_non_persistent_matlab_vars() -> None:
    """
    Clear any non-persistent variables.
    That is any variable that hasn't been added via the above method.
    """
    ENG.clearvars("-except", r"persistent_vars{:}", nargout=0)


def list_persistent_matlab_vars() -> list[str]:
    """
    Return a list of all persistent variables
    """
    return ENG.workspace["persistent_vars"]

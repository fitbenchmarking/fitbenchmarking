import matlab.engine

ENG = matlab.engine.start_matlab()


def add_persistent_matlab_var(name):
    """
    Manage a list of variables to keep when clearing memory.

    :param name: The variable to add to the persistent list
    :type name: str
    """
    ENG.evalc(
        r'if not(exist("persistent_vars"));'
        r' persistent_vars = {"persistent_vars"};'
        r'end;'
    )
    ENG.evalc(
        f'if not(any(cellfun(@(x) x=="{name}", persistent_vars)));'
        f' persistent_vars{{end+1}} = "{name}";'
        r'end;'
    )


def clear_non_persistent_matlab_vars():
    """
    Clear any non-persistent variables.
    That is any varible that hasn't been added via the above method.
    """
    ENG.clearvars('-except', r'persistent_vars{:}', nargout=0)

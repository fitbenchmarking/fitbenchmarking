from abc import ABCMeta, abstractmethod


class Jacobian:
    """
    Jacobian base class
    """
    __metaclass__ = ABCMeta

    def __init__(self, problem):
        self.problem = problem

    @abstractmethod
    def eval(self):
        pass

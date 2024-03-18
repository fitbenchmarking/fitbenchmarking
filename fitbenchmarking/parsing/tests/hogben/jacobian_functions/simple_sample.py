from numpy import exp
from scipy import sparse


def simple_sample_dense_jac(x, params):

    p1 = params[0]
    p2 = params[1]
    J = [p1*p2*exp(-p2*x)]
    return J


def simple_sample_sparse_jac(x, params):

    p1 = params[0]
    p2 = params[1]
    J = [p1*p2*exp(-p2*x)]
    return sparse.csr_matrix(J)

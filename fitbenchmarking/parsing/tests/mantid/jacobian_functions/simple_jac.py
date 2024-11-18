from scipy import sparse


def simple_sparse_jac(x, params):
    """Sparse jac function."""

    p1 = params[0]
    p2 = params[1]
    J = [20 * x * p1 + 10 * p2, 20 * p1 + 10 * x * p2]
    return sparse.csr_matrix(J)

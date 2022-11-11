#include "mex.h"
#include "matrix.h"

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {
    // nlhs: num of lhs args
    // plhs: pointers to lhs args
    // nrhs and prhs are similar

    // Function wrapper for fitbenchmarking costfunction evaluation.
    // Call with:
    //     result = evalfunction(f, p)
    //
    // Args:
    //     f (function): The function to evaluate, signature -- [result] = f(params)
    //     p (array): The values to evaluate at
    // Returns:
    //     result (double): The cost at the values
    
    double (*fun)(double*, double*);
    fun = (double (*)(double*, double*)) *((mwSize*) mxGetData(prhs[0]));
    double *in;
    double out;
    in = mxGetDoubles(prhs[1]);
    int res = fun(in, &out);
    plhs[0] = mxCreateDoubleScalar(out);
}

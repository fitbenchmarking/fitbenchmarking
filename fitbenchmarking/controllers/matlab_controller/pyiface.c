#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "matrix.h"
#include "libmatlabcontroller.h"
#include <stdbool.h>

// ========== CALLBACK ===========
static PyObject *py_eval_cost = NULL;
static int nparams = 0;

static int c_eval_cost(
    double *params, // list of nparams doubles
    double *out     // output reference
)
{
    // Run the python function with params
    PyObject *arglist; // Container for passing params to python
    PyObject *result;  // Container for result of callback

    // Convert *double to python list
    arglist = PyList_New(nparams);
    for (int i = 0; i < nparams; i++)
        PyList_SetItem(arglist, i, Py_BuildValue("d", params[i]));

    result = PyObject_CallFunctionObjArgs(py_eval_cost, arglist, NULL);
    if (result == NULL)
        return -1;

    *out = PyFloat_AsDouble(result);

    Py_DecRef(arglist);
    Py_DecRef(result);

    return 0;
}

// ===============================

// ====== MATLAB INTERFACE =======
int matlab_fminsearch(
    double *x,    // The optimal values
    double *fval, // The optimal cost
    int *flag,    // The status
    double *x0    // The initial values
)
{
    // Convert values to Matlab arrays and call the Matlab fitting routine.

    mxArray *of;      // Matlab array for function pointer
    mxArray *x0arr;   // Matlab array for starting values
    mxArray *xarr;    // Matlab array for output x
    mxArray *fvalarr; // Matlab array for output fval
    mxArray *flagarr; // Matlab array for output flag

    double *tmp; // Variable to aid converting from xArray

    // Create a numeric datatype large enough to hold a pointer
    of = mxCreateNumericMatrix(1, 1, mxUINT64_CLASS, mxREAL);
    // Save the pointer to the objective function as numeric
    *((mwSize *)mxGetData(of)) = (mwSize)c_eval_cost;

    // The starting point
    x0arr = mxCreateDoubleMatrix(nparams, 1, mxREAL);
    tmp = mxGetDoubles(x0arr);
    for (int i = 0; i < nparams; i++)
        tmp[i] = x0[i];

    // Call matlab
    xarr = NULL;
    fvalarr = NULL;
    flagarr = NULL;
    mlfMin_wrapper(3, &xarr, &fvalarr, &flagarr, of, x0arr);

    // Unpack the results
    tmp = mxGetDoubles(xarr);
    for (int i = 0; i < nparams; i++)
        x[i] = tmp[i];

    *fval = *mxGetDoubles(fvalarr);
    *flag = *mxGetInt32s(flagarr);

    // Clean up
    mxDestroyArray(of);
    mxDestroyArray(x0arr);
    mxDestroyArray(xarr);
    mxDestroyArray(fvalarr);
    mxDestroyArray(flagarr);

    return 0;
}

// ===============================

// == FITBENCHMARKING INTERFACE ==
static bool initialised = false;

PyDoc_STRVAR(
    py_initialise_doc,
    "Initialise the matlab controller and set the function to minimise.\n"
    "Calling this function again will not reinitialise the matlab controller"
    " but will update the function.\n\n"
    ":param eval_cost: The function to minimise.\n"
    ":type eval_cost: Callable\n");
static PyObject *py_initialise(PyObject *self,
                               PyObject *args)
{
    PyObject *eval_cost; // Temp place for new function while testing callable
    int np;              // number of params

    PyArg_ParseTuple(args, "Oi", &eval_cost, &np);
    if (!PyCallable_Check(eval_cost))
    {
        PyErr_SetString(PyExc_TypeError,
                        "eval_cost not callable");
        return NULL;
    }
    Py_IncRef(eval_cost);
    Py_DecRef(py_eval_cost);
    py_eval_cost = eval_cost;
    nparams = np;

    if (!initialised)
    {
        if (!mclInitializeApplication(NULL, 0))
        {
            PyErr_SetString(
                PyExc_RuntimeError,
                "Could not initialize the matlab runtime.");
            return NULL;
        }
        if (!libmatlabcontrollerInitialize())
        {
            PyErr_SetString(
                PyExc_RuntimeError,
                strcat("An error occurred while initializing: \n",
                       mclGetLastErrorMessage()));
            return NULL;
        }
    }

    initialised = true;

    if (PyErr_Occurred()) return NULL;

    Py_IncRef(Py_None);
    return Py_None;
}

PyDoc_STRVAR(
    py_fit_doc,
    "Run the fitting using the matlab controller.\n\n"
    ":param ini_params: The initial values for the parameters to fit.\n"
    ":type ini_params: List[float]\n\n"
    ":return: A status flag and the calculated optimal values.\n"
    ":rtype: List[float]");
static PyObject *py_fit(PyObject *self, PyObject *args)
{
    PyObject *py_ini_params; // Python list of initial params
    double *ini_params;      // C array of initial params

    PyObject *result; // Result to return - Tuple[int, List[float]]]

    int len;   // Length of list

    PyObject *py_fin_params; // Python list of output params
    double *fin_params;      // Resulting optimal parameters
    double *fin_value;       // Resulting optimal cost *unused*
    int *flag;               // Flag from optimiser

    if (!initialised)
    {
        PyErr_SetString(PyExc_RuntimeError,
                        "No function available - please call init(func).");
        return NULL;
    }
    
    PyArg_ParseTuple(args, "O", &py_ini_params);
    len = PyList_Size(py_ini_params);

    ini_params = (double *)malloc(SIZEOF_DOUBLE * len);
    for (int i = 0; i < len; i++)
        ini_params[i] = PyFloat_AsDouble(PyList_GetItem(py_ini_params, i));

    fin_params = malloc(SIZEOF_DOUBLE * nparams);
    fin_value = malloc(SIZEOF_DOUBLE * 1);
    flag = malloc(SIZEOF_INT * 1);
    matlab_fminsearch(fin_params, fin_value, flag, ini_params);

    py_fin_params = PyList_New(len);
    for (int i = 0; i < len; i++)
        PyList_SetItem(py_fin_params, i, Py_BuildValue("d", fin_params[i]));

    result = PyTuple_New(2);
    PyTuple_SetItem(result, 0, py_fin_params);
    PyTuple_SetItem(result, 1, Py_BuildValue("i", *flag));

    free(fin_params);
    free(fin_value);
    free(flag);

    if (PyErr_Occurred()) return NULL;
    
    return result;
}

PyDoc_STRVAR(
    py_finalise_doc,
    "Terminate the Matlab controller and release any memory.\n"
    "Calling this function resets the initialisation state, "
    "calling init() will reinitialise the controller.\n\n");
static PyObject *py_finalise(PyObject *self, PyObject *args)
{
    // Clean up callback
    Py_DecRef(py_eval_cost);
    py_eval_cost = NULL;
    nparams = 0;

    // Clean up initialisation
    //initialised = false;

    //libmatlabcontrollerTerminate();
    //mclTerminateApplication();

    if (PyErr_Occurred()) return NULL;
    
    Py_IncRef(Py_None);
    return Py_None;
}

// ===============================

// = PYTHON CALLING DEFINITIONS ==
PyDoc_STRVAR(
    module_doc,
    "A module to include python callbacks in matlab's fminsearch.");

static PyMethodDef matlab_controller_methods[] = {
    {"init", (PyCFunction)py_initialise, METH_VARARGS, py_initialise_doc},
    {"fit", (PyCFunction)py_fit, METH_VARARGS, py_fit_doc},
    {"cleanup", (PyCFunction)py_finalise, METH_VARARGS, py_finalise_doc},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "matlab_controller_c",
    module_doc,
    -1,
    matlab_controller_methods};

PyMODINIT_FUNC PyInit_matlab_controller_c(void)
{
    return PyModule_Create(&module);
};
// ===============================

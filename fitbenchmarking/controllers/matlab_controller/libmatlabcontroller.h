/*
 * MATLAB Compiler: 8.5 (R2022b)
 * Date: Fri Nov 11 15:23:19 2022
 * Arguments:
 * "-B""macro_default""-W""lib:libmatlabcontroller""-T""link:lib""min_wrapper.m"
 */

#ifndef libmatlabcontroller_h
#define libmatlabcontroller_h 1

#if defined(__cplusplus) && !defined(mclmcrrt_h) && defined(__linux__)
#  pragma implementation "mclmcrrt.h"
#endif
#include "mclmcrrt.h"
#ifdef __cplusplus
extern "C" { // sbcheck:ok:extern_c
#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_libmatlabcontroller_C_API 
#define LIB_libmatlabcontroller_C_API /* No special import/export declaration */
#endif

/* GENERAL LIBRARY FUNCTIONS -- START */

extern LIB_libmatlabcontroller_C_API 
bool MW_CALL_CONV libmatlabcontrollerInitializeWithHandlers(
       mclOutputHandlerFcn error_handler, 
       mclOutputHandlerFcn print_handler);

extern LIB_libmatlabcontroller_C_API 
bool MW_CALL_CONV libmatlabcontrollerInitialize(void);

extern LIB_libmatlabcontroller_C_API 
void MW_CALL_CONV libmatlabcontrollerTerminate(void);

extern LIB_libmatlabcontroller_C_API 
void MW_CALL_CONV libmatlabcontrollerPrintStackTrace(void);

/* GENERAL LIBRARY FUNCTIONS -- END */

/* C INTERFACE -- MLX WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- START */

extern LIB_libmatlabcontroller_C_API 
bool MW_CALL_CONV mlxMin_wrapper(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

/* C INTERFACE -- MLX WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- END */

/* C INTERFACE -- MLF WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- START */

extern LIB_libmatlabcontroller_C_API bool MW_CALL_CONV mlfMin_wrapper(int nargout, mxArray** x, mxArray** fval, mxArray** exitflag, mxArray* fun, mxArray* x0);

#ifdef __cplusplus
}
#endif
/* C INTERFACE -- MLF WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- END */

#endif

/*
 * MATLAB Compiler: 8.5 (R2022b)
 * Date: Fri Nov 11 15:23:19 2022
 * Arguments:
 * "-B""macro_default""-W""lib:libmatlabcontroller""-T""link:lib""min_wrapper.m"
 */

#define EXPORTING_libmatlabcontroller 1
#include "libmatlabcontroller.h"

static HMCRINSTANCE _mcr_inst = NULL; /* don't use nullptr; this may be either C or C++ */

#ifdef __cplusplus
extern "C" { // sbcheck:ok:extern_c
#endif

static int mclDefaultPrintHandler(const char *s)
{
    return mclWrite(1 /* stdout */, s, sizeof(char)*strlen(s));
}

#ifdef __cplusplus
} /* End extern C block */
#endif

#ifdef __cplusplus
extern "C" { // sbcheck:ok:extern_c
#endif

static int mclDefaultErrorHandler(const char *s)
{
    int written = 0;
    size_t len = 0;
    len = strlen(s);
    written = mclWrite(2 /* stderr */, s, sizeof(char)*len);
    if (len > 0 && s[ len-1 ] != '\n')
        written += mclWrite(2 /* stderr */, "\n", sizeof(char));
    return written;
}

#ifdef __cplusplus
} /* End extern C block */
#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_libmatlabcontroller_C_API
#define LIB_libmatlabcontroller_C_API /* No special import/export declaration */
#endif

LIB_libmatlabcontroller_C_API 
bool MW_CALL_CONV libmatlabcontrollerInitializeWithHandlers(
    mclOutputHandlerFcn error_handler,
    mclOutputHandlerFcn print_handler)
{
    int bResult = 0;
    if (_mcr_inst)
        return true;
    if (!mclmcrInitialize())
        return false;
    {
        mclCtfStream ctfStream = 
            mclGetEmbeddedCtfStream((void *)(libmatlabcontrollerInitializeWithHandlers));
        if (ctfStream) {
            bResult = mclInitializeComponentInstanceEmbedded(&_mcr_inst,
                                                             error_handler, 
                                                             print_handler,
                                                             ctfStream);
            mclDestroyStream(ctfStream);
        } else {
            bResult = 0;
        }
    }  
    if (!bResult)
    return false;
    return true;
}

LIB_libmatlabcontroller_C_API 
bool MW_CALL_CONV libmatlabcontrollerInitialize(void)
{
    return libmatlabcontrollerInitializeWithHandlers(mclDefaultErrorHandler, 
                                                   mclDefaultPrintHandler);
}

LIB_libmatlabcontroller_C_API 
void MW_CALL_CONV libmatlabcontrollerTerminate(void)
{
    if (_mcr_inst)
        mclTerminateInstance(&_mcr_inst);
}

LIB_libmatlabcontroller_C_API 
void MW_CALL_CONV libmatlabcontrollerPrintStackTrace(void) 
{
    char** stackTrace;
    int stackDepth = mclGetStackTrace(&stackTrace);
    int i;
    for(i=0; i<stackDepth; i++)
    {
        mclWrite(2 /* stderr */, stackTrace[i], sizeof(char)*strlen(stackTrace[i]));
        mclWrite(2 /* stderr */, "\n", sizeof(char)*strlen("\n"));
    }
    mclFreeStackTrace(&stackTrace, stackDepth);
}


LIB_libmatlabcontroller_C_API 
bool MW_CALL_CONV mlxMin_wrapper(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[])
{
    return mclFeval(_mcr_inst, "min_wrapper", nlhs, plhs, nrhs, prhs);
}

LIB_libmatlabcontroller_C_API 
bool MW_CALL_CONV mlfMin_wrapper(int nargout, mxArray** x, mxArray** fval, mxArray** 
                                 exitflag, mxArray* fun, mxArray* x0)
{
    return mclMlfFeval(_mcr_inst, "min_wrapper", nargout, 3, 2, x, fval, exitflag, fun, x0);
}


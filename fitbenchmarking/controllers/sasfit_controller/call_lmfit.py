import numpy as np
import ctypes as ct
from ctypes import (
    c_int, c_float, c_bool, POINTER, Structure, CFUNCTYPE, byref, pointer, cast
)

# Load library
lib = ct.CDLL("sasfit_LM_rewritten/liblmfit.so") 

# ---- Match your C structs ----

class sasfit_analytpar(Structure):
    _fields_ = []  # C struct is currently empty

class SASFIT_CData(Structure):
    _fields_ = [
        ("alpha", POINTER(POINTER(c_float))),
        ("covar", POINTER(POINTER(c_float))),
        ("oneda", POINTER(POINTER(c_float))),
        ("beta",  POINTER(c_float)),
        ("a",     POINTER(c_float)),
        ("da",    POINTER(c_float)),
        ("atry",  POINTER(c_float)),
        ("lista", POINTER(c_int)),
        ("ma",    c_int),
        ("mfit",  c_int),
        ("max_SD",c_int),
        ("chisq", c_float),
    ]

# ---- Helper to create float** matrices ----
def make_matrix_float(rows, cols):
    """
    Returns (mat_ptr, row_buffers) where:
      - mat_ptr is POINTER(POINTER(c_float)) suitable for passing to C as float** 
      - row_buffers is a list you must KEEP referenced so memory isn't GC'd
    """
    RowArray = (c_float * cols)
    row_buffers = [RowArray() for _ in range(rows)]
    # Build array of row pointers
    MatArray = POINTER(c_float) * rows
    mat = MatArray(*[row_buffers[r] for r in range(rows)])
    return mat, row_buffers

# ---- Function pointer type for 'funcs' ----
# C signature we need to match:
# void funcs(float x_i, float res_i, float a[], float *ymod, float *ysub,
#            float dyda[], int max_SD, sasfit_analytpar *AP,
#            int error_type, int flag, bool *error);
FUNCS_T = CFUNCTYPE(
    None,
    c_float,                  # x_i
    c_float,                  # res_i
    POINTER(c_float),         # a
    POINTER(c_float),         # ymod
    POINTER(c_float),         # ysub
    POINTER(c_float),         # dyda
    c_int,                    # max_SD
    POINTER(sasfit_analytpar),# AP
    c_int,                    # error_type
    c_int,                    # flag
    POINTER(c_bool)           # error
)


# ---- Example model (linear: y = a0 + a1*x) ----
@FUNCS_T
def funcs(x_i, res_i, a, ymod, ysub, dyda, max_SD, AP, error_type, flag, error_ptr):
    # Zero all derivatives to be safe
    # (Assumes ma known; if not, at least zero the ones you will use.)
    # Here we assume ma>=2
    dyda[0] = 0.0
    dyda[1] = 0.0

    y = a[0] + a[1] * x_i

    if not np.isfinite(y):
        print("Non-finite ymod for x:", float(x_i))
        
    ymod[0] = y
    ysub[0] = y
    dyda[0] = 1.0
    dyda[1] = x_i
    error_ptr[0] = False



# ---- Bind the C functions ----
lib.SASFITmrqmin.argtypes = [
    POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float),  # x,y,sig,res
    POINTER(c_float), POINTER(c_float),                                      # yfit, ysubstr
    c_int, c_int,                                                            # ndata, max_SD
    POINTER(sasfit_analytpar), c_int,                                        # AP, error_type
    POINTER(SASFIT_CData),                                                   # SASFIT_CData[]
    POINTER(c_float),                                                        # chisq
    FUNCS_T,                                                                 # funcs
    POINTER(c_float),                                                        # alamda
    POINTER(c_bool)                                                          # error
]
lib.SASFITmrqmin.restype = None

lib.SASFITmrqcof.argtypes = [
    POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float),
    POINTER(c_float), POINTER(c_float), c_int,
    POINTER(c_float), POINTER(c_int), c_int, c_int,
    POINTER(sasfit_analytpar), c_int, c_int,
    POINTER(POINTER(c_float)), POINTER(c_float), POINTER(c_float),
    FUNCS_T, POINTER(c_bool)
]
lib.SASFITmrqcof.restype = None

lib.SASFITgaussj.argtypes = [POINTER(POINTER(c_float)), c_int, POINTER(POINTER(c_float)), c_int, POINTER(c_bool)]
lib.SASFITgaussj.restype = None

lib.SASFITcovsrt.argtypes = [POINTER(POINTER(c_float)), c_int, POINTER(c_int), c_int, POINTER(c_bool)]
lib.SASFITcovsrt.restype = None


########################################################################
# ---- Problem sizes ----
ndata = 50
ma = 2        # number of parameters (for our example: intercept, slope)
mfit = 2      # number of fitted parameters
max_SD = 0    # not used in this minimal example
error_type = 0  # 0: linear errors (yexp=y[i], sigma=sig[i])

# ---- Synthetic data (y = 2 + 0.5*x + noise) ----
rng = np.random.default_rng(42)
x_np   = np.linspace(0, 10, ndata).astype(np.float32)
x_np = np.asarray(x_np, dtype=np.float32, order="C")

true_a = np.array([2.0, 0.5], dtype=np.float32)
y_clean = true_a[0] + true_a[1] * x_np
noise = rng.normal(0, 0.2, size=ndata).astype(np.float32)
y_np   = (y_clean + noise).astype(np.float32)
y_np = np.asarray(y_np, dtype=np.float32, order="C")

# uncertainties and residual channel
sig_np = np.full(ndata, 0.2, dtype=np.float32)
sig_np = np.asarray(sig_np, dtype=np.float32, order="C")
res_np = np.zeros(ndata, dtype=np.float32)

# outputs
yfit_np    = np.zeros(ndata, dtype=np.float32)
ysubstr_np = np.zeros(ndata, dtype=np.float32)

# ---- LM parameter arrays ----
a_arr    = (c_float * ma)(* [1.0, 1.0])  # initial guess
da_arr   = (c_float * ma)()
atry_arr = (c_float * ma)()
beta_arr = (c_float * mfit)()
lista_arr = (c_int * mfit)(*list(range(mfit)))  # fit both parameters

# ---- Matrices: alpha, covar (mfit x mfit), oneda (mfit x 1) ----
alpha_mat, alpha_bufs = make_matrix_float(mfit, mfit)
covar_mat, covar_bufs = make_matrix_float(mfit, mfit)
oneda_mat, oneda_bufs = make_matrix_float(mfit, 1)

# ---- Prepare struct and other scalars ----
AP = sasfit_analytpar()  # empty (ok)
chisq = c_float(0.0)
alamda = c_float(-1.0)   # < 0 triggers initialization path
err = c_bool(False)

cdata = SASFIT_CData(
    alpha_mat, covar_mat, oneda_mat,
    beta_arr,
    a_arr, da_arr, atry_arr,
    lista_arr,
    ma, mfit, max_SD,
    c_float(0.0)
)

cdata_array = (SASFIT_CData * 1)(cdata)

# ---- Convert numpy arrays to float* ----
x_ptr   = x_np.ctypes.data_as(POINTER(c_float))
y_ptr   = y_np.ctypes.data_as(POINTER(c_float))
sig_ptr = sig_np.ctypes.data_as(POINTER(c_float))
res_ptr = res_np.ctypes.data_as(POINTER(c_float))
yfit_ptr    = yfit_np.ctypes.data_as(POINTER(c_float))
ysubstr_ptr = ysubstr_np.ctypes.data_as(POINTER(c_float))



def check_finite(name, arr):
    if not np.all(np.isfinite(arr)):
        bad = np.where(~np.isfinite(arr))[0][:5]
        print(f"{name} has non-finite at indices:", bad)
        return False
    return True

check_finite("x", x_np)
check_finite("y", y_np)
check_finite("sig", sig_np)

# ---- Call SASFITmrqmin ----
lib.SASFITmrqmin(
    x_ptr, y_ptr, sig_ptr, res_ptr,
    yfit_ptr, ysubstr_ptr,
    ndata, max_SD, byref(AP), error_type,
    cdata_array,
    byref(chisq), funcs,
    byref(alamda), byref(err)
)

print("err              :", bool(err.value))
print("final chisq      :", chisq.value)
print("final alamda     :", alamda.value)
print("fitted a[0], a[1]:", a_arr[0], a_arr[1])

#########################################################################
"""
SASStudio functions to load and call SASfit plugins from Python.

Copyright (C) 2026 The Science and Technology Facilities Council (STFC)
Author: Jase Tennyson Taylor (STFC)
"""

import ctypes
from os import environ, path, walk
import platform

SASLIB_PATH = environ["SASFIT_LOCATION"]
PLUGIN_PATH = path.join(SASLIB_PATH, "plugins")

MAXPAR = 50  # from sasfit_constants.h

# "param" structure from sasfit_function.h
class sasfit_plugin_parameters_types(ctypes.Structure):
    _fields_ = [  # comments below are directly copied fom sasfit_function.h...
        ("p", ctypes.c_double * MAXPAR),  # Parameter of a function.
        (
            "kernelSelector",
            ctypes.c_int,
        ),  # Selects the kernel function to use, when used with gsl functions.
        ("kernelSubSelector", ctypes.c_int),  # ??
        ("errStr", ctypes.c_wchar_p),  # An error message.
        ("errLen", ctypes.c_int),  # Length of the error message.
        (
            "errStatus",
            ctypes.c_bool,
        ),  # True, if an error occured. False otherwise.
        ("xarr", ctypes.c_double),  # hack for OZ solver "double *xarr"
        ("yarr", ctypes.c_double),  # hack for OZ solver "double *yarr"
        ("moreparam", ctypes.c_void_p),  #
        ("more_p", ctypes.c_double * MAXPAR),  # more Parameter of a function.
        (
            "function",
            ctypes.CFUNCTYPE(
                ctypes.c_double, ctypes.c_double, ctypes.c_void_p
            ),
        ),  # "double (*function)(double, void *)"
    ]


# plugin function and stubs ctypes templates
FunctionType2 = ctypes.CFUNCTYPE(
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(sasfit_plugin_parameters_types),
)
SASFIT_FUNC_ONE_T = ctypes.CFUNCTYPE(
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(sasfit_plugin_parameters_types),
)
SASFIT_FUNC_VOL_T = ctypes.CFUNCTYPE(
    ctypes.c_double,
    ctypes.c_double,
    ctypes.POINTER(sasfit_plugin_parameters_types),
    ctypes.c_int,
)


class SASFIT_PLUGIN_FUNC_T(ctypes.Structure):
    _fields_ = [
        ("len", ctypes.c_int),
        ("name", ctypes.c_char_p),
        ("func", ctypes.POINTER(SASFIT_FUNC_ONE_T)),
        ("func_f", ctypes.POINTER(SASFIT_FUNC_ONE_T)),
        ("func_v", ctypes.POINTER(SASFIT_FUNC_VOL_T)),
    ]


class SASFIT_PLUGIN_INFO_T(ctypes.Structure):
    _fields_ = [
        ("num", ctypes.c_int),
        ("functions", ctypes.POINTER(SASFIT_PLUGIN_FUNC_T)),
    ]


class SASFIT_COMMON_STUBS_T(ctypes.Structure):
    _fields_ = [
        ("func", ctypes.c_void_p * 155),
    ]


class Plugin:
    def __init__(self, requested_plugin_name, parameter_values=[]):
        # must match order as defined in C header!
        self.parameter_values = parameter_values
        # to be populated once plugin is found & loaded,
        # and the C header parsed
        self.parameter_labels = []
        # to be populated once plugin is found & loaded,
        # and the C header parsed
        self.parameter_descriptions = {}

        self.function_signatures = {}

        requested_function_name = None

        (base, extension) = path.splitext(requested_plugin_name)
        # search for a C .so, .dll, or .dylib filename
        if (extension in [".so", ".dll",".dylib"]) and path.exists(
            path.join(PLUGIN_PATH, f"libsasfit_{requested_plugin_name}")
        ):
            self.plugin_file_path = path.join(
                PLUGIN_PATH, f"libsasfit_{requested_plugin_name}"
            )
            print(
                f"...plugin file libsasfit_{requested_plugin_name}"
                 " found; loading..."
            )
            plugin_language = "c"
        elif extension == "":
            if platform.system() == "Windows":
                extension = ".dll"
            elif platform.system() == "Linux":
                extension = ".so"
            elif platform.system() == "Darwin":
                extension = ".dylib"
        
            if path.exists(
                path.join(PLUGIN_PATH, f"libsasfit_{requested_plugin_name}{extension}")
            ):
                self.plugin_file_path = path.join(
                    PLUGIN_PATH, f"libsasfit_{requested_plugin_name}{extension}"
                )
                print(
                    f"...plugin file libsasfit_{requested_plugin_name}{extension}"
                     " found; loading..."
                )
                plugin_language = "c"
            # search through all C headers in case this plugin has been
            # implemented alongside lots of others inside a different
            # single dll, e.g. with azimuthal.dll
            else:
                self.plugin_file_path = ""
                for paths, folders, files in walk(PLUGIN_PATH):
                    for each_filename in files:
                        if each_filename.endswith(".h"):
                            with open(
                                path.join(PLUGIN_PATH, each_filename)
                            ) as open_file:
                                plugin_functions_list = open_file.read().split(
                                    "* \defgroup "
                                )
                                for (
                                    each_plugin_function
                                ) in plugin_functions_list:
                                    if not each_plugin_function.startswith(
                                        "/*"
                                    ):
                                        x = each_plugin_function.split(
                                            "* \ingroup "
                                        )[0]
                                        each_function_name = x.split(" ")[0]
                                        each_plugin_name = x.split(
                                            each_function_name
                                        )[1].strip()
                                        if (
                                            each_plugin_name
                                            == requested_plugin_name
                                        ):
                                            self.plugin_file_path = path.join(
                                                PLUGIN_PATH,
                                                f"lib{each_filename.split('.')[0]}{extension}",
                                            )
                                            requested_function_name = (
                                                requested_plugin_name
                                            )
                                            requested_plugin_name = (
                                                each_filename.split(".")[
                                                    0
                                                ].removeprefix("sasfit_")
                                            )
                if self.plugin_file_path == "":
                    print(f"...plugin {requested_plugin_name} NOT FOUND!")
                    plugin_language = ""
                else:
                    print(f"...plugin {requested_plugin_name} found in"
                          f" {self.plugin_file_path}; loading..."
                    )
                    plugin_language = "c"

        if plugin_language == "c":
            # import dll
            if path.exists(self.plugin_file_path):
                imported_library_object = ctypes.CDLL(self.plugin_file_path)
            else:
                print(f"...plugin file {self.plugin_file_path} NOT FOUND!")

            # parse corresponding C header to get function name(s) & parameters
            self.plugin_header_path = path.join(
                PLUGIN_PATH, f"sasfit_{requested_plugin_name}.h"
            )

            with open(self.plugin_header_path) as header_file_handle:
                try:
                    if requested_function_name:
                        for f in header_file_handle.read().split(
                            "/* ################ start "
                        ):
                            if requested_function_name in f:
                                text_info_section = f
                                break
                    else:
                        text_info_section = header_file_handle.read().split(
                            "/* ################ start "
                        )[1]
                    self.function_name = (
                        "sasfit_"
                        + text_info_section.split(" ################ */")[0]
                    )
                    parameters_list_raw = (
                        text_info_section.split("* \par Required parameters:")[
                            1
                        ]
                        .split(" */")[0]
                        .split("<tr>")[1:]
                    )
                    for each_parameter_pair_raw in parameters_list_raw:
                        parameter_name_raw = each_parameter_pair_raw.split(
                            "<td>\\b "
                        )[1].split("</td>")[0]
                        parameter_description_raw = (
                            each_parameter_pair_raw.split("<td>")[2].split(
                                "</td>"
                            )[0]
                        )
                        self.parameter_descriptions[parameter_name_raw] = (
                            parameter_description_raw
                        )
                except:
                    print(f"...C header {self.plugin_header_path} NOT FOUND!")

            exec(
                "self.function_signatures['scattering intensity'] ="
                f" imported_library_object.{self.function_name}"
            )
            self.function_signatures["scattering intensity"].argtypes = [
                ctypes.c_double,
                ctypes.POINTER(sasfit_plugin_parameters_types),
            ]
            self.function_signatures[
                "scattering intensity"
            ].restype = ctypes.c_double

            exec(
                "self.function_signatures['scattering amplitude'] ="
                f" imported_library_object.{self.function_name}_f"
            )
            self.function_signatures["scattering amplitude"].argtypes = [
                ctypes.c_double,
                ctypes.POINTER(sasfit_plugin_parameters_types),
            ]
            self.function_signatures[
                "scattering amplitude"
            ].restype = ctypes.c_double

            exec(
                "self.function_signatures['volume'] ="
                f" imported_library_object.{self.function_name}_v"
            )
            self.function_signatures["volume"].argtypes = [
                ctypes.c_double,
                ctypes.POINTER(sasfit_plugin_parameters_types),
                ctypes.c_int,
            ]
            self.function_signatures["volume"].restype = ctypes.c_double

class Scattering_Contribution:
    def __init__(self, label=""):
        self.label = label
        self.form_factor_plugin_name = "None"

    def set_form_factor_parameters(self, param_array_values):
        param_array = (ctypes.c_double * MAXPAR)(*param_array_values)
        sasfit_param_instance = sasfit_plugin_parameters_types()
        sasfit_param_instance.p = param_array
        self.form_factor_params = ctypes.cast(
            ctypes.pointer(sasfit_param_instance),
            ctypes.POINTER(sasfit_plugin_parameters_types),
        )

    def load_form_factor(self, plugin_name):
        self.form_factor_plugin_name = plugin_name
        form_factor_plugin = Plugin(plugin_name)

        self.form_factor_scattering_intensity = (
            form_factor_plugin.function_signatures["scattering intensity"]
        )
        self.form_factor_scattering_amplitude = (
            form_factor_plugin.function_signatures["scattering amplitude"]
        )
        self.form_factor_volume = form_factor_plugin.function_signatures[
            "volume"
        ]

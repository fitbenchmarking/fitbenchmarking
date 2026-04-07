import ctypes
from os import environ, path, walk

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

        # TODO:
        # Search through all DLLs and python files for a matching plugin name
        # - some DLLs contain multiple (related) plugins in one file, hence 
        #   the need to search through all DLLs
        # - python plugins should be 1-plugin-per-file, with filename
        #   matching the plugin name

        requested_function_name = None

        (base, extension) = path.splitext(requested_plugin_name)
        # search for a C .dll filename
        if (extension == ".so") and path.exists(
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
        # search for a python .py filename
        elif (extension == ".py") and path.exists(
            path.join(PLUGIN_PATH, f"libsasfit_{requested_plugin_name}")
        ):
            print(
                f"...plugin file saslib_{requested_plugin_name}"
                 " found; loading..."
            )
            plugin_language = "python"
        elif extension == "":
            # search for a C .dll filename
            if path.exists(
                path.join(PLUGIN_PATH, f"libsasfit_{requested_plugin_name}.so")
            ):
                self.plugin_file_path = path.join(
                    PLUGIN_PATH, f"libsasfit_{requested_plugin_name}.so"
                )
                print(
                    f"...plugin file libsasfit_{requested_plugin_name}.so"
                     " found; loading..."
                )
                plugin_language = "c"
            # search for a python .py filename
            elif path.exists(
                path.join(PLUGIN_PATH, f"saslib_{requested_plugin_name}.py")
            ):
                print(
                    f"...plugin file saslib_{requested_plugin_name}.py"
                     " found; loading..."
                )
                plugin_language = "python"
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
                                                f"lib{each_filename.split('.')[0]}.so",
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
                imported_library_object = safely_load_dll(
                    self.plugin_file_path
                )  # ctypes.CDLL(self.plugin_file_path)
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

        elif plugin_language == "python":
            command_string = f"""from plugins.saslib_{requested_plugin_name} import scattering_intensity
            from plugins.saslib_{requested_plugin_name} import scattering_amplitude
            from plugins.saslib_{requested_plugin_name} import volume"""
            exec(command_string, globals())
            self.function_signatures["scattering intensity"] = (
                scattering_intensity
            )
            self.function_signatures["scattering amplitude"] = (
                scattering_amplitude
            )
            self.function_signatures["volume"] = volume

    #     def set_parameters(self, param_array_values):
    #         #param_array_values = [10.0, 0.5, 1.0, 1e-4]
    #         param_array = (ctypes.c_double * MAXPAR)(*param_array_values)
    #         sasfit_param_instance = sasfit_plugin_parameters_types()
    #         sasfit_param_instance.p = param_array
    #         params_ptr = ctypes.cast(ctypes.pointer(sasfit_param_instance),
    #                       ctypes.POINTER(sasfit_parameters_types))
    #
    #     def set_single_parameter(self, parameter_name, parameter_value):
    #         pass
    #
    #     def load_parameters_from_file(self, filename):
    #         pass

    def __str__(self):  # invoked by print()
        return ""
        return str(self.function_signatures, "\n", self.parameters_description)


class Scattering_Contribution:
    def __init__(self, label="", structure_factor_approach="monodisperse"):
        self.label = label
        self.structure_factor_plugin_name = "None"
        self.form_factor_plugin_name = "None"
        self.size_distribution_plugin_name = "None"
        self.structure_factor_approach = structure_factor_approach

    def set_structure_factor_parameters(self, param_array_values):
        param_array = (ctypes.c_double * MAXPAR)(*param_array_values)
        sasfit_param_instance = sasfit_plugin_parameters_types()
        sasfit_param_instance.p = param_array
        self.form_factor_params = ctypes.cast(
            ctypes.pointer(sasfit_param_instance),
            ctypes.POINTER(sasfit_plugin_parameters_types),
        )

    def load_structure_factor(self, plugin_name):
        print(f"Loading structure factor: {plugin_name}...")
        self.structure_factor_plugin_name = plugin_name
        structure_factor_plugin = Plugin(plugin_name)
        # TODO parse header and assign default param values now
        default_param_values = []
        self.set_structure_factor_parameters(default_param_values)
        self.structure_factor_scattering_intensity = (
            structure_factor_plugin.function_signatures["scattering intensity"]
        )

    def set_form_factor_parameters(self, param_array_values):
        param_array = (ctypes.c_double * MAXPAR)(*param_array_values)
        sasfit_param_instance = sasfit_plugin_parameters_types()
        sasfit_param_instance.p = param_array
        self.form_factor_params = ctypes.cast(
            ctypes.pointer(sasfit_param_instance),
            ctypes.POINTER(sasfit_plugin_parameters_types),
        )

    def load_form_factor(self, plugin_name):
        # print(f"Loading form factor: {plugin_name}...")
        self.form_factor_plugin_name = plugin_name
        form_factor_plugin = Plugin(plugin_name)
        # TODO parse header and assign default param values now
        default_param_values = []
        self.set_form_factor_parameters(default_param_values)
        self.form_factor_scattering_intensity = (
            form_factor_plugin.function_signatures["scattering intensity"]
        )
        self.form_factor_scattering_amplitude = (
            form_factor_plugin.function_signatures["scattering amplitude"]
        )
        self.form_factor_volume = form_factor_plugin.function_signatures[
            "volume"
        ]

    def set_size_distribution_parameters(self, param_array_values):
        param_array = (ctypes.c_double * MAXPAR)(*param_array_values)
        sasfit_param_instance = sasfit_plugin_parameters_types()
        sasfit_param_instance.p = param_array
        self.form_factor_params = ctypes.cast(
            ctypes.pointer(sasfit_param_instance),
            ctypes.POINTER(sasfit_plugin_parameters_types),
        )

    def load_size_distribution(self, plugin_name):
        print(f"Loading size distributions: {plugin_name}...")
        self.size_distribution_plugin_name = plugin_name
        size_distribution_plugin = Plugin(plugin_name)
        # TODO parse header and assign default param values now
        default_param_values = []
        self.set_size_distribution_parameters(default_param_values)
        self.size_distribution_scattering_intensity = (
            size_distribution_plugin.function_signatures[
                "scattering intensity"
            ]
        )

    def set_structure_factor_approach(self, structure_factor_approach):
        if structure_factor_approach in {"monodisperse"}:
            self.structure_factor_approach = structure_factor_approach
        else:
            print(
                f"'{structure_factor_approach}' is an unrecognised approach for"
                 " including structure factors; defaulting to 'monodisperse'."
            )
            self.structure_factor_approach = "monodisperse"

    def construct_scattering_contribution_function(self):
        match self.structure_factor_approach:
            case "monodisperse":  # sasfit manual 4.1.1
                self.scattering_contribution_function = (
                    self.run_integrator(
                        0,
                        inf,
                        self.size_distribution_scattering_intensity
                        * self.form_factor_scattering_intensity,
                        params,
                    )
                    * self.structure_factor_scattering_intensity
                )
            case "decoupling approximation":  # sasfit manual 4.1.2
                self.scattering_contribution_function = self.run_integrator(
                    0,
                    inf,
                    (
                        self.size_distribution_scattering_intensity
                        * self.form_factor_scattering_intensity
                    )
                    + (
                        (
                            compute_integral[0, inf](
                                self.size_distribution_scattering_intensity
                                * self.form_factor_scattering_amplitude
                            )
                        )
                        ** 2
                        * (self.structure_factor_scattering_intensity - 1)
                        / integrate[0, inf](
                            self.size_distribution_scattering_intensity
                        )
                    ),
                    params,
                )  # crikey!
            case "local monodisperse approximation":  # sasfit manual 4.1.3
                self.scattering_contribution_function = self.run_integrator(
                    0,
                    inf,
                    (
                        self.size_distribution_scattering_intensity
                        * self.form_factor_scattering_intensity
                        * self.structure_factor_scattering_intensity
                    ),
                    params,
                )
            case "partial structure factors":  # sasfit manual 4.1.3
                self.scattering_contribution_function = self.run_integrator(
                    0,
                    inf,
                    (
                        self.size_distribution_scattering_intensity
                        * self.form_factor_scattering_intensity
                        * self.structure_factor_scattering_intensity
                    ),
                    params,
                )
            case _:  # otherwise
                print(
                    f"'{self.structure_factor_approach}' is an unrecognised approach"
                     " for including structure factors; try e.g. 'monodisperse'."
                )
                self.scattering_contribution = 0.0

    def compute_form_factor(self, q):
        return self.form_factor_scattering_intensity(
            q, self.form_factor_params
        )

    def __str__(self):
        if self.structure_factor_plugin_name == "None":
            status_string = "Structure factor: none\n"
        else:
            status_string = (
                f"Structure factor: {self.structure_factor_plugin_name}\n"
            )
            status_string = (
                status_string
                + f"Inclusion approach: {self.structure_factor_approach}\n"
            )

        if self.form_factor_plugin_name == "None":
            status_string = status_string + "Form factor: none\n"
        else:
            status_string = (
                status_string
                + f"Form factor: {self.form_factor_plugin_name}\n"
            )

        if self.size_distribution_plugin_name == "None":
            status_string = status_string + "Size distribution: none\n"
        else:
            status_string = (
                status_string
                + f"Size distribution: {self.size_distribution_plugin_name}\n"
            )

        return status_string


def safely_load_dll(dll_path):
    # # list dlls depended upon
    # dependency_list = pefile.PE(dll_path).DIRECTORY_ENTRY_IMPORT
    # # list dlls already in memory
    # dlls_in_memory = psutil.Process( getpid() ).memory_maps()

    # # for each dependency...
    # for each_dependency in dependency_list:
    #     # get its name as a string
    #     this_dependency_name = each_dependency.dll.decode()
    #     # presume it's not loaded yet
    #     this_dependency_loaded = False
    #     # for each dll already loaded...
    #     for each_dll_in_memory in dlls_in_memory:
    #         # get its name as a string
    #         this_dll_in_memory_name = path.basename(each_dll_in_memory.path)
    #         # compare this dependency with each dll already in memory
    #         if this_dependency_name == this_dll_in_memory_name:
    #             # found it!
    #             this_dependency_loaded = True
    #             # so stop searching for it
    #             break
    #     # ...if not, recursively load the missing dependency
    #     if this_dependency_loaded == False:
    #         sasfit_library_path = path.join(SASLIB_PATH, this_dependency_name)
    #         plugin_library_path = path.join(PLUGIN_PATH, this_dependency_name)
    #         # try looking in sasfitlib root folder first
    #         if path.exists(sasfit_library_path):
    #             this_dependency_handle = safely_load_dll(sasfit_library_path)
    #         # next try looking in plugins folder
    #         elif path.exists(plugin_library_path):
    #             this_dependency_handle = safely_load_dll(plugin_library_path)

    # reaching this point means any & all dependencies are already loaded into memory, so go ahead and load this
    dll_handle = ctypes.CDLL(dll_path)
    return dll_handle

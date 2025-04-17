/**
* Uses jQuery to find a collection of DOM elements with text equal to the provided search text.
* @param   {String} class_name    The name of a html element class to find.
* @param   {String} search_text   The text to search for.
* @return  {jQuery Object}        A collection of DOM elements which matched the jQuery search.
*/
function _find_element_from_text(class_name, search_text) {
    return $(class_name).filter(function () { return $(this).text() == search_text; });
}

/**
* Adjusts the span of a column header that encompasses a number of sub-headers.
* @param   {jQuery Object} header   A collection of DOM elements representing column headers with a span.
* @param   {bool} increment         True if the column span should be incremented. Otherwise it is decremented.
*/
function _adjust_colspan(header, increment) {
    var colspan = parseInt(header.attr('colspan'));
    if (isNaN(colspan)) {
        var new_colspan = increment ? 1 : 0;
    } else {
        var new_colspan = increment ? colspan + 1 : colspan - 1;
        header.attr('colspan', new_colspan);
    }

    // Hide the header if the sub-headers are all hidden
    if (new_colspan == 0) {
        header.hide();
    } else {
        header.show();
    }
}

/**
* Shows or hides the table row containing a specific problem.
* @param   {String} problem_name   The name of the problem as it appears in the table row header.
*/
function toggle_problem(problem_name) {
    var span_object = _find_element_from_text("a.problem_header", problem_name);
    span_object.parent().parent().toggle();
}

/**
* Shows or hides the table column containing a specific minimizer.
* @param   {String} software   The name of the software corresponding to the minimizer.
* @param   {String} minimizer  The name of the minimizer as it appears in the table column header.
* @param   {Boolean} independent_call  Determines if the function is called independently or from toggle_softwares.
*/
function toggle_minimizer(software, minimizer) {
    var software_header = _find_element_from_text("a.software_header", software).parent();
    var minimizer_text = _find_element_from_text("a.minimizer_header", minimizer);
    var minimizer_header = minimizer_text.parent();

    // Get the checkbox status
    var is_checked = $(`input[type="checkbox"][value="${minimizer}"]`).is(':checked');

    // calls helper function if the minimizer is 
    // toggled from the minimizer dropdown menu. 
    _handle_disabling_software_checkbox(software)

    // Toggle the minimizer header based on is_checked
    if (is_checked) {
        minimizer_header.show();
    } else {
        minimizer_header.hide();
    }

    const cost_func_names = _get_cost_func_names();
    cost_func_names.forEach(function(cost_func){
        // Get the data cell ids for a given cost function 
        const [_, cols] = _get_all_data_cell_ids(cost_func)
        var width = _get_cost_func_header_span(cost_func);

        // Adjust the column width of the cost function header
        var cost_function_header = $('th a.cost_function_header').filter(function () {
            return $(this).text().trim().toLowerCase() === cost_func;
        }).parent();
        cost_function_header.attr('colspan', width);

        // Adjust the column width of the software
        const software_names = _get_software_names();
        software_names.forEach(function(name){
            const header = $('th a.software_header').filter(function () {
                const name_check = $(this).text().trim() === name;
                const thId = $(this).parent().attr('id');
                const colMatch = thId.match(/col\d+$/);
                const col = colMatch ? colMatch[0] : null;
                return name_check && cols.includes(col);
            }).parent();
            var width = _get_software_header_span(cost_func, name);
            if (width == 0) {
                header.hide();
            } else {
                header.attr('colspan', width);
            }
        })
    })

    // Toggle the data cells in a column
    var table_id = software_header.parent().parent().parent().attr("id");

    minimizer_text.each(function () {
        var column_num = parseInt($(this).attr('col')) + 3;
        // Toggle the table cells based on is_checked
        if (is_checked) {
            $("#" + table_id + " tr > td:nth-child(" + column_num + ")").show();
        } else {
            $("#" + table_id + " tr > td:nth-child(" + column_num + ")").hide();
        }
    });
}

/**
* Helper function that extracts the names of the minimizers for the software.
* @param   {String} software   The name of the software.
*/
function _get_minimizer_names(software){
    const minimizer_names = [];
    $(`a.minimizer_header[data-software="${software}"]`).each(function () {
        minimizer_names.push($(this).text().trim());
    });
    // Returns the unique minimizer names
    return [...new Set(minimizer_names)];
}

/**
 * Returns the span of the cost function header.
 * @param {String} cost_func - The name of the cost function.
 */
function _get_cost_func_header_span(cost_func) {
    const [_, cols] = _get_all_data_cell_ids(cost_func)
    var width = 0;
    cols.forEach(function(col) {
        const th = $(`#T_table_level2_${col}`);
        if (th.is(':visible')){
            width += 1
        }
    })
    return width;
}

/**
 * Returns the span of the cost function header.
 * @param {String} cost_func - The name of the cost function.
 */
function _get_software_header_span(cost_func, software) {
    const [_, cols] = _get_all_data_cell_ids(cost_func)
    // Select the minimizer headers
    const updated_cols = []
    cols.forEach(function(col) {
        const th = $(`#T_table_level2_${col}`);
        const link = th.find('a.minimizer_header');
        if (link.data('software') === software) {
            updated_cols.push(col)
        }
    });
    var width = 0;
    updated_cols.forEach(function(col) {
        const th = $(`#T_table_level2_${col}`);
        if (th.is(':visible')){
            width += 1
        }
    })
    return width;
}

/**
* Helper function that extracts the names of the cost function used while benchmarking.
*/
function _get_cost_func_names(){
    var costfunc_names = []
    var cost_function_headers = $('th a.cost_function_header')
    cost_function_headers.each(function () {
        costfunc_names.push($(this).text().trim().toLowerCase());
    });
    return costfunc_names
}

/**
* Helper function that extracts the names of the software used while benchmarking.
*/
function _get_software_names(){
    var software_names = []
    var software_headers = $('th a.software_header')
    software_headers.each(function () {
        software_names.push($(this).text().trim());
    });
    return [...new Set(software_names)]
}

/**
* Handles the case when a minimizer is toggled directly from the
* minimizer dropdown, rather than through the software dropdown.
* @param {String} software - The name of the software.
*/
function _handle_disabling_software_checkbox(software){
    var software_checkboxes = $(`input[type="checkbox"][value="${software}"]`);
    var software_has_single_minimizer = false;
    
    // Get all the unique minimizers names for a software
    const minimizer_names = _get_minimizer_names(software);

    if (minimizer_names.length === 1){
        software_has_single_minimizer = true;
    } 

    // Get the checked status and push them on to the all_checked list
    var checked = [];
    minimizer_names.forEach(function (name) {
        checked.push($(`input[type="checkbox"][value="${name}"]`).is(':checked'));
    });
    // Verify if all minimizers are checked
    const all_checked = checked.every(check => check === true);
    const all_not_checked = checked.every(check => check === false);
    
    // Set the checkboxes
    if (all_checked){
        software_checkboxes.prop('disabled', false);
        software_checkboxes.prop('checked', true);
    } else {
        software_checkboxes.prop('checked', false);
        // Enable/Disable checkboxes in the software dropdown menu
        if (!software_has_single_minimizer){
            if (all_not_checked) {
                software_checkboxes.prop('disabled', false)
            } else {
                software_checkboxes.prop('disabled', true);
            }
        }
    }
}

/**
* Handles the case when a software is hidden or selected from the
* software dropdown menu.
* @param   {String} software   The name of the software.
*/
function toggle_software(software) {
    const is_checked = $(`input[type="checkbox"][value="${software}"]`).is(':checked');
    
    // Retrive cost functions used while benchmarking
    const cost_func_names = _get_cost_func_names();

    // Process each cost function
    cost_func_names.forEach(function (cost_func) {

        var cost_function_header = $('th a.cost_function_header').filter(function () {
            return $(this).text().trim().toLowerCase() === cost_func;
        }).parent();
        const cost_function_is_checked = $(`input[type="checkbox"][value="${cost_func}"]`).is(':checked');

        if (cost_function_is_checked){

            // Get the data cell ids for a given cost function 
            const [matching_ids, cols] = _get_all_data_cell_ids(cost_func)

            // Select the minimizer headers
            const minimizer_headers = [];
            const updated_cols = []
            cols.forEach(function(col) {
                const th = $(`#T_table_level2_${col}`);
                const link = th.find('a.minimizer_header');
                if (link.data('software') === software) {
                    minimizer_headers.push(th.attr('id'));
                    updated_cols.push(col)
                }
            });

            // Hide/Show the minimizer headers
            minimizer_headers.forEach(function (header) {
                if (is_checked){
                    $('#' + header).show();
                } else {
                    $('#' + header).hide();
                }
            });

            // Select the software headers
            const software_headers = [];
            updated_cols.forEach(function(col) {
                const th = $(`#T_table_level1_${col}`);
                const link = th.find('a.software_header');
                const text = link.text().trim();
                if (text === software) {
                    software_headers.push(th.attr('id'));
                }
            });

            // Hide/Show the software headers
            software_headers.forEach(function (header) {
                if (is_checked){
                    $('#' + header).show();
                } else {
                    $('#' + header).hide();
                }
            });

            // Hide the data cells
            const filtered_ids = matching_ids.filter(id => {
                return updated_cols.some(col => id.endsWith(col));
            });
            filtered_ids.forEach(function (id) {
                if (is_checked){
                    $('#' + id).show();
                } else {
                    $('#' + id).hide();
                }
            });

            // Adjust the column width of the cost function cell
            var width = _get_cost_func_header_span(cost_func);
            cost_function_header.attr('colspan', width);
            
        }         
    });

    // Get all the minimizers names for a software
    const minimizer_names = _get_minimizer_names(software);
    minimizer_names.forEach(function (minimizer) {
        // Set the minimizer checkboxes
        var minimizer_checkboxes = $(`input[type="checkbox"][value="${minimizer}"]`)
        if (is_checked) {
            minimizer_checkboxes.prop('checked', true);
        } else {
            minimizer_checkboxes.prop('checked', false);
        }
    });
}

/**
* Handles the case when a cost function is hidden or selected from the
* cost function dropdown menu.
* @param   {String} cost_func   The name of the cost function.
*/
function _get_all_data_cell_ids(cost_func) {
    // Get the matching cell ids and the column numbers
    const matching_ids = [];
    const cols = [];
    $('td').each(function () {
        const anchor = $(this).find(`a[href*="_${cost_func}"]`);
        if (anchor.length > 0) {
            var id = $(this).attr('id');
            matching_ids.push(id);
            const match = id.match(/col\d+/);
            const col_id = match ? match[0] : null;
            cols.push(col_id)  
        }
    });
    return [matching_ids, [...new Set(cols)]]
}

/**
* Handles the case when a cost function is hidden or selected from the
* cost function dropdown menu.
* @param   {String} cost_func   The name of the cost function.
* @param   {String} minimizer   The name of the minimizer.
* @param   {String} software    The name of the software.
*/
function _get_minimizer_data_cell_ids(cost_func, minimizer, software) {
    if (minimizer.includes(':')) {
        // minimizer name will be shortened from 'lm-scipy: j:best_available' to 'lm-scipy'
        minimizer = minimizer.split(':')[0].trim();
    }
    software = software.replace('-', '_');
    var search_text = `a[href*="_${cost_func}_${minimizer}_[${software}"]`;
    // Get the matching cell ids and the column numbers
    const matching_ids = [];
    $('td').each(function () {
        const anchor = $(this).find(search_text);
        if (anchor.length > 0) {
            var id = $(this).attr('id');
            matching_ids.push(id);  
        }
    });
    return matching_ids
}

/**
* Handles the case when a cost function is hidden or selected from the
* cost function dropdown menu.
* @param   {String} cost_func   The name of the cost function.
*/
function toggle_cost_function(cost_func) {
    var cost_function_header = $('th a.cost_function_header').filter(function () {
        return $(this).text().trim().toLowerCase() === cost_func;
    }).parent();
    const [matching_ids, cols] = _get_all_data_cell_ids(cost_func)
    
    // Hide the cost function header names
    const is_checked = $(`input[type="checkbox"][value="${cost_func}"]`).is(':checked');
    if (is_checked){
        // Show cost function header
        cost_function_header.show();
    
        // Get software names
        const software_names = _get_software_names()
        // Iterate over the softwares
        software_names.forEach(function (software) {

            const is_software_checked = $(`input[type="checkbox"][value="${software}"]`).is(':checked') || $(`input[type="checkbox"][value="${software}"]`).is(':disabled');

            if (is_software_checked){
                // Show software header
                const software_header = $('th a.software_header').filter(function () {
                    const name = $(this).text().trim() === software;
                    const thId = $(this).parent().attr('id');
                    const colMatch = thId.match(/col\d+$/);
                    const col = colMatch ? colMatch[0] : null;
                    return name && cols.includes(col);
                }).parent();
                software_header.show();

                // Get minimizer names
                const minimizer_names = _get_minimizer_names(software)
                // Iterate over the minimizers
                minimizer_names.forEach(function (minimizer){
                    var is_minimizer_checked = $(`input[type="checkbox"][value="${minimizer}"]`).is(':checked');

                    if (is_minimizer_checked){
                        // Show minimizer header
                        const minimizer_header = $('th a.minimizer_header').filter(function () {
                            const name = $(this).text().trim() === minimizer;
                            const thId = $(this).parent().attr('id');
                            const colMatch = thId.match(/col\d+$/);
                            const col = colMatch ? colMatch[0] : null;
                            return name && cols.includes(col);
                        }).parent();
                        minimizer_header.show();

                        // Get the data cell ids of the minimizer
                        const matching_minimizer_ids = _get_minimizer_data_cell_ids(cost_func, minimizer, software)
                        matching_minimizer_ids.forEach(function (id) {
                            // Show data cells
                            $('#' + id).show();
                        });
                    } 
                })
            }
        });
        
    } else {
        // Hide cost function header
        cost_function_header.hide();
        cols.forEach(function (id) {
            // Hide problem headers
            $(`#T_table_level1_${id}`).hide(); 
            // Hide minimizer headers
            $(`#T_table_level2_${id}`).hide(); 
        });
        matching_ids.forEach(function (id) {
            // Hide data cells
            $('#' + id).hide();
        });
    }

    // Adjust the column width of the cost function cell
    var width = _get_cost_func_header_span(cost_func);
    cost_function_header.attr('colspan', width);

}

/**
* Shows or hides the table header of the problem sizes.
*/
function toggle_prob_size_header() {

    var checkBox = document.getElementById("checkbox_prob_size");

    // If the checkbox is checked, display the problem size header column, otherwise hide it.
    if (checkBox.checked == true) {
        $('#T_table th:nth-child(2)').show();
    } else {
        $('#T_table th:nth-child(2)').hide();
    }
}


/**
* Sets multiple attributes for an element.
*/
function setAttributes(el, attrs) {
    for (var key in attrs) {
        el.setAttribute(key, attrs[key]);
    }
}

/**
* Allows to set iframe height.
*/
function set_iframe_height(path){

    var button1 = document.getElementById("offline_plot");
    var n_solvers_large = button1.dataset.value3;
    var profiles_info = document.getElementById("profiles_info");

    var is_dash_plot = path.startsWith("http");
    var pp_name = path.split('/').pop();

    if ((is_dash_plot) || n_solvers_large === "False") {
        number_of_pps = pp_name.split('+').length;
        iframe_height = number_of_pps*650;
        profiles_info.setAttribute("style", "display:block");

    } else {
        iframe_height = 100;
        profiles_info.setAttribute("style", "display:none");
    };
    return iframe_height;
}

/**
* Allows to switch between offline and online (Dash) performance profile plots.
*/
function load_src(_button) {
    var path = _button.dataset.value1.split("|");
    var iframewrapper = document.getElementsByClassName("iframe-wrapper")[0];

    var new_iframes = []
    for (p in path) {
        var new_iframe = document.createElement("iframe");
        setAttributes(new_iframe, {
            "src": path[p],
            "height": set_iframe_height(path[p]),
            "width": "100%",
            "frameborder": 0,
            "seamless": "seamless",
        });
        new_iframes.push(new_iframe);
    };

    iframewrapper.replaceChildren(...new_iframes);
}

/**
* Updates the display value dynamically based on the selected runtime metric.
*/
function update_runtime(metric) {
    sessionStorage.setItem("selected_runtime_metric", metric);

    const radios = document.querySelectorAll("input[name='runtime_selection']");
    radios.forEach(radio => {
        radio.checked = (radio.getAttribute("onclick") === `update_runtime('${metric}')`);
    });

    let linkElements = document.querySelectorAll("a.dark, a.light");

    linkElements.forEach(link => {
        let allRuntimeElements = link.querySelectorAll(".runtime");
        allRuntimeElements.forEach(element => {
            element.style.display = "none";
        });

        let selectedElement = link.querySelector(`#${metric}`);
        if (selectedElement) {
            selectedElement.style.display = "inline";
        }
    });
}


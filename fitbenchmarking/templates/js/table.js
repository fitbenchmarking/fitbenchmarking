/**
* Uses jQuery to find a collection of DOM elements with text equal to the provided search text.
* @param   {String} class_name    The name of a html element class to find.
* @param   {String} search_text   The text to search for.
* @param   {String} process_text  Determines whether to process text to lower case
* @return  {jQuery Object}        A collection of DOM elements which matched the jQuery search.
*/
function _find_element_from_text(class_name, search_text, process_text = true) {
    return $(class_name).filter(function () {
        if (process_text){
            var text = $(this).text().trim().toLowerCase()
        } else {
            var text = $(this).text().trim()
        }
        return text == search_text; 
    }).parent();
}

/**
* Adjusts the span of a header that encompasses a number of sub-headers.
* @param   {jQuery Object} header   A collection of DOM elements representing column headers with a span.
* @param   {bool} width             The width of the header.
*/
function _adjust_colspan(header, width) {
    if (width == 0) {
        header.hide();
    } else {
        if (width == 1) {
            header.show();
        }
        header.attr('colspan', width);
    }
}

/**
* Shows or hides the table row containing a specific problem.
* @param   {String} problem_name   The name of the problem as it appears in the table row header.
*/
function toggle_problem(problem_name) {
    var span_object = _find_element_from_text("a.problem_header", problem_name, process_text = false);
    span_object.parent().toggle();
}

/**
* Hides or shows the minimizers based on the checkbox
* selection from the dropdown menu.
* @param   {String} software   The name of the software corresponding to the minimizer.
* @param   {String} minimizer  The name of the minimizer as it appears in the table column header.
*/
function toggle_minimizer(software, minimizer) {
    // Retrive cost functions names used while benchmarking
    const cost_func_names = _get_cost_func_names();

    // Retrive minimizer checked status to determine whether to hide or show columns
    var is_minimizer_checked = $(`input[type="checkbox"][value="${minimizer}"]`).is(':checked');

    // Loop over cost functions
    cost_func_names.forEach(function (cost_func) {

        // Retrive cost function checked status to determine if sub-columns need updating
        const cost_function_is_checked = $(`input[type="checkbox"][value="${cost_func}"]`).is(':checked');

        if (cost_function_is_checked){
            // Call helper function that processes the minimizer column
            _process_minimizer_column(minimizer, is_minimizer_checked, software, cost_func)
        }         
    });

    // Call helper function that decides whether to
    // check/uncheck/disable the software checkboxes
    _update_software_checkboxes(software)

}

/**
* Helper function used to update the minimizer column.
* @param {String} minimizer   The name of the minimizer.
* @param {String} is_minimizer_checked   The checked status of the minimizer.
* @param {String} software - The name of the software.
* @param {String} cost_func - The name of the cost function.
*/
function _process_minimizer_column(minimizer, is_minimizer_checked, software, cost_func){

    // Get the data cell ids for a minimizer that is a sub-column of the given cost function
    const matching_ids = _get_minimizer_data_cell_ids(cost_func, minimizer, software)
    const column_number = matching_ids[0].split('col')[1].trim();

    // Retrive minimizer header that is a sub-column of the given cost function
    const minimizer_header = $('th a.minimizer_header').filter(function () {
        const name = $(this).text().trim() === minimizer;
        const thId = $(this).parent().attr('id') === `T_table_level2_col${column_number}`;
        return name && thId;
    }).parent();

    // Show/Hide minimizer header        
    if (is_minimizer_checked){
        minimizer_header.show();
    } else {
        minimizer_header.hide();
    }

    // Show/Hide data cells
    matching_ids.forEach(function (id) {
        if (is_minimizer_checked){
            $('#' + id).show();
        } else {
            $('#' + id).hide();
        }
    });

    // Retrive cost function header
    var cost_function_header = _find_element_from_text('th a.cost_function_header', cost_func);

    // Retrive software header that is a sub-column of the given cost function
    const software_header = $('th a.software_header').filter(function () {
        name_check = $(this).text().trim().toLowerCase() === software;

        // The cost function column check
        var cf_col_num = parseInt(cost_function_header.attr('id').split('col')[1].trim());
        var cf_col_span = _get_cost_func_header_span(cost_func, visible = false);
        var cf_col_check = cf_col_num <= column_number && column_number < cf_col_num + cf_col_span;

        // The software column check
        var s_col_num = parseInt($(this).parent().attr('id').split('col')[1].trim());
        var s_col_check = cf_col_num <= s_col_num && s_col_num < cf_col_num + cf_col_span;

        return name_check && cf_col_check && s_col_check;
    }).parent();

    // Adjust the column width of the cost function cell
    var width = _get_cost_func_header_span(cost_func);
    _adjust_colspan(cost_function_header, width)

    // Adjust the column width of the sofware cell
    var width = _get_software_header_span(cost_func, software);
    _adjust_colspan(software_header, width)

}


/**
* Helper function used to update the select software checkboxes.
* @param {String} software - The name of the software.
*/
function _update_software_checkboxes(software){

    var software_checkboxes = $(`input[type="checkbox"][value="${software}"]`);
    var software_has_single_minimizer = false;
    
    // Get all the unique minimizers names for a software
    const minimizer_names = _get_minimizer_names(software);

    if (minimizer_names.length === 1){
        software_has_single_minimizer = true;
    } 

    // Get the checked status and push them on to the checked list
    var checked = [];
    minimizer_names.forEach(function (name) {
        checked.push($(`input[type="checkbox"][value="${name}"]`).is(':checked'));
    });
    // Verify if all minimizers are checked or unchecked
    const all_checked = checked.every(check => check === true);
    const all_not_checked = checked.every(check => check === false);
    
    // Update the checkboxes
    if (all_checked){
        software_checkboxes.prop('disabled', false);
        software_checkboxes.prop('checked', true);
    } else {
        software_checkboxes.prop('checked', false);
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
 * Returns the span of the cost function header. It calculates
 * the span by counting the visible sub-column minimizers if 
 * visible is true, otherwise it counts all sub-column minimizers.
 * @param {String} cost_func - The name of the cost function.
 * @param {Boolean} visible - The bool to determine whether to count visible or all headers.
 */
function _get_cost_func_header_span(cost_func, visible = true) {
    const [_, cols] = _get_all_data_cell_ids(cost_func)

    // Count visible minimizers
    var width = 0;
    cols.forEach(function(col) {
        const th = $(`#T_table_level2_${col}`);
        if (visible) {
            if (th.is(':visible')){
                width += 1
            }
        } else {
            width += 1
        }
        
    })
    return width;
}

/**
 * Returns the span of the software header. It calculates
 * the span by counting the visible sub-column minimizers.
 * @param {String} cost_func - The name of the cost function.
 * @param {String} software - The name of the software.
 */
function _get_software_header_span(cost_func, software) {
    const [_, cols] = _get_all_data_cell_ids(cost_func)
    
    // Select the minimizer headers associated with the software
    const updated_cols = []
    cols.forEach(function(col) {
        const th = $(`#T_table_level2_${col}`);
        const link = th.find('a.minimizer_header');
        if (link.data('software') === software) {
            updated_cols.push(col)
        }
    });

    // Count visible minimizers
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
* Helper function that extracts the names of the
* cost functions used while benchmarking.
*/
function _get_cost_func_names(){
    var costfunc_names = []
    var cost_function_headers = $('th a.cost_function_header')
    cost_function_headers.each(function () {
        costfunc_names.push($(this).text().trim().toLowerCase());
    });
    // Returns the cost function names
    return costfunc_names
}

/**
* Helper function that extracts the names of the
* softwares used while benchmarking.
*/
function _get_software_names(){
    var software_names = []
    var software_headers = $('th a.software_header')
    software_headers.each(function () {
        software_names.push($(this).text().trim());
    });
    // Returns the unique software names
    return [...new Set(software_names)]
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
* Hides or shows all the minimizers of a software based
* on the checkbox selection from the dropdown menu.
* @param   {String} software   The name of the software.
*/
function toggle_software(software) {
    const is_checked = $(`input[type="checkbox"][value="${software}"]`).is(':checked');
    
    // Retrive cost functions and minimizers used while benchmarking
    const cost_func_names = _get_cost_func_names();
    const minimizer_names = _get_minimizer_names(software);

    // Process each cost function
    cost_func_names.forEach(function (cost_func) {

        // var cost_function_header = _find_element_from_text('th a.cost_function_header', cost_func);
        const cost_function_is_checked = $(`input[type="checkbox"][value="${cost_func}"]`).is(':checked');

        if (cost_function_is_checked){

            minimizer_names.forEach(function (minimizer) {
                // Call helper function that processes the minimizer column
                _process_minimizer_column(minimizer, is_checked, software, cost_func)
            });
            
        }         
    });

    // Set the minimizer checkboxes
    minimizer_names.forEach(function (minimizer) {
        var minimizer_checkboxes = $(`input[type="checkbox"][value="${minimizer}"]`)
        if (is_checked) {
            minimizer_checkboxes.prop('checked', true);
        } else {
            minimizer_checkboxes.prop('checked', false);
        }
    });
}

/**
* Retrives the ids and column numbers of the data cell for
* a given cost function.
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
* Retrives the ids of the data cell for a given cost function,
* minimizer and software.
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
    var search_text = `a[href*="_${cost_func}_${minimizer.toLowerCase()}_[${software}"]`;
    // Get the matching cell ids
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
* Hides or shows all the minimizers and softwares of a cost function
* based on the checkbox selection from the dropdown menu.
* @param   {String} cost_func   The name of the cost function.
*/
function toggle_cost_function(cost_func) {
    var cost_function_header = _find_element_from_text('th a.cost_function_header', cost_func);
    const [matching_ids, cols] = _get_all_data_cell_ids(cost_func)
    
    // Retrieve the checkbox status
    const is_checked = $(`input[type="checkbox"][value="${cost_func}"]`).is(':checked');

    if (is_checked){
        // Show cost function header
        cost_function_header.show();
    
        // Get software names
        const software_names = _get_software_names()
        // Iterate over softwares
        software_names.forEach(function (software) {

            // Retrieve software checked status
            const is_software_checked = $(`input[type="checkbox"][value="${software}"]`).is(':checked') || $(`input[type="checkbox"][value="${software}"]`).is(':disabled');

            if (is_software_checked){
                // Get minimizer names
                const minimizer_names = _get_minimizer_names(software)

                minimizer_names.forEach(function (minimizer) {
                    // Retrieve minimizer checked status
                    var is_minimizer_checked = $(`input[type="checkbox"][value="${minimizer}"]`).is(':checked');
                    // Call helper function that processes the minimizer column
                    _process_minimizer_column(minimizer, is_minimizer_checked, software, cost_func)
                });
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


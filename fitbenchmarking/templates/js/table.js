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
*/
function toggle_minimizer(software, minimizer) {
    var cost_function_header = $("a.cost_function_header").parent();
    var software_header = _find_element_from_text("a.software_header", software).parent();
    var minimizer_text = _find_element_from_text("a.minimizer_header", minimizer);
    var minimizer_header = minimizer_text.parent();

    // Toggle the minimizer header
    minimizer_header.toggle();

    // Decrement or increment the column span of the cost function and software header
    var is_visible = minimizer_header.is(":visible");

    _adjust_colspan(cost_function_header, is_visible);
    _adjust_colspan(software_header, is_visible);

    // Toggle the data cells in a column
    var table_id = software_header.parent().parent().parent().attr("id");

    minimizer_text.each(function () {
        var column_num = parseInt($(this).attr('col')) + 3;
        $("#" + table_id + " tr > td:nth-child(" + column_num + ")").toggle();
    });
}

/**
* Shows or hides the table header of the problem sizes.
*/
function toggle_prob_size_header() {

    var checkBox = document.getElementById("checkbox_prob_size");

    // If the checkbox is checked, display the problem size header column, otherwise hide it.
    if (checkBox.checked == true) {
        $('th:nth-child(2)').show();
    } else {
        $('th:nth-child(2)').hide();
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


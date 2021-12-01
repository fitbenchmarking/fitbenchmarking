function _find_element_from_text(class_name, search_text) { 
    return $(class_name).filter(function() { return $(this).text() == search_text; });
}

function toggle_row(name) {
    var span_object = _find_element_from_text("a.problem_header", name);
    span_object.parent().parent().toggle();
}

function toggle_column(solver, minimizer) {
    var solver_header = _find_element_from_text("a.solver_header", solver).parent();
    var minimizer_text = _find_element_from_text("span.minimizer_header", minimizer);
    var minimizer_header = minimizer_text.parent();

    // Toggle the minimizer header
    minimizer_header.toggle();

    // Decrement or increment the column span of the Solver header
    var colspan = parseInt(solver_header.attr('colspan'));
    new_colspan = minimizer_header.is(":visible") ? colspan + 1: colspan - 1;

    solver_header.attr('colspan', new_colspan);

    // Hide the solver header if no minimizers are shown
    if (new_colspan == 0) {
        solver_header.hide();
    } else {
        solver_header.show();
    }

    // Toggle the data cells in a column
    var table_id = solver_header.parent().parent().parent().attr("id");
    var column_num = parseInt(minimizer_text.attr('col')) + 2;

    $("#" + table_id + " tr > td:nth-child(" + column_num + ")").toggle();
}

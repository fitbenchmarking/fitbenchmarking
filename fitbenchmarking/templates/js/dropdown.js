function show_dropdown(dropdown_id) {
    var checkList = document.getElementById(dropdown_id);

    if (checkList.classList.contains('visible')) {
        checkList.classList.remove('visible');
    } else {
        checkList.classList.add('visible');
    }
}

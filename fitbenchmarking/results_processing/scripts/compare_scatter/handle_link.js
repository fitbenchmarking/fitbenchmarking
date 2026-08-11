function(data){
    if (!data) {
        return null;
    }
    const DATA_REPORT_FILE_INDEX = 3;
    var newpath = data.points?.[0]?.customdata?.[DATA_REPORT_FILE_INDEX];
    if (typeof(newpath) !== "undefined") {
        window.parent.postMessage({path:newpath},"*");
    }
    return null;
}
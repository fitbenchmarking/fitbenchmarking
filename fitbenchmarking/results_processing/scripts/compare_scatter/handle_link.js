function(data){
    if (!data) {
        return null;
    }
    var newpath = data.points?.[0]?.customdata?.[3];
    if (typeof(newpath) !== "undefined") {
        window.parent.postMessage({path:newpath},"*");
    }
    return null;
}
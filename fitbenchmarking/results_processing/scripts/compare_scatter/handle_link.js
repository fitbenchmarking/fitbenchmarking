function(data){
    if (!data) {
        return null;
    }
    var newpath = data.points?.[0]?.customdata?.[3];
    console.log(newpath);
    if (typeof(newpath) !== "undefined") {
        console.log("emitting");
        window.parent.postMessage({path:newpath},"*");
    }
    return null;
}
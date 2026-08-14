function() {
    const observer = new MutationObserver(() => {
    const el = document.getElementById(
        "compare_scatter_container");

    if (el && el.scrollHeight > 0) {
        window.parent.postMessage(
        {
            height: el.scrollHeight,
            src: "mutation"
        },
        "*"
        );
        observer.disconnect();
    }
    });

    observer.observe(document.body, { 
        childList: true, subtree: true 
    });
    return null;
}
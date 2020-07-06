var code = function () {
    var open = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function open(method, url, async) {
        if (url.indexOf("HifJzoc9") > -1) {
            debugger;
        }
    };
};
var script = document.createElement('script');
script.textContent = '(' + code + ')()';
(document.head || document.documentElement).appendChild(script);
script.parentNode.removeChild(script);

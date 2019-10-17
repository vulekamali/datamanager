import * as pym from 'pym.js'

(function() {
    const container = document.getElementById("programme-econ-small-multiples");
    if (container === null)
        // This runs on all pages so stop if container isn't on the page.
        return;

    const vizURL = container.getAttribute("data-src");
    new pym.Parent('programme-econ-small-multiples', vizURL);
})()

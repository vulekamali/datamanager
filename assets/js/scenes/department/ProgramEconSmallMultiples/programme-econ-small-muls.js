import * as pym from 'pym.js'

(function() {
    const container = document.getElementById("programme-econ-small-multiples");
    const vizURL = container.getAttribute("data-src");
    new pym.Parent('programme-econ-small-multiples', vizURL);
})()

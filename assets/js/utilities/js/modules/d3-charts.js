// TODO refactor with crop and wrap
export function fade(text, width) {
    text.each(function(d) {
        var padding = 10;
        var text = d3.select(this),
            words = text.text().split("").reverse(),
            word,
            line = [],
            lineNumber = 0,
            x = text.attr("x"),
            y = text.attr("y"),
            dy = 0, //parseFloat(text.attr("dy")),
            tspan = text.text(null)
                        .append("tspan")
                        .attr("x", x)
                        .attr("y", y)
                        .attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(""));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop()
                tspan.text(line.join(""));
                text.style("fill", "url(#text-fade)")
            }
        }
    });
}

export function crop(text, width) {
    text.each(function(d) {
        var padding = 10;
        // TODO wish there was a cleaner way to pass the width in to this
        // function
        var width = width || (d.x1 - d.x0 - padding);
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            x = text.attr("x"),
            y = text.attr("y"),
            dy = 0, //parseFloat(text.attr("dy")),
            tspan = text.text(null)
                        .append("tspan")
                        .attr("x", x)
                        .attr("y", y)
                        .attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop()
                tspan.text(line.join(" "));
            }
        }
    });
}

export function wrap(text, width, lineHeight) {
    lineHeight = lineHeight || 1.1; // ems
    text.each(function(d) {
        var padding = 10;
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            x = text.attr("x"),
            y = text.attr("y"),
            dy = 0, //parseFloat(text.attr("dy")),
            tspan = text.text(null)
                        .append("tspan")
                        .attr("x", x)
                        .attr("y", y)
                        .attr("dy", dy + "em");
        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan")
                            .attr("x", x)
                            .attr("y", y)
                            .attr("dy", ++lineNumber * lineHeight + dy + "em")
                            .text(word);
            }
        }
    });
}

function unique(x) {
    return x.reverse().filter(function (e, i, x) {return x.indexOf(e, i+1) === -1;}).reverse();
}

export var rand_human_fmt = function(x) {
    if (x >= 1000000000) {
        return rand_fmt(x / 1000000000) + " billion"
    } else if (x >= 1000000) {
        return rand_fmt(x / 1000000) + " million"
    } else {
        return rand_fmt(x)
    }
}

export var rand_fmt = function(x) {
    return "R" + d3.format(",.0f")(x);
}

export var slugify = function(x) {
    return x.replace(/\s+/g, "-").toLowerCase()
}

export var getViewportDimensions = function() {
    // Dynamically get the size of the viewport
    var baseWidth = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var baseHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    return {
        width: baseWidth,
        height: baseHeight
    }
}

export var getDimensions = function(el) {
    var rect = el.node().getBoundingClientRect();
    return {
        x: rect.x || rect.left,
        y: rect.y || rect.top,
        width: rect.width,
        height: rect.height

    }
}

var createBoundingBox = function(container, el) {
    var d = getDimensions(el);
    var box = container.append("rect")
        .attr("x", d.x)
        .attr("y", d.y)
        .attr("width", d.width)
        .attr("height", d.height)
        .classed("bounding-box", true)
    return box
}

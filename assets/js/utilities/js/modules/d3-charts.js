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
function wrap(text, width, lineHeight) {
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
            if (words.length > 1) {
                console.log(text.text())
            }
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

var slugify = function(x) {
}

export default crop;

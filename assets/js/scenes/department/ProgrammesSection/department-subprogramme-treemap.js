import {createMainLabel, createSVG, colorMap} from './elements.js';
import {
    getViewportDimensions,
    getDimensions,
    crop,
    rand_fmt,
    rand_human_fmt,
    slugify,
    fade,
} from '../../../utilities/js/modules/d3-charts.js';
import {getProgNameRef, getSubprogNameRef} from '../../../utilities/js/modules/vulekamali-openspending.js';

(function() {
    var container = d3.select(".department-subprogramme-treemap")
    if (container.empty())
        return;

    var mainConfig = {
        container: container,
        url: container.attr("data-aggregate-url"),
    }

    var model = JSON.parse(container.attr("data-openspending-model"));
    var progNameRef = getProgNameRef(model);
    var subprogNameRef = getSubprogNameRef(model);
    var valueField = "value.sum"

    var viewport = getViewportDimensions();

    // set the dimensions and margins of the graph
    var margin = {top: 0, right: 0, bottom: 0, left: 0},
        width = viewport.width - margin.left - margin.right,
        height = viewport.height - margin.top - margin.bottom

    var programmeOffset = 62;
    var budgetOffset = programmeOffset + 24;
    var treemapPadding = 3;

    var largestBudget = function(d) {
        var subprogrammes = d.parent.data.values;
        return d3.max(subprogrammes, function(x) { return x[valueField] })
    }

    function addProgrammeLabels(d) {
        var maxBudget = largestBudget(d)
        var budget = d.data[valueField];

        if (budget == maxBudget) {
            if (d.ry1 - d.ry0 > 30) {
                return d.data[progNameRef]
            } else {
                return ""
            }
        }
    }

    function fadeProgramme(d, i) {
        var maxBudget = largestBudget(d)
        var budget = d.data[valueField];

        if (budget == maxBudget) {
            var minX = d3.min(d.parent.children, function(el) { return el.x0;})
            var maxX = d3.max(d.parent.children, function(el) { return el.x1;})
            var width = maxX - minX;

            fade(d3.select(this), width - 10)
        }
    }

    function addSubprogrammeLabels(key, currency) {
        return function(d) {
            if (d.ry1 - d.ry0 > 50 && d.rx1 - d.rx0 > 100) {
                if (currency)
                    return rand_human_fmt(d.data[key])
                return d.data[key]
            } else {
                return ""
            }
        }
    }

    function updateRangeCoordinates(data, x, y) {
        data.map(function(d) {
            d.rx0 = x(d.x0);
            d.rx1 = x(d.x1);
            d.ry0 = y(d.y0);
            d.ry1 = y(d.y1);
        })
    }

    function zoom(d) {

        parent = d.parent;
        // unzoom if already zoomed
        if (
            x.domain()[0] == parent.x0 && x.domain()[1] == parent.x1
                && y.domain()[0] == parent.y0 && y.domain()[1] == parent.y1
        ) {
            x.domain([0, width]);
            y.domain([0, treemapHeight]);
            parent = d.parent.parent;
        } else {
            x.domain([parent.x0, parent.x1]);
            y.domain([parent.y0, parent.y1]);

        }

        updateRangeCoordinates(d3.selectAll(".box").data(), x, y)

        var clamp = function(scale, val) {
            if (val < scale.domain()[0])
                return scale.range()[0];
            else if (val > scale.domain()[1])
                return scale.range()[1];
            else
                return scale(val)
        }

        var t = d3.transition()
            .duration(800)
            .ease(d3.easeCubicOut);

        d3.selectAll("rect.tile")
            .transition(t)
            .attr('x', function (d) { return clamp(x, d.x0) })
            .attr('y', function (d) { return clamp(y, d.y0) })
            .attr('width',  function(d) { return clamp(x, d.x1) - clamp(x, d.x0)})
            .attr('height', function(d) { return clamp(y, d.y1) - clamp(y, d.y0)})

        function displayLabels(d) {
            if (d.x0 < x.domain()[0] || d.x1 > x.domain()[1]
                || d.y0 < y.domain()[0] || d.y1 > y.domain()[1])
                return "none";
            return "block"
        }

        d3.selectAll(".programme-label tspan")
            .transition(t)
            .attr("x", function(d) { return clamp(x, d.x0) + 5})
            .attr("y", function(d) { return clamp(y, d.y0) + 28})
            .text(addProgrammeLabels)
            .style("display", displayLabels)
            .each(fadeProgramme)

        d3.selectAll(".box .subprogramme-label tspan")
            .transition(t)
            .attr("x", function(d) { return clamp(x, d.x0) + 5})
            .attr("y", function(d) { return clamp(y, d.y1) - 30})
            .text(addSubprogrammeLabels(subprogNameRef))
            .style("display", displayLabels)

        d3.selectAll(".box .subprogramme-budget-label tspan")
            .transition(t)
            .attr("x", function(d) { return clamp(x, d.x0) + 5})
            .attr("y", function(d) { return clamp(y, d.y1) - 6})
            .text(addSubprogrammeLabels(valueField, true))
            .style("display", displayLabels)
    }


    var svg = createSVG(mainConfig.container, viewport.width, viewport.height)
        .attr("transform", "translate(" + margin.left + ", " + margin.top + ")");

    var gradient = svg
        .append("defs")
        .append("linearGradient")
        .attr("id", "text-fade")
        .attr("x1", "0%")
        .attr("y1", "100%")
        .attr("x2", "100%")
        .attr("y2", "100%")

    gradient
        .append("stop")
        .attr("offset", "95%")
        .style("stop-color", "rgb(255,255,255)")
        .style("stop-opacity", "1")

    gradient
        .append("stop")
        .attr("offset", "100%")
        .style("stop-color", "rgb(255,255,255)")
        .style("stop-opacity", "0")

    var labels = svg.append("g")
        .classed("top-labels", true);

    var nester = d3
        .nest()
        .key(function(d) { return d[progNameRef]})

    var programmeButton = labels
        .append("g")
        .classed("programme-button", true)

    createMainLabel(programmeButton, "PROGRAMME")

    var programmeLabel = labels
        .append("text")
        .classed("programme-label", true)
        .text("All programmes")
        .attr("transform", "translate(0, " + programmeOffset + ")")

    var programmeBudgetLabel = labels
        .append("text")
        .classed("programme-budget-label", true)
        .text("R0")
        .attr("transform", "translate(0, " + budgetOffset + ")")

    var subprogrammeButton = labels
        .append("g")
        .classed("subprogramme-button", true)
        .attr("transform", "translate(" + (width / 1.8 - 10) + ", 0)")


    createMainLabel(subprogrammeButton, "SUB-PROGRAMME")

    var subprogrammeLabel = subprogrammeButton
        .append("text")
        .classed("subprogramme-label", true)
        .text("None selected")
        .attr("transform", "translate(0, " + programmeOffset + ")")

    var subprogrammeBudgetLabel = subprogrammeButton
        .append("text")
        .classed("subprogramme-budget-label", true)
        .text("R0")
        .attr("transform", "translate(0, "  + budgetOffset + ")")

    var labelDimensions = getDimensions(labels);
    var labelSeparatorOffset = -25;

    subprogrammeButton
        .append("line")
        .classed("label-separator", true)
        .attr("x1", labelSeparatorOffset)
        .attr("x2", labelSeparatorOffset)
        .attr("y1", labelDimensions.y)
        .attr("y2", labelDimensions.height + labelDimensions.y + 10)

    var treemapOffset = 10;
    var treemapHeight = height - labelDimensions.height - labelDimensions.y - treemapOffset;
    var x = d3.scaleLinear().domain([0, width]).range([0, width])
    var y = d3.scaleLinear().domain([0, treemapHeight]).range([0, treemapHeight]);
    var treemap = svg.append("g")
        .attr("transform", "translate(" + -treemapPadding * 2 + ", " + (labelDimensions.y + labelDimensions.height + treemapOffset) + ")")


    d3.json(mainConfig.url).then(function(data) {
        data = data.cells.sort(function(a, b) {
            return b[valueField] - a[valueField];
        });

        var nested_data = nester.entries(data);

        var root = d3.hierarchy(
            {values:nested_data},
            function(d) { return d.values }
        )
            .sum(function(d) { return d[valueField]})

        // Then d3.treemap computes the position of each element of the hierarchy
        d3.treemap()
            .size([width, treemapHeight])
            .padding(1)
            .paddingOuter(treemapPadding)
        (root)

        updateRangeCoordinates(root.leaves(), x, y)

        var boxes = treemap
            .selectAll("g")
            .data(root.leaves())
            .enter()
            .append("g")
            .classed("box", true)

        // Add rectangles
        boxes
            .append("rect")
            .classed("tile", true)
            .attr('x', function (d) {return x(d.x0)})
            .attr('y', function (d) { return y(d.y0)})
            .attr('width', function (d) {return x(d.x1- d.x0)})
            .attr('height', function (d) { return y(d.y1 - d.y0)})
            .attr("data-programme", function(d, i) {
                return slugify(d.data[progNameRef])
            })
            .style("fill", function(d, idx) {
                var programmes = root.data.values.map(function(d) { return d.key});
                var subprogrammes = d.parent.data.values;
                var subprogramme_labels = subprogrammes.map(function(d) { return d[subprogNameRef];});

                var idx = programmes.indexOf(d.data[progNameRef])
                var idx2 = subprogramme_labels.indexOf(d.data[subprogNameRef]);
                var hues = colorMap[idx];
                return hues[idx2];
            })
            .on("mouseover", function(d) {
                programmeLabel.text(d.data[progNameRef])
                subprogrammeLabel.text(d.data[subprogNameRef])
                programmeBudgetLabel.text(rand_fmt(d.parent.value));
                subprogrammeBudgetLabel.text(rand_fmt(d.value));

            })
            .on("mouseout", function(d) {
                programmeBudgetLabel.text(rand_fmt(d.parent.parent.value))
                programmeLabel.text("All programmes")
                subprogrammeLabel.text("None selected")
                subprogrammeBudgetLabel.text("R0")
            })
            .on("click", zoom)

        // Add programme labels
        treemap
            .selectAll(".programme-label")
            .data(root.leaves())
            .enter()
            .append("text")
            .classed("programme-label", true)
            .attr("x", function(d) { return d.x0 + 5})
            .attr("y", function(d) { return d.y0 + 28})
            .text(addProgrammeLabels)
            .attr("font-size", "0.6em")
            .attr("fill", "white")
            .each(fadeProgramme)

        // Add subprogramme labels
        boxes
            .append("text")
            .classed("subprogramme-label", true)
            .attr("x", function(d) { return d.x0 + 5})
            .attr("y", function(d) { return d.y1- 30})
            .text(addSubprogrammeLabels(subprogNameRef))
            .attr("font-size", "0.6em")
            .attr("fill", "white")
            .each(function(d, i) {
                var width = d.x1 - d.x0;
                fade(d3.select(this), width - 5)
            })

        // Add subprogramme budgets
        boxes
            .append("text")
            .classed("subprogramme-budget-label", true)
            .attr("x", function(d) { return d.x0 + 5})
            .attr("y", function(d) { return d.y1 - 8})
            .text(addSubprogrammeLabels(valueField, true))
            .attr("font-size", "0.6em")
            .attr("fill", "white")
            .call(fade)

        programmeBudgetLabel
            .datum(root)
            .text(function(d) {
                return rand_fmt(d.value)
            })

    })
})();

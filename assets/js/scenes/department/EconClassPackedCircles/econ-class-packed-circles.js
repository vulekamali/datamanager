import {createMainLabel, createSVG, colorMap2} from '../../../utilities/js/modules/d3-chart-elements.js';
import {
    getViewportDimensions,
    getDimensions,
    crop,
    rand_fmt,
    rand_human_fmt,
    slugify,
    fade,
    unique,
} from '../../../utilities/js/modules/d3-charts.js';
import {
    getProgNameRef,
    getSubprogNameRef,
    getEconClass4Ref,
} from '../../../utilities/js/modules/vulekamali-openspending.js';

(function() {
    var container = d3.select(".department-econ-class-packed-circles")
    if (container.empty())
        return;
    var mainConfig = {
        container: container,
        url: container.attr("data-aggregate-url")
    }

    var model = JSON.parse(container.attr("data-openspending-model"));
    var progNameRef = getProgNameRef(model);
    var subprogNameRef = getSubprogNameRef(model);
    var econ4Ref = getEconClass4Ref(model);
    var valueField = "value.sum";

    var viewport = getViewportDimensions();
    var sectionPadding = 24;
    var boxPadding = 15;
    var bubbleChartOffset = 0;
    var sectionLeft = (viewport.width - 24) / 3;
    var sectionRight = viewport.width - (viewport.width - 24) / 3;
    var bubbleChart;

    // set the dimensions and margins of the graph
    var margin = {top: 0, right: 0, bottom: 0, left: 0},
        width = viewport.width - margin.left - margin.right,
        height = viewport.height - margin.top - margin.bottom,
        x = d3.scaleLinear().domain([0, width]).range([0, width]),
        y = d3.scaleLinear().domain([0, height]).range([0, height]);

    var svg = createSVG(mainConfig.container, viewport.width, viewport.height)


    var leftSection = svg.append("g").classed("left-section", true);
    var middleSection = svg.append("g").classed("middle-section", true);
    var rightSection = svg
        .append("g")
            .attr("transform", "translate(" + (sectionLeft + sectionPadding) + ", 0)")
            .classed("right-section", true);

    middleSection
        .append("line")
            .classed("label-separator", true)
            .attr("x1", 0)
            .attr("x2", 0)
            .attr("y1", 0)
            .attr("y2", 90)
            .attr("transform", "translate(" + sectionLeft + ", 0)")

    var labels = svg
        .append("g")
            .classed("top-labels", true)
            .attr("transform", "translate(" + margin.left + ", " + margin.top + ")")

    function createBudgetSection(container) {
        var econContainer = container.append("g").classed("budget-section", true);

        var classificationSection = econContainer.append("g").attr("transform", "translate(" + 10 + ", 0)")
        createMainLabel(classificationSection, "ECONOMIC CLASSIFICATION")

        classificationSection.append("text")
            .classed("economic-classification", true)
            .text("None Selected")
            .attr("transform", "translate(6, 55)")

        classificationSection.append("text")
            .classed("budget-amount", true)
            .text("R0")
            .attr("transform", "translate(6, 80)")

        return econContainer

    }

    function createLegend(container, programmes, colScale) {
        var legend = container.
            append("g")
                .classed("legend", true)

        var mainLabel = createMainLabel(legend, "PROGRAMME");

        var bbox = getDimensions(mainLabel);

        var legendItems = legend
            .append("g")
                .classed("legend-items", true)
                .selectAll(".item")
                .data(programmes)
                .enter()
                .append("g")
                .attr("transform", "translate(0, " + (bbox.y + bbox.height + sectionPadding) + ")")
                    .classed("item", true)
                    .on("click", function(d) { unselect(d); })

        var rects = legendItems
            .append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("rx", 8)
                .attr("ry", 8)
                .style("fill", colScale)
                .classed("legend-item-box", true)

        var boxHeight = getDimensions(rects).width;
        var boxDisplacement = boxHeight + boxPadding;

        rects
            .attr("transform", function(d, idx) {
                return "translate(0, " + (idx * boxDisplacement) + ")"
            })


        var backgroundPadding = 2;
        var legendItemBackgrounds = legendItems
            .append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("rx", 3)
                .attr("ry", 3)
                .attr("transform", function(d, idx) {
                    return "translate(" + (boxDisplacement) + ", " + (idx * boxDisplacement - backgroundPadding) + ")"
                })
                .attr("height", boxHeight + 2 * backgroundPadding)
                .classed("legend-item-text-background", true)

        legendItems
            .append("text")
                .attr("x", 0)
                .attr("y", 0)
                .attr("transform", function(d, idx) {
                    return "translate(" + (boxDisplacement + backgroundPadding * 2) + ", " + (idx * boxDisplacement) + ")"
                })
                .attr("dy", "1em")
                .text(function(d) { return d; })
                .style("fill", "black")
                .classed("legend-item-text", true)

        legendItemBackgrounds
            .each(function(d) {
                var bbox = getDimensions(d3.select(this.nextSibling));
                d3.select(this).attr("width", bbox.width + backgroundPadding * 4);
            });

        return legend;
    }

    function createHead(container, programmes, colScale) {
    }

    function unselect(programme) {
        d3.selectAll(".bubble circle")
            .classed("unselected", function(d) {
                if (d[progNameRef] != programme)
                    return !d3.select(this).classed("unselected")
                return false
            })

        d3.selectAll(".legend-items rect")
            .classed("unselected", function(d) {
                if (d != programme)
                    return !d3.select(this).classed("unselected")
                return false
            })
    }


    function createCircles(container, data, colScale) {
        var simulation = d3.forceSimulation()
            .force("x", d3.forceX(0 / 2).strength(0.1))
            .force("y", d3.forceX(height / 2).strength(0.1))
            .force("collide", d3.forceCollide(function(d) { return radiusScale(d[valueField])}))

        var radiusScale = d3.scaleSqrt().domain([
            d3.min(data, function(d) { return d[valueField]}),
            d3.max(data, function(d) { return d[valueField]})
        ]).range([viewport.height / 100, viewport.height / 10])

        var circles = container
            .selectAll("g")
            .data(data)
            .enter()
            .append("g")
                .classed("bubble", true)
                .on("mouseover", function(d) {
                    d3.select(".economic-classification").text(d[econ4Ref])
                    d3.select(".budget-amount").text(rand_fmt(d[valueField]))
                })

                .on("click", function(d) {
                    var programme = d[progNameRef]
                    unselect(programme);
                })

        circles
            .append("circle")
                .attr("r", function(d) { return radiusScale(d[valueField]) })
                .style("fill", function(d) {
                    return colScale(d[progNameRef]);
                })
                .classed("econ-circle", true)

        circles
            .append("text")
            .text(function(d) {
                if (radiusScale(d[valueField]) > 20) {
                    return d[econ4Ref]
                } else {
                    return "";
                }
            })
            .classed("econ-label", true)
            .style("font-size", function(d) {
                var radius = radiusScale(d[valueField])
                var a = Math.min(2 * radius, (2 * radius - 8) / this.getComputedTextLength() * 24) + "px";
                return a;
            })
            .attr("dy", ".35em")

        simulation.nodes(data).on("tick", ticked);

        function ticked() {
            circles.attr("transform", function(d) {
                var radius = radiusScale(d[valueField])
                d.y = Math.max(radius, Math.min(height - bubbleChartOffset - radius - 24, d.y));
                d.x = Math.max(radius, Math.min(width - (sectionLeft + sectionPadding + radius), d.x));
                return "translate(" + d.x + ", " + d.y + ")";
            });

            var bbox = getDimensions(container);
            svg.select(".bubble-chart-bbox")
                .attr("x", bbox.x)
                .attr("y", bbox.y)
                .attr("width", bbox.width)
                .attr("height", bbox.height)
            }
    }


    d3.json(mainConfig.url).then(function(data) {
        data = data.cells;

        var programmes = unique(data.map(function(d) { return d[progNameRef]; }));
        var colScale = d3.scaleOrdinal().domain(programmes).range(colorMap2)


        var legend = createLegend(leftSection, programmes, colScale);

        var budgetLabel = createBudgetSection(rightSection);


        var bbox = getDimensions(budgetLabel);

        var bubbleChartOffset = bbox.y + bbox.height + 32;
        var bubbleChart = rightSection
            .append("g")
                .classed("bubble-chart", true)
                .attr("transform", "translate(0, " + bubbleChartOffset + ")")

        createCircles(bubbleChart, data, colScale);


    });


})();

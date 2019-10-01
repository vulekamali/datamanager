export function createMainLabel(container, label, config) {
    var config = config || {};
    var padding = config.padding || 5;

    var programmeButton = container
        .append("g")
            .classed("main-label", true)

    var background = programmeButton
        .append("rect")
            .attr("rx", 3)
            .attr("ry", 3)
            .attr("x", 0)
            .attr("y", 0)

    var text = programmeButton
        .append("text")
            .text(label)

    var bbox = text.node().getBBox();
    text.attr("transform", "translate(" + padding + ", " + -bbox.y + ")")
    text.attr("dy", "5")

    background
        .attr("width", bbox.width + 2 * padding)
        .attr("height", bbox.height + 2 * padding)

    return programmeButton;
}

export function createSVG(container, width, height) {
    var svg = container
        .append("svg")
            .attr("viewBox", "0 0 " + width + " " + height)
            .attr("xmlns", "http://www.w3.org/2000/svg")
            .attr("preserveAspectRatio", "xMinYMin meet")
            .classed("svg-content-responsive", true)
            .append("g")

    return svg
}

export function addLinearGradient(container, id, color1, color2, offset1, offset2) {
    var gradient = container
        .append("defs")
            .append("linearGradient")
                .attr("id", id)
                .attr("x1", "0%")
                .attr("y1", "100%")
                .attr("x2", "100%")
                .attr("y2", "100%")

    offset1 = offset1 || "0%"
    offset2 = offset1 || "100%"

    gradient.append("stop")
        .attr("offset", 0)
        .attr("stop-color")

    gradient.append("stop")
        .attr("offset", 100)
        .attr("stop-color")
}

export var colorMap = [
    ["#2C35AA", "#4050C7", "#5D76F4", "#546BE7", "#5D76F4", "#788FF7", "#96A7F9", "#B2BEFA", "#D2D9FC", "#E7EAFC"],
    ["#7D1D4E", "#9F2757", "#B22E5B", "#C73361", "#D63864", "#DA4F7A", "#DF6B92", "#E793B0", "#EFBED0", "#F8E5EC"],
    ["#1D4B40", "#2C675C", "#33776B", "#3C877B", "#429388", "#52A39A", "#6AB4AC", "#91C9C4", "#BBDEDB", "#E3F1F1"],
    ["#E68537", "#EEAB46", "#F2C34F", "#F8DA58", "#FCEC60", "#FDEF72", "#FDF288", "#FEF5A8", "#FEF9CA", "#FFFDE9"],
    ["#3A2723", "#4A352F", "#594139", "#684D43", "#74564A", "#886F65", "#9D8980", "#B9AAA5", "#D5CCC9", "#EEEBE9"],
    ["#000000", "#212121", "#424242", "#616161", "#757575", "#9E9E9E", "#BDBDBD", "#E0E0E0", "#EEEEEE", "#F5F5F5"],
    ["#285F63", "#39818D", "#4295A5", "#4CA9BE", "#54B9D1", "#60C4D7", "#74CEDE", "#97DCE8", "#BEEAF1", "#E4F7FA"]
]

export var colorMap2 = ["#4B5DD6", "#4C2EA2", "#8F31AA", "#CB332B", "#33776B", "#749D47", "#F2C34F", "#E68231", "#594139", "#495A63"];

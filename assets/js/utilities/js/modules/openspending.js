export function getDimension(model, hierarchyName, level) {
    if (typeof(level) === 'undefined')
        level = 0;

    return model.hierarchies[hierarchyName].levels[level];
}

export function getRef(model, dimensionName, refType) {
    return model.dimensions[dimensionName][refType + "_ref"];
}

import {getRef, getDimension} from './openspending.js';

export function getProgNameRef(model) {
    return getRef(model, getProgDimension(model), "label");
}

export function getProgDimension(model) {
    return getDimension(model, "activity");
}

export function getSubprogNameRef(model) {
    return getRef(model, getSubprogDimension(model), "label");
}

export function getSubprogDimension(model) {
    return getDimension(model, "activity", 1);
}

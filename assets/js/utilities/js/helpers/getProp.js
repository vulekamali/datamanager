import decodeHtmlEntities from './decodeHtmlEntities.js';


const parseString = (string, parse) => {
  switch (parse) {
    case 'json': return JSON.parse(string);
    case 'num': return parseFloat(string, 10);
    default: return string;
  }
};

function innerGetProp(name, node, parse, valueParse) {
  const result = node.getAttribute(`data-${name}`);

  if (parse === 'node') {
    const innerNode = node.querySelector(`[data-${name}]`);

    if (!valueParse) {
      return innerNode;
    }

    return {
      node: innerNode,
      value: innerGetProp(name, innerNode, valueParse),
    };
  }

  if (result === null) {
    return null;
  }

  if (parse === 'bool') {
    return result !== null;
  }

  return parseString(decodeHtmlEntities(result), parse);
}


export default innerGetProp;


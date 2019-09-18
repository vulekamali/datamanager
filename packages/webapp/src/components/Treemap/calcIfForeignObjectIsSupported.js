/**
Borrow feature detection from Modernizr
https://stackoverflow.com/a/24566105/1305080
*/

const calcIfForeignObjectIsSupported = () => {
  if (!document.createElementNS) {
    return false;
  }

  const toStringFnc = ({}).toString;
  const createForeignObject = toStringFnc.call(document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject'));
  return /SVGForeignObject/.test(createForeignObject)
}

export default calcIfForeignObjectIsSupported;

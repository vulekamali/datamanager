import arrayFrom from 'array.from';
import promisePolyfill from 'promise-polyfill';
import every from 'array.prototype.every';
import findIndex from 'array.prototype.findindex';
import assign from 'object.assign';
import './arrayIncludes';


function polyfillOldFeatures() {
  if (!window.Array.findIndex) {
    findIndex.shim();
  }

  if (!window.Object.assign) {
    window.Object.assign = assign.getPolyfill();
  }

  if (!window.Array.from) {
    window.Array.from = arrayFrom;
  }

  if (!window.Promise) {
    window.Promise = promisePolyfill;
  }

  if (!Array.prototype.every) {
    Array.prototype = {
      ...Array.protoype,
      every,
    };
  }

  if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position) {
      position = position || 0;
      return this.indexOf(searchString, position) === position;
    };
  }
}


export default polyfillOldFeatures();

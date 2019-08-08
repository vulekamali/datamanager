import { intersectionBy, mergeWith, has } from 'lodash';
import lunr from 'lunr';
import wrapStringPhrases from './../../../utilities/js/helpers/wrapStringPhrases.js';


export default function lunrSearchWrapper(array, refProp, fieldProps, search) {
  // Normalises fieldProps into an array, even when passed as string
  const fieldPropsArray = Array.isArray(fieldProps) ? fieldProps : [fieldProps];


  // Create Lunr index object
  /* eslint-disable func-names */
  const index = lunr(function () {
    fieldPropsArray.forEach(prop => this.field(prop));
    this.ref(refProp);
    array.forEach(object => this.add(object));
  });
  /* eslint-enable */


  // Perfrom Lunr search and edits copy of original array to reflect Lur results
  const rawResult = index.search(search);

  const renameProp = (val) => {
    return {
      [refProp]: val.ref,
    };
  };

  const normalisedResult = rawResult.map(renameProp);

  return intersectionBy(
    array,
    normalisedResult,
    object => object[refProp],
  );
}

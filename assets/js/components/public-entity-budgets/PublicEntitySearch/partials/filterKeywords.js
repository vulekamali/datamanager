import lunrSearchWrapper from './../../../../utilities/js/helpers/lunrSearchWrapper.js';
import wrapStringPhrases from './../../../../utilities/js/helpers/wrapStringPhrases.js';


export default function filterKeywords(keywords, results) {
  return results.map((group) => {
    const filteredItems = lunrSearchWrapper(
      results,
      'slug',
      'name',
      keywords,
    );

    const phraseArray = [keywords, ...keywords.split(' ')];
    const wrapFn = string => `<em class="Highlight">${string}</em>`;

    const currentItems = filteredItems.map((obj) => {
      return {
        ...obj,
        name: wrapStringPhrases(obj.name, phraseArray, wrapFn),
      };
    });

    return {
      ...group,
      public_entities: currentItems,
    };
  });
}

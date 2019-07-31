import wrapStringPhrases from './../../../../utilities/js/helpers/wrapStringPhrases.js';


export default function highlightResults(results, phrase) {
  const phrasesArray = [phrase, ...(phrase.split(' '))];
  const highlightFn = innerString => `<em class="Highlight">${innerString}</em>`;

  const buildSnippet = (itemObj) => {
    return wrapStringPhrases(itemObj.snippet, phrasesArray, highlightFn);
  };

  return {
    ...results,
    items: results.items.map((itemObj) => {
      return {
        ...itemObj,
        title: wrapStringPhrases(itemObj.title, phrasesArray, highlightFn),
        snippet: itemObj.snippet ? buildSnippet(itemObj) : null,
      };
    }),
  };
}

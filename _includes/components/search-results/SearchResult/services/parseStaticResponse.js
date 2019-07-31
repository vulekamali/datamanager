import lunrSearchWrapper from './../../../../utilities/js/helpers/lunrSearchWrapper.js';
import wrapStringPhrases from './../../../../utilities/js/helpers/wrapStringPhrases.js';


const glossaryToArray = (glossaryObj) => {
  const keysArray = Object.keys(glossaryObj);

  const convertItemToArray = (obj) => {
    return (title) => {
      const description = obj[title];
      return { title, description };
    };
  };

  return keysArray.map(convertItemToArray(glossaryObj));
};


const buildResult = (phrase, videosResult, glossaryResult) => {
  const phraseArray = [phrase, ...phrase.split(' ')];
  const wrapFn = string => `<em class="Highlight">${string}</em>`;

  const addVideoHighlights = (array) => {
    if (array.length <= 0) {
      return null;
    }

    const languages = array[0].languages;

    return {
      count: array.length,
      title: wrapStringPhrases(array[0].title, phraseArray, wrapFn),
      description: wrapStringPhrases(array[0].description, phraseArray, wrapFn),
      url: `/videos?phrase=${phrase}`,
      open: false,
      languages: array[0].languages,
      id: languages[(Object.keys(languages)[0])],
    };
  };

  const addGlossaryHighlights = (array) => {
    if (array.length <= 0) {
      return null;
    }

    return {
      count: array.length,
      title: wrapStringPhrases(array[0].title, phraseArray, wrapFn),
      description: wrapStringPhrases(array[0].description, phraseArray, wrapFn),
      url: `/glossary?phrase=${phrase}`,
    };
  };

  return {
    videos: addVideoHighlights(videosResult),
    glossary: addGlossaryHighlights(glossaryResult),
  };
};


export default function parseStaticResponse(phrase, videos, glossary) {
  const videosResult = lunrSearchWrapper(
    videos,
    'id',
    ['title', 'description'],
    phrase,
  );

  const glossaryResult = lunrSearchWrapper(
    glossaryToArray(glossary),
    'title',
    ['title', 'description'],
    phrase,
  );

  return buildResult(phrase, videosResult, glossaryResult);
}

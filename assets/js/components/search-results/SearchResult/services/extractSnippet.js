import { escape } from 'lodash';


const escapeText = (string) => {
  const withoutMultipleSpaces = string.replace(/\s+/gm, ' ')
  return escape(withoutMultipleSpaces.replace(/[^a-zA-Z0-9]{5,1000}/g, ' '));
};


const scanResources = (resourcesList) => {
  for (let i = 0; i < resourcesList.length; i++) {
    const resource = resourcesList[i];

    if (resource.highlighting && resource.highlighting.fulltext) {
      const highlightArray = resource.highlighting.fulltext;

      return {
        url: resource.url,
        text: escapeText(highlightArray[0]),
      };
    }
  }

  return null;
};


export default function extractSnippet(itemObj, isOfficial) {
  if (!isOfficial) {
    if (itemObj.highlighting.notes) {
      return {
        text: escapeText(itemObj.highlighting.notes[0]),
        organization: itemObj.organization.title,
      };
    }
  }

  if (itemObj.resources && itemObj.resources.length > 0) {
    const partial = scanResources(itemObj.resources);

    if (partial) {
      return {
        ...partial,
        organization: itemObj.organization.title,
      };
    }
  }

  return null;
}

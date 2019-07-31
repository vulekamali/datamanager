export default function wrapStringPhrases(string, phrases, templateFn) {

  // Create regular experession string by concatenating all string in the phrases array with the regex 'or' operator.
  const sortFromLongToShort = (a, b) => b.length - a.length;
  const regExpTermsWithOrOperators = phrases.sort(sortFromLongToShort).join('|');

  // Escapes all regex-specific operators from the regex string.
  const escapeRegExp = regexString => regexString.replace(/[\/\-\[\\\]\{\}\(\)\*\+\?\.\,\^\$\#\s]/gi, '\\$&');
  const escapededRegExp = escapeRegExp(regExpTermsWithOrOperators);

  // Creates an actual regular expression from the regex string.
  const regex = new RegExp(`(?:^|\\b)${escapededRegExp}(?!\\w)`, 'gi');

  // Runs the passed function (regex match is automatically passed as the first parameter) on all matches of the regex and replaces the match with the function's return.
  return string.replace(regex, templateFn);
}
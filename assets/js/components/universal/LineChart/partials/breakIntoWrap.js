export default function breakIntoWrap(string, wrap) {
  const splitter = string.split(' ');

  let count = 0;
  let word = '';
  let results = [];

  for (let i = 0; i < splitter.length; i++) {
    if (splitter[count].length >= wrap) {
      // for (let ii = 0; ii < splitter[count].length; ii += wrap) {
      //   results.push(splitter[count].substr(ii, wrap));
      // }

      results.push(splitter[count]);

      word = '';
      count++;
    } else {
      word = `${word} ${splitter[count]}`;
      count++;

      if (word.length >= wrap) {
        results.push(word);
        word = '';
      }

      if (i === splitter.length - 1) {
        results.push(word);
        word = '';
      }
    }
  }

  return results;
}

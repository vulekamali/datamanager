const randomNumber = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

const blankArray = (length, content = null) => Array(length).fill(content);

const randomLengthBlankArray = (min, max, content) => {
  const length = randomNumber(min, max);
  return blankArray(length, content);
};

const arrayOfNumbers = (min, max, length) => {
  const result = blankArray(length).map(() => randomNumber(min, max));
  return result;
};

const randomFromArray = (array = [], min, providedMax) => {
  const maxLength = array.length < 1 ? 0 : array.length - 1;
  const max = providedMax <= maxLength ? providedMax : maxLength;
  return array[randomNumber(min || 0, max)];
};

const randomBool = () => !!randomNumber(0, 1);

export {
  randomBool,
  randomFromArray,
  randomNumber,
  blankArray,
  randomLengthBlankArray,
  arrayOfNumbers,
};

export default {
  randomBool,
  randomFromArray,
  randomNumber,
  blankArray,
  randomLengthBlankArray,
  arrayOfNumbers,
};

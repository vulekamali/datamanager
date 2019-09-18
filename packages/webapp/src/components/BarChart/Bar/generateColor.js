import { colors } from './data.json';

const amountOfColors = colors.length;

function* createColorGenerator() {
  let count = 0;

  while (true) {
    if (count >= amountOfColors) {
      count = 0;
    }

    const color: Tcolor = colors[count];
    yield color;

    count += 1;
  }
}

export default createColorGenerator;

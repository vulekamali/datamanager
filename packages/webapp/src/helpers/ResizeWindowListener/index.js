import { debounce } from 'lodash';


class ResizeWindowListener {
  constructor(callback, { delay = 300, dimension } = {}) {
    this.callback = callback;
    this.debouncedResize = debounce(this.onResize, delay);

    window.addEventListener('resize', this.debouncedResize, false);
    this.onResize();
  }

  stop = () => {
    const size = this.dimensions !== 'height' ? window.innerWidth : window.innerHeight;

    window.removeEventListener('resize', this.debouncedResize, false);

    return size;
  }

  onResize = () => {
    const size = this.dimensions !== 'height' ? window.innerWidth : window.innerHeight;

    if (this.callback) {
      this.callback(size);
    }

    return size;
  }
}


export default ResizeWindowListener;
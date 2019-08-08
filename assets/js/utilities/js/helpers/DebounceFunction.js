export default class DebounceFunction {
  constructor(time) {
    this.time = time;
    this.timeout = null;
  }

  update(func) {
    if (this.timeout) {
      clearTimeout(this.timeout);
    }

    this.timeout = window.setTimeout(
      () => {
        clearTimeout(this.timeout);
        func();
      },
      this.time,
    );
  }
}

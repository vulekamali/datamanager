export default class FixedNodeBox {
  constructor(boxNode) {
    // static values
    this.boxNode = boxNode;
    this.boxPosition = boxNode.offsetTop;

    // stateful values
    this.boxNodeFixed = {
      value: false,
      changed: false,
    };

    this.scrollTimeout = {
      value: null,
    };

    this.updateStateDebounce();
  }

  updatePresentation() {
    if (this.boxNodeFixed.changed === true) {

      if (this.boxNodeFixed.value === true) {
        this.boxNode.classList.add('is-fixed');
        this.boxNodeFixed.changed = false;
      } else {
        this.boxNode.classList.remove('is-fixed');
        this.boxNodeFixed.changed = false;
      }
    }
  }


  calcNewStateValuesIfNeeded() {
    const scrollPosition = document.body.scrollTop;

    const changeFixedValue = (active) => {
      this.boxNodeFixed = {
        ...this.boxNodeFixed,
        changed: true,
        value: active,
      };
    };

    if (this.boxNodeFixed.value === true && scrollPosition - this.boxPosition < -50) {
      changeFixedValue(false);
    } else if (this.boxNodeFixed.value === false && scrollPosition - this.boxPosition > -50) {
      changeFixedValue(true);
    }

    this.updatePresentation();
  }

  updateState() {
    this.calcNewStateValuesIfNeeded();
  }

  updateStateDebounce() {
    if (this.scrollTimeout.value) {
      clearTimeout(this.scrollTimeout.value);
    }

    const updateStateWrap = () => this.updateState();
    this.scrollTimeout.value = setTimeout(updateStateWrap, 5);
  }
}

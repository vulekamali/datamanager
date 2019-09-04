import { h, render, Component } from 'preact';
import { getState, subscribe } from './../../../reduxStore.js';
import Modals from './index.jsx';
import createComponents from './../../../utilities/js/helpers/createComponents.js';


class ModalsContainer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      title: null,
      markup: null,
    };

    this.events = {
      closeModal: this.closeModal.bind(this),
    };

    subscribe(() => {
      const storeState = getState();

      if (!storeState.modal) {
        return this.setState({
          ...this.state,
          title: null,
          markup: null,
        });
      }

      if (
        storeState.modal.title !== this.state.title &&
        storeState.modal.markup !== this.state.markdown
      ) {
        return this.setState({
          ...this.state,
          title: storeState.modal.title,
          markup: storeState.modal.markup,
        });
      }

      return null;
    });
  }

  closeModal() {
    this.setState({
      ...this.state,
      title: null,
      markup: null,
    });
  }

  render() {
    const { title, markup } = this.state;
    const { closeModal } = this.events;
    return <Modals {...{ title, markup, closeModal }} />;
  }
}


function scripts() {
  const createInstance = node => render(<ModalsContainer />, node);
  createComponents('Modals', createInstance);
}


export default scripts();

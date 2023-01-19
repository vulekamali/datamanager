import React from 'react';
import ReactDOM from 'react-dom';
import PseudoSelect from './../index.jsx';


function basicScript() {
  class PseudoSelectBasicExample extends React.Component {
    constructor(props) {
      super(props);

      this.state = {
        selected: '1',
        open: true,
      };

      this.changeAction = this.changeAction.bind(this);
      this.canvas = null;
    }

    changeAction(value) {
      if (this.state.open) {
        this.setState({ selected: value });
        return this.setState({ open: false });
      }

      return this.setState({ open: true });
    }

    render() {
      return (
        <PseudoSelect
          items={{ 'Test 1': '1', 'Test 2': '2', 'Test 3': '3' }}
          selected={this.state.selected}
          changeAction={this.changeAction}
          name="example"
          open={this.state.open}
        />
      );
    }
  }


  const node = document.getElementById('example-pseudoselect-basic-07-03');
  ReactDOM.render(
    <PseudoSelectBasicExample />,
    node,
  );
}


export default basicScript();

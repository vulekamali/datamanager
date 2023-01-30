import React from 'react';
import ReactDOM from 'react-dom';
import IntroSection from './index.jsx';


class IntroSectionContainer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      open: false,
      triggered: false,
    };

    this.parent = null;
    this.setOpen = this.setOpen.bind(this);
    this.parentAction = this.parentAction.bind(this);
  }

  setOpen() {
    this.setState({ open: !this.state.open });
  }

  parentAction(node) {
    if (node && this.parent !== node.clientHeight) {
      this.parent = node.clientHeight;
      this.calcIfTriggered(node.clientHeight);
    }
  }

  calcIfTriggered(value) {
    if (value > 330) {
      return this.setState({ triggered: true });
    }

    return this.setState({ triggered: false });
  }

  render() {
    return (
      <IntroSection
        triggered={this.state.triggered}
        innerHtml={this.props.innerHtml}
        setOpen={this.setOpen}
        open={this.state.open}
        parentAction={this.parentAction}
      />
    );
  }
}


function scripts() {
  const nodes = document.getElementsByClassName('js-initIntroSection');

  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    const innerHtml = node.getElementsByClassName('js-content')[0].innerHTML;

    ReactDOM.render(
      <IntroSectionContainer {...{ innerHtml }} />,
      node,
    );
  }

}


export default scripts();

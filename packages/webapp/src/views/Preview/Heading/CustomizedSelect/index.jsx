import React, { Component } from 'react';
import { MenuItem, CssBaseline } from '@material-ui/core';

import { CustomizedForm, SelectPreview } from './styled';

const callMenuItems = ({ id, name }) => (
  <MenuItem value={id} key={id}>
    {name}
  </MenuItem>
);

class CustomizedSelect extends Component {
  constructor(props) {
    super(props);

    this.state = {
      budgetValue: '',
    };

    this.handleChange = this.handleChange.bind(this);
  }

  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
  }

  render() {
    const { departmentNames, selected, eventHandler } = this.props;
    return (
      <CustomizedForm>
        <CssBaseline />
        <SelectPreview
          value={selected}
          onChange={eventHandler}
          displayEmpty
          name="budgetValue"
          classes={{ icon: 'icon', selectMenu: 'selectMenu' }}
        >
          {departmentNames.map(callMenuItems)}
        </SelectPreview>
      </CustomizedForm>
    );
  }
}

export default CustomizedSelect;

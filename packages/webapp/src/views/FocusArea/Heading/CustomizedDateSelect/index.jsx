import React, { Component } from 'react';

import { MenuItem, CssBaseline } from '@material-ui/core';

import {
  CustomizedForm,
  FormControlDateCtrl,
  SelectPreviewDate
} from './styled';

class CustomizedDateSelect extends Component{

  state = {
    DateValue: ''
  };

  handleChange = event => {
    this.setState({ [event.target.name]: event.target.value });
  };

  render() {
    return (
      <CustomizedForm>
        <SelectPreviewDate
          disabled
          value={this.state.DateValue}
          onChange={this.handleChange}
          displayEmpty
          name="DateValue"
          classes={{ 
            selectMenu: 'selectMenu',
            disabled: 'disabled',
            icon: 'icon'
          }}
        >
          <MenuItem value="">2019-20</MenuItem>
        </SelectPreviewDate>
      </CustomizedForm>
    );
  }
}

export default CustomizedDateSelect;

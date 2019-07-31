import { Component, createElement } from 'react';
import axios from 'axios';

import FocusAreaPreview from '../../views/FocusArea';
import transformData from './transformData';

class DataLoader extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: true,
      data: null,
    };
  }

  componentDidMount() {
    const { year } = this.props;
    const api = `/json/${year}/focus.json`;

    const loadliveData = ({ data }) =>
      this.setState({ data: transformData(data), loading: false });

    return axios.get(api)
      .then(({ data }) => data)
      .then(loadliveData);
  }

  render() {
    const { state, props } = this;
    const { loading, data } = state;
    const { year } = props;

    if (loading || !data) {
      return createElement('div', {}, 'Loading...');
    }

    const passedProps = {
      items: data,
      department: this.props.department,
      year,
      updateUrl: true
    }
    
    return createElement(FocusAreaPreview, passedProps);
  }
}

export default DataLoader;

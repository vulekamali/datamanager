import { Component, createElement } from 'react';
import axios from 'axios';

import NationalTreemap from '../../views/NationalTreemap';
import transformData from './transformData';
import { api } from './config.json';

class DataLoader extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: true,
      data: null,
    };
  }

  componentDidMount() {
    const loadliveData = ({ data }) => this.setState({ data: transformData(data), loading: false });

    return axios
      .get(api)
      .then(({ data }) => data)
      .then(loadliveData);
  }

  render() {
    const { state } = this;
    const { loading, data } = state;

    if (loading || !data) {
      return createElement('div', {}, 'Loading...');
    }

    const { items, total } = data;

    const initialSelected = {
      name: 'National Budget Summary',
      value: total,
      url: null,
      color: '#D8D8D8',
    };

    const passedProps = { items, initialSelected };

    return createElement(NationalTreemap, passedProps);
  }
}

export default DataLoader;

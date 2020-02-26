import { Component, createElement } from 'react';
import axios from 'axios';

import ProvincialTreemap from '../../views/ProvincialTreemap';
import transformData from './transformData';

class DataLoader extends Component {
  constructor(props) {
    super(props);
    const { financialYearSlug } = props;

    this.state = {
      loading: true,
      data: null,
      financialYearSlug: financialYearSlug,
      financialYearInt: parseInt(financialYearSlug.substring(0, 4)),
    };
  }

  componentDidMount() {
    const loadliveData = ({ data }) => this.setState({ data: transformData(data), loading: false });
    const endpoint = `/json/${this.state.financialYearSlug}/provincial/original.json`;

    return axios
      .get(endpoint)
      .then(({ data }) => data)
      .then(loadliveData);
  }

  render() {
    const { state } = this;
    const { loading, data, financialYearSlug, financialYearInt } = state;

    if (loading || !data) {
      return createElement('div', {}, 'Loading...');
    }

    const { items, total } = data;
    const initialSelected = {
      name: 'Provincial Budget Summary',
      value: total,
      url: null,
      color: '#D8D8D8',
    };

    const passedProps = { items, initialSelected, financialYearSlug, financialYearInt };

    return createElement(ProvincialTreemap, passedProps);
  }
}

export default DataLoader;

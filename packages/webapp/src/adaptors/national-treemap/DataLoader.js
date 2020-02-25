import { Component, createElement } from 'react';
import axios from 'axios';

import NationalTreemap from '../../views/NationalTreemap';
import transformData from './transformData';

class DataLoader extends Component {
  constructor(props) {
    super(props);
    const { financialYearSlug } = props;

    this.state = {
      loading: true,
      data: null,
      financialYearSlug: financialYearSlug,
      financialYearInt: parseInt(financialYearSlug.substring(4)),
    };
  }

  componentDidMount() {
    const endpoint = `/json/${this.state.financialYearSlug}/national/original.json`;
    const loadliveData = ({ data }) => this.setState({ data: transformData(data), loading: false });

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
      name: 'National Budget Summary',
      value: total,
      url: null,
      color: '#D8D8D8',
    };

    const passedProps = { items, initialSelected, financialYearSlug, financialYearInt };

    return createElement(NationalTreemap, passedProps);
  }
}

export default DataLoader;

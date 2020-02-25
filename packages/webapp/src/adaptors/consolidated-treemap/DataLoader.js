import { Component, createElement } from 'react';
import axios from 'axios';

import ConsolidatedTreemap from '../../views/ConsolidatedTreemap';

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
    const loadliveData = ({ data }) => this.setState({ data, loading: false });
    const endpoint = `/json/${this.state.financialYearSlug}/consolidated.json`;

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
      name: 'Consolidated Budget Summary',
      value: total,
      url: null,
      color: '#D8D8D8',
    };

    const passedProps = { items, initialSelected, financialYearSlug, financialYearInt };

    return createElement(ConsolidatedTreemap, passedProps);
  }
}

export default DataLoader;

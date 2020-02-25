import { Component, createElement } from 'react';
import axios from 'axios';

import FocusAreaPreview from '../../views/FocusArea';
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
    const endpoint = `/json/${this.state.financialYearSlug}/focus.json`;
    console.log(endpoint);
    const loadliveData = ({ data }) =>
      this.setState({ data: transformData(data), loading: false });

    return axios.get(endpoint)
      .then(({ data }) => data)
      .then(loadliveData);
  }

  render() {
    const { state, props } = this;
    const { loading, data, financialYearSlug, financialYearInt } = state;

    if (loading || !data) {
      return createElement('div', {}, 'Loading...');
    }

    const passedProps = {
      items: data,
      department: this.props.department,
      updateUrl: true,
      financialYearSlug: financialYearSlug,
      financialYearInt: financialYearInt,
    };

    return createElement(FocusAreaPreview, passedProps);
  }
}

export default DataLoader;

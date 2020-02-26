import { Component, createElement } from 'react';
import axios from 'axios';

import Preview from '../../views/Preview';
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
    const { financialYearSlug, sphere, government, department } = this.props;
    const endpoint = `/json/${ financialYearSlug }/previews/${ sphere }/${ government }/original.json`;

    const loadliveData = ({ data }) =>
      this.setState({ data: transformData(data, department), loading: false });

    return axios
      .get(endpoint)
      .then(({ data }) => data)
      .then(loadliveData);
  }

  render() {
    const { state, props } = this;
    const { loading, data, financialYearSlug, financialYearInt } = state;
    const { sphere, department, government } = props;

    if (loading || !data) {
      return createElement('div', {}, 'Loading...');
    }

    const passedProps = {
      items: data,
      sphere,
      department,
      government,
      financialYearSlug,
      financialYearInt,
    };
    return createElement(Preview, passedProps);
  }
}

export default DataLoader;

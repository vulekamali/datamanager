import { Component, createElement } from 'react';
import axios from 'axios';

import Preview from '../../views/Preview';
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
    const { year, sphere, government, department } = this.props;
    const api = `/json/${year}/previews/${sphere}/${government}/original.json`;

    const loadliveData = ({ data }) =>
      this.setState({ data: transformData(data, department), loading: false });

    return axios
      .get(api)
      .then(({ data }) => data)
      .then(loadliveData);
  }

  render() {
    const { state, props } = this;
    const { loading, data } = state;
    const { sphere, department, government, year } = props;

    if (loading || !data) {
      return createElement('div', {}, 'Loading...');
    }

    const passedProps = {
      items: data,
      sphere,
      department,
      government,
      year,
    };
    return createElement(Preview, passedProps);
  }
}

export default DataLoader;

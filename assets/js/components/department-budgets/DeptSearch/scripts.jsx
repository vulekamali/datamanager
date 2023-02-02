import React from 'react';
import ReactDOM from 'react-dom';
import decodeHtmlEntities from './../../../utilities/js/helpers/decodeHtmlEntities.js';
import updateQs from './../../../utilities/js/helpers/updateQs.js';
import { DeptSearch, makeGroups } from './index.jsx';
import filterResults from './partials/filterResults.js';
import fetchWrapper from './../../../utilities/js/helpers/fetchWrapper.js';
import { resourcesUrl, resultsToResources, initialResourceGroups } from './../../GovernmentResources/governmentResourcesData.js';

class DeptSearchContainer extends React.Component {
  constructor(props) {
    super(props);
    const filters = {
      keywords: this.props.phrase || '',
      sphere: this.props.sphere || 'all',
      province: this.props.province || 'all',
    };

    this.state = {
      loading: false,
      open: null,
      results: filterResults(filters, this.props.governments),
      filters,
      resourceGroups: initialResourceGroups(),
    };

    this.eventHandlers = {
      updateDropdown: this.updateDropdown.bind(this),
      updateKeywords: this.updateKeywords.bind(this),
    };

    this.requestResources();
  }

  componentWillUpdate(nextProps, nextState) {
    updateQs({
      ...window.vulekamali.qs,
      phrase: nextState.filters.keywords,
      sphere: nextState.filters.sphere,
      province: nextState.filters.province,
    });
  }

  updateKeywords(keywords) {
    const filters = {
      ...this.state.filters,
      keywords,
    };

    this.setState({ filters });
    this.setState({ results: filterResults(filters, this.props.governments) });
  }

  updateDropdown(filter, value) {
    if (this.state.open === filter) {
      this.setState({ open: null });
    } else {
      return this.setState({ open: filter });
    }

    const filters = {
      ...this.state.filters,
      province: 'all',
      [filter]: value,
    };

    this.setState({ filters });
    return this.setState({ results: filterResults(filters, this.props.governments) });
  }

  requestResources() {
    const url = resourcesUrl(this.props.ckanUrl, this.props.financialYear);
    fetchWrapper(url)
      .then((response) => {
        this.setState({resourceGroups: resultsToResources(response.result.results)});
      })
      .catch((errorResult) => console.warn(errorResult));
  }

  render() {
    return <DeptSearch state={this.state} eventHandlers={this.eventHandlers} />;
  }
}


function scripts() {
  const componentsList = document.getElementsByClassName('js-initDeptSearch');
  const ckanUrl = document.getElementsByTagName('body')[0].getAttribute('data-ckan-url');;

  for (let i = 0; i < componentsList.length; i++) {
    const component = componentsList[i];
    const nationalData = JSON.parse(decodeHtmlEntities(component.getAttribute('data-national-json'))).data;
    const rawProvincialData = JSON.parse(decodeHtmlEntities(component.getAttribute('data-provincial-json'))).data;
    const financialYear = decodeHtmlEntities(component.getAttribute('data-year'));

    const provincialData = rawProvincialData.sort((a, b) => {
      return a.name.localeCompare(b.name);
    });
    provincialData.forEach(p => {
      p.label = p.name
    });

    const governments = [
      {
        ...nationalData,
        label: 'National',
      },
      ...provincialData,
    ];

    const { sphere, province, phrase } = window.vulekamali.qs;

    ReactDOM.render(
      <DeptSearchContainer {...{ governments, ckanUrl, financialYear, sphere, province, phrase }} />,
      component,
    );
  }
}


export default scripts();

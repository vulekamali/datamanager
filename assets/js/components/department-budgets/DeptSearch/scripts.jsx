import { h, Component, render } from 'preact';
import decodeHtmlEntities from './../../../utilities/js/helpers/decodeHtmlEntities.js';
import updateQs from './../../../utilities/js/helpers/updateQs.js';
import DeptSearch from './index.jsx';
import filterResults from './partials/filterResults.js';


class DeptSearchContainer extends Component {
  constructor(props) {
    super(props);
    const filters = {
      keywords: this.props.phrase || '',
      sphere: this.props.sphere || 'all',
      province: this.props.province || 'all',
    };

    const getEmptyGroups = (data) => {
      return data.reduce(
        (results, val) => {
          if (val.departments.length <= 0) {

            return [
              ...results,
              val.slug,
            ];
          }

          return results;
        },
        [],
      );
    };

    this.state = {
      loading: false,
      open: null,
      results: filterResults(filters, this.props.spheres),
      emptyGroups: getEmptyGroups(this.props.spheres),
      filters,
    };

    this.eventHandlers = {
      updateDropdown: this.updateDropdown.bind(this),
      updateKeywords: this.updateKeywords.bind(this),
    };
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
    this.setState({ results: filterResults(filters, this.props.spheres) });
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
    return this.setState({ results: filterResults(filters, this.props.spheres) });
  }

  render() {
    return <DeptSearch state={this.state} eventHandlers={this.eventHandlers} epresData={this.props.epresData} />;
  }
}


function scripts() {
  const componentsList = document.getElementsByClassName('js-initDeptSearch');

  for (let i = 0; i < componentsList.length; i++) {
    const component = componentsList[i];
    const nationalData = JSON.parse(decodeHtmlEntities(component.getAttribute('data-national-json'))).data;
    const rawProvincialData = JSON.parse(decodeHtmlEntities(component.getAttribute('data-provincial-json'))).data;
    const financialYear = decodeHtmlEntities(component.getAttribute('data-year'));

    const provincialData = rawProvincialData.sort((a, b) => {
      return a.name.localeCompare(b.name);
    });
    const labeledProvincialData = provincialData.map(p => {
      p.label = p.name;
    });

    const spheres = [
      {
        ...nationalData,
        label: 'National',
      },
      ...provincialData,
    ];

    const { sphere, province, phrase } = window.vulekamali.qs;

    render(
      <DeptSearchContainer {...{ spheres, financialYear, sphere, province, phrase }} />,
      component,
    );
  }
}


export default scripts();
